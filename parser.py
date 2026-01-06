import errors
from constants import (
    TT_DIVIDE,
    TT_EOF,
    TT_EQ,
    TT_EXPO,
    TT_FLOAT,
    TT_IDENTIFIER,
    TT_INT,
    TT_KEYWORD,
    TT_LPAREN,
    TT_MINUS,
    TT_MUL,
    TT_PLUS,
    TT_RPAREN,
)
from lexer import Token
from nodes import (
    BinOpNode,
    NumberNode,
    PowerOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignmentNode,
)

"""ParseResult"""


class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None

    def register(self, result):
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


"""PARSER"""


class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_index = -1
        self._advance()

    def _advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token: Token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        result = self.expression()
        if not result.error and self.current_token.type != TT_EOF:
            return result.failure(
                errors.InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected '+', '-' , '*', or '/'",
                )
            )
        return result

    def factor(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            result.register(self._advance())
            factor = result.register(self.factor())
            if result.error:
                return result
            return result.success(UnaryOpNode(token, factor))

        elif token.type in (TT_INT, TT_FLOAT):
            result.register(self._advance())
            return result.success(NumberNode(token))

        elif token.type == TT_IDENTIFIER:
            result.register(self._advance())
            return result.success(VarAccessNode(token))

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
                    errors.InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected ')'",
                    )
                )
        return result.failure(
            errors.InvalidSyntaxError(
                token.pos_start, token.pos_end, "Expected int or float."
            )
        )

    def specialist(self):
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
        return self.bin_op(self.specialist, (TT_MUL, TT_DIVIDE))

    def expression(self):
        res = ParseResult()
        if self.current_token.matches(TT_KEYWORD, "let"):
            res.register(self._advance())
            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(
                    errors.InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected identifier",
                    )
                )
            var_name = self.current_token.value
            res.register(self._advance())
            if self.current_token.type != TT_EQ:
                return res.failure(
                    errors.InvalidSyntaxError(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected '='",
                    )
                )
            res.register(self._advance())
            value = res.register(self.expression())
            if res.error:
                return res
            return res.success(VarAssignmentNode(var_name, value))
        node = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))
        if res.error:
            return res.failure(
                errors.InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected 'let', int, float, identifier, '+', '-' , '*', or '/'.",
                )
            )
        return res.success(node)

    def bin_op(self, func, ops):
        result = ParseResult()
        left = result.register(func())
        if result.error:
            return result

        while self.current_token.type in ops:
            op_token = self.current_token
            result.register(self._advance())
            right = result.register(func())
            left = BinOpNode(left, op_token, right)

        return result.success(left)
