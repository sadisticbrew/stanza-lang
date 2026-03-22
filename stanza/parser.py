from .constants import TT
from .errors import InvalidSyntaxError
from .lexer import Token
from .nodes import (
    BinOpNode,
    CallNode,
    ForNode,
    FuncDefNode,
    IfNode,
    NumberNode,
    PowerOpNode,
    StringNode,
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
        if not self.current_token.matches(TT.KEYWORD, keyword):
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
        if not result.error and self.current_token.type != TT.EOF:
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
        if token.type in (TT.PLUS, TT.MINUS):
            result.register(self._advance())
            factor = result.register(self.factor())
            if result.error:
                return result
            return result.success(UnaryOpNode(token, factor))

        # Handle numbers
        elif token.type in (TT.INT, TT.FLOAT):
            result.register(self._advance())
            return result.success(NumberNode(token))

        # Handle variables
        elif token.type == TT.IDENTIFIER:
            result.register(self._advance())
            return result.success(VarAccessNode(token))

        elif token.type == TT.STRING:
            result.register(self._advance())
            return result.success(StringNode(token))

        # Handle parentheses
        elif token.type == TT.LPAREN:
            result.register(self._advance())
            expression = result.register(self.expression())
            if result.error:
                return result
            if self.current_token.type == TT.RPAREN:
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

        elif token.matches(TT.KEYWORD, "if"):
            if_expr = result.register(self.if_expr())
            if result.error:
                return result
            return result.success(if_expr)

        elif token.matches(TT.KEYWORD, "for"):
            for_expr = result.register(self.for_expr())
            if result.error:
                return result
            return result.success(for_expr)

        elif token.matches(TT.KEYWORD, "while"):
            while_expr = result.register(self.while_expr())
            if result.error:
                return result
            return result.success(while_expr)

        elif token.matches(TT.KEYWORD, "fn"):
            func_def = result.register(self.func_def())
            if result.error:
                return result
            return result.success(func_def)

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "Expected int or float.")
        )

    def call(self):
        """
        Handles the function calls
        """
        res = ParseResult()

        base_node = res.register(self.factor())
        if res.error:
            return res
        while self.current_token.type == TT.LPAREN:
            arg_nodes = []
            res.register(self._advance())
            if self.current_token.type == TT.RPAREN:
                res.register(self._advance())
            else:
                arg_nodes.append(res.register(self.expression()))
                if res.error:
                    return res

                while self.current_token.type == TT.COMMA:
                    res.register(self._advance())
                    arg_nodes.append(res.register(self.expression()))
                    if res.error:
                        return res
                if self.current_token.type != TT.RPAREN:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "Expected  an ',' or ')'.",
                        )
                    )
                res.register(self._advance())
            base_node = CallNode(base_node, arg_nodes)
        return res.success(base_node)

    def specialist(self):
        """
        Handles the power operator
        """

        result = ParseResult()
        factor = result.register(self.call())
        if result.error:
            return result
        if self.current_token.type == TT.EXPO:
            result.register(self._advance())
            right = result.register(self.specialist())
            if result.error:
                return result
            return result.success(PowerOpNode(factor, right))
        return result.success(factor)

    def term(self):
        """Handles the multiplication, division and modulo"""
        return self._binary_operation(self.specialist, (TT.MUL, TT.DIVIDE, TT.MODULO))

    def arithmetic_expr(self):
        """Handles the addition and subtraction"""
        return self._binary_operation(self.term, (TT.PLUS, TT.MINUS, TT.MUL, TT.DIVIDE))

    def comp_expr(self):
        """Handles comparisions (<, >, ==, !=) and the logical NOT"""
        res = ParseResult()

        if self.current_token.matches(TT.KEYWORD, "not"):
            op_tok = self.current_token
            res.register(self._advance())
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        start_index = self.token_index
        node = res.register(
            self._binary_operation(
                self.arithmetic_expr, (TT.EE, TT.NE, TT.GT, TT.GTE, TT.LTE, TT.LT)
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

        res.register(self._expect_keyword("if"))
        if res.error:
            return res

        condition = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("then"))
        if res.error:
            return res

        expr = res.register(self.expression())
        if res.error:
            return res

        cases.append((condition, expr))

        while self.current_token.matches(TT.KEYWORD, "elif"):
            res.register(self._advance())

            condition = res.register(self.expression())
            if res.error:
                return res

            res.register(self._expect_keyword("then"))
            if res.error:
                return res

            expr = res.register(self.expression())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_token.matches(TT.KEYWORD, "else"):
            res.register(self._advance())

            expr = res.register(self.expression())
            if res.error:
                return res

            else_case = expr

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        res.register(self._expect_keyword("for"))
        if res.error:
            return res

        if self.current_token.type != TT.IDENTIFIER:
            return res.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected identifier",
                )
            )
        var_name_tok = self.current_token
        res.register(self._advance())

        res.register(self._expect_keyword("in"))
        if res.error:
            return res

        start_value_node = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("to"))
        if res.error:
            return res

        end_value_node = res.register(self.expression())
        if res.error:
            return res

        if self.current_token.matches(TT.KEYWORD, "step"):
            res.register(self._advance())
            step = res.register(self.expression())
            if res.error:
                return res
        else:
            step = None

        res.register(self._expect_keyword("do"))
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

        res.register(self._expect_keyword("while"))
        if res.error:
            return res

        condition = res.register(self.expression())
        if res.error:
            return res

        res.register(self._expect_keyword("do"))
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
        if self.current_token.matches(TT.KEYWORD, "let"):
            res.register(self._advance())
            if self.current_token.type != TT.IDENTIFIER:
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
            if self.current_token.type != TT.EQ:
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
        elif self.current_token.type == TT.IDENTIFIER:
            next_tok = self._peek()
            if next_tok and next_tok.type == TT.EQ:
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
        node = res.register(self._binary_operation(self.comp_expr, (TT.PLUS, TT.MINUS)))
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

    def func_def(self):
        res = ParseResult()

        res.register(self._expect_keyword("fn"))
        if res.error:
            return res

        if self.current_token.type == TT.IDENTIFIER:
            func_name_tok = self.current_token
            res.register(self._advance())
            if self.current_token.type != TT.LPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected  '('.",
                    )
                )
        else:
            func_name_tok = None
            if self.current_token.type != TT.LPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected  '('.",
                    )
                )

        res.register(self._advance())
        arg_name_toks = []
        if self.current_token.type == TT.IDENTIFIER:
            arg_name_toks.append(self.current_token)
            res.register(self._advance())

            while self.current_token.type == TT.COMMA:
                res.register(self._advance())

                if self.current_token.type != TT.IDENTIFIER:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "Expected  ')'.",
                        )
                    )

                arg_name_toks.append(self.current_token)
                res.register(self._advance())

            if self.current_token.type != TT.RPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected  ')'.",
                    )
                )
        else:
            if self.current_token.type != TT.RPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected  an identifier or ')'.",
                    )
                )

        res.register(self._advance())

        if self.current_token.type != TT.ARROW:
            return res.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected  '->'.",
                )
            )

        res.register(self._advance())

        node_to_return = res.register(self.expression())
        if res.error:
            return res

        return res.success(FuncDefNode(func_name_tok, arg_name_toks, node_to_return))

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
