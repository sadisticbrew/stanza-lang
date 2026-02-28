from .constants import (
    TT_DIVIDE,
    TT_EE,
    TT_EOF,
    TT_EQ,
    TT_EXPO,
    TT_FLOAT,
    TT_GT,
    TT_GTE,
    TT_IDENTIFIER,
    TT_INT,
    TT_KEYWORD,
    TT_LPAREN,
    TT_LT,
    TT_LTE,
    TT_MINUS,
    TT_MODULO,
    TT_MUL,
    TT_NE,
    TT_PLUS,
    TT_RPAREN,
)
from .errors import InvalidSyntaxError
from .lexer import Token
from .nodes import (
    BinOpNode,
    ForNode,
    IfNode,
    NumberNode,
    PowerOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignmentNode,
    VarReassignmentNode,
    WhileNode,
)

"""----------ParseResult----------"""


class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None

    def register(self, result):
        """
        Unwraps a child ParseResult.
        If the child has an error, it bubbles up.
        If the child has a node, it returns it.
        """
        if isinstance(result, ParseResult):
            if result.error:
                self.error = result.error
            return result.node
        return result

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


"""----------PARSER----------"""


class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_index = -1
        self._advance()

    def _peek(self) -> Token | None:
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        return None

    def _advance(self) -> Token:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token: Token = self.tokens[self.token_index]
        return self.current_token

    def _expect_keyword(self, keyword):
        res = ParseResult()
        if not self.current_token.matches(TT_KEYWORD, keyword):
            return res.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    f"Expected '{keyword}'.",
                )
            )
        res.register(self._advance())
        return res.success(None)

    def parse(self):
        result = self.expression()
        if not result.error and self.current_token.type != TT_EOF:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected '+', '-' , '*', or '/'",
                )
            )
        return result

    def factor(self):
        """
        Handles numbers, variables, parentheses, and unary operators (+/-).
        """
        result = ParseResult()
        token = self.current_token

        # Handle unary operators
        if token.type in (TT_PLUS, TT_MINUS):
            result.register(self._advance())
            factor = result.register(self.factor())
            if result.error:
                return result
            return result.success(UnaryOpNode(token, factor))

        # Handle numbers
        elif token.type in (TT_INT, TT_FLOAT):
            result.register(self._advance())
            return result.success(NumberNode(token))

        # Handle variables
        elif token.type == TT_IDENTIFIER:
            result.register(self._advance())
            return result.success(VarAccessNode(token))

        # Handle parentheses
        elif token.type == TT_LPAREN:
            result.register(self._advance())
            expression = result.register(self.expression())
            if result.error:
                return result
            if self.current_token.type == TT_RPAREN:
                result.register(self._advance())
                return result.success(expression)
            else:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected ')'",
                    )
                )

        elif token.matches(TT_KEYWORD, "IF"):
            if_expr = result.register(self.if_expr())
            if result.error:
                return result
            return result.success(if_expr)

        elif token.matches(TT_KEYWORD, "FOR"):
            for_expr = result.register(self.for_expr())
            if result.error:
                return result
            return result.success(for_expr)

        elif token.matches(TT_KEYWORD, "WHILE"):
            while_expr = result.register(self.while_expr())
            if result.error:
                return result
            return result.success(while_expr)

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "Expected int or float.")
        )

    def specialist(self):
        """
        Handles the power operator
        """

        result = ParseResult()
        factor = result.register(self.factor())
        if result.error:
            return result
        if self.current_token.type == TT_EXPO:
            result.register(self._advance())
            right = result.register(self.specialist())
            if result.error:
                return result
            return result.success(PowerOpNode(factor, right))
        return result.success(factor)

    def term(self):
        """Handles the multiplication, division and modulo"""
        return self._binary_operation(self.specialist, (TT_MUL, TT_DIVIDE, TT_MODULO))

    def arithmetic_expr(self):
        """Handles the addition and subtraction"""
        return self._binary_operation(self.term, (TT_PLUS, TT_MINUS, TT_MUL, TT_DIVIDE))

    def comp_expr(self):
        """Handles comparisions (<, >, ==, !=) and the logical NOT"""
        res = ParseResult()

        if self.current_token.matches(TT_KEYWORD, "NOT"):
            op_tok = self.current_token
            res.register(self._advance())
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        start_index = self.token_index
        node = res.register(
            self._binary_operation(
                self.arithmetic_expr, (TT_EE, TT_NE, TT_GT, TT_GTE, TT_LTE, TT_LT)
            )
        )
        if res.error:
            # If we haven't moved forward, show the general error
            if self.token_index == start_index:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected 'let', int, float, identifier, '+', '-' , '*', 'NOT' or '/'. (inside comp_expr)",
                    )
                )
            # If we DID move forward, keep the specific error
            return res
        return res.success(node)

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        res.register(self._expect_keyword("IF"))
        if res.error:
            return res

        condition = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("THEN"))
        if res.error:
            return res

        expr = res.register(self.expression())
        if res.error:
            return res

        cases.append((condition, expr))

        while self.current_token.matches(TT_KEYWORD, "ELIF"):
            res.register(self._advance())

            condition = res.register(self.expression())
            if res.error:
                return res

            res.register(self._expect_keyword("THEN"))
            if res.error:
                return res

            expr = res.register(self.expression())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_token.matches(TT_KEYWORD, "ELSE"):
            res.register(self._advance())

            expr = res.register(self.expression())
            if res.error:
                return res

            else_case = expr

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        res.register(self._expect_keyword("FOR"))
        if res.error:
            return res

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected identifier",
                )
            )
        var_name_tok = self.current_token
        res.register(self._advance())

        res.register(self._expect_keyword("IN"))
        if res.error:
            return res

        start_value_node = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("TO"))
        if res.error:
            return res

        end_value_node = res.register(self.expression())
        if res.error:
            return res

        if self.current_token.matches(TT_KEYWORD, "STEP"):
            res.register(self._advance())
            step = res.register(self.expression())
            if res.error:
                return res
        else:
            step = None

        res.register(self._expect_keyword("DO"))
        if res.error:
            return res

        body = res.register(self.expression())
        if res.error:
            return res

        return res.success(
            ForNode(var_name_tok, start_value_node, end_value_node, body, step)
        )

    def while_expr(self):
        res = ParseResult()

        res.register(self._expect_keyword("WHILE"))
        if res.error:
            return res

        condition = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("DO"))
        if res.error:
            return res

        body = res.register(self.expression())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def expression(self):
        """
        This is the top level boss function.
        Currently it handles 'let' assignments, reassignments and binary operations
        """

        res = ParseResult()

        # case 0: it is a variable declaration
        if self.current_token.matches(TT_KEYWORD, "let"):
            res.register(self._advance())
            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected identifier",
                    )
                )
            var_name = self.current_token.value
            var_pos = self.current_token.pos_start.copy()
            res.register(self._advance())
            if self.current_token.type != TT_EQ:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected '='",
                    )
                )
            res.register(self._advance())
            value = res.register(self.expression())
            if res.error:
                return res
            return res.success(
                VarAssignmentNode(var_name, value, var_pos, value.pos_end)
            )

        # case 1: it is a variable reassignment
        elif self.current_token.type == TT_IDENTIFIER:
            next_tok = self._peek()
            if next_tok and next_tok.type == TT_EQ:
                var_name = self.current_token.value
                var_pos = self.current_token.pos_start.copy()

                res.register(self._advance())  # Consume variable name
                res.register(self._advance())  # Consume '='

                value = res.register(self.expression())

                if res.error:
                    return res
                return res.success(
                    VarReassignmentNode(var_name, value, var_pos, value.pos_end)
                )

        # case 2: std binary operations like add, sub, mul, etc.

        start_index = self.token_index
        node = res.register(self._binary_operation(self.comp_expr, (TT_PLUS, TT_MINUS)))
        if res.error:
            # If we haven't moved forward, show the general error
            if self.token_index == start_index:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected 'let', int, float, identifier, '+', '-' , '*', 'NOT' or '/'. (inside expr)",
                    )
                )
            # If we DID move forward, keep the specific error
            return res
        return res.success(node)

    def _binary_operation(self, func, ops):
        """
        Generic helper function that handles binary operations and reduces code duplication
        """
        result = ParseResult()
        left = result.register(func())
        if result.error:
            return result

        while (
            self.current_token.type in ops
            or (self.current_token.type, self.current_token.value) in ops
        ):
            op_token = self.current_token
            result.register(self._advance())
            right = result.register(func())
            if result.error:
                return result
            left = BinOpNode(left, op_token, right)

        return result.success(left)
