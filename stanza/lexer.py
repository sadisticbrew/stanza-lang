from .constants import (
    DIGITS,
    KEYWORDS,
    LETTERS,
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
from .errors import ExpectedCharError, IllegalCharacterError, Position


class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None) -> None:
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end

    def matches(self, tok_type, keyword):
        return self.type == tok_type and self.value == keyword

    def __repr__(self) -> str:
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


"""LEXER"""


class Lexer:
    def __init__(self, filename, text) -> None:
        self.fn = filename
        self.text = text
        self.pos = Position(-1, 0, -1, self.fn, text)
        self.current_char = None
        self._advance()

    def _advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self):
        tokens = []

        while self.current_char:
            char = self.current_char

            # TODO: This long elif chain CAN be replaced with a shorter one by using dictionary to map character and their enum token_type in constants.py but I am too lazy to do that right now.
            if char in " \t":
                self._advance()

            elif char in DIGITS:
                tokens.append(self._make_number())

            elif char.isalpha() or char == "_":
                tokens.append(self._make_identifier())

            elif char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos.copy()))
                self._advance()
            elif char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos.copy()))
                self._advance()

            elif char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos.copy()))
                self._advance()

            elif char == "/":
                tokens.append(Token(TT_DIVIDE, pos_start=self.pos.copy()))
                self._advance()

            elif char == "%":
                tokens.append(Token(TT_MODULO, pos_start=self.pos.copy()))
                self._advance()

            elif char == "^":
                tokens.append(Token(TT_EXPO, pos_start=self.pos.copy()))
                self._advance()

            elif char == "!":
                token, error = self._make_not_equal()
                if error:
                    return [], error
                tokens.append(token)

            elif char == "<":
                tokens.append(self._make_less_than())
                self._advance()

            elif char == ">":
                tokens.append(self._make_greater_than())
                self._advance()

            elif char == "=":
                tokens.append(self._make_equals())
                self._advance()

            elif char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos.copy()))
                self._advance()

            elif char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos.copy()))
                self._advance()

            else:
                pos_start = self.pos.copy()
                bad_char = char
                self._advance()
                return [], IllegalCharacterError(pos_start, self.pos, f"' {bad_char} '")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    """----------helper funcs----------"""

    def _make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self._advance()
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start=pos_start, pos_end=self.pos)
        else:
            return Token(
                TT_FLOAT, float(num_str), pos_start=pos_start, pos_end=self.pos
            )

    def _make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()
        while self.current_char and self.current_char in LETTERS + "_":
            id_str += self.current_char
            self._advance()
        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, id_str, pos_start, pos_end=self.pos)

    def _make_not_equal(self):
        pos_start = self.pos.copy()
        self._advance()
        if self.current_char == "=":
            self._advance()
            return Token(TT_NE, pos_start=pos_start), None
        self._advance()
        return None, ExpectedCharError(pos_start, self.pos, "Expected '='")

    def _make_equals(self):
        pos_start = self.pos.copy()
        self._advance()
        if self.current_char == "=":
            self._advance()
            return Token(TT_EE, pos_start=pos_start)
        return Token(TT_EQ, pos_start=pos_start)

    def _make_less_than(self):
        pos_start = self.pos.copy()
        self._advance()

        if self.current_char == "=":
            return Token(TT_LTE, pos_start=pos_start)

        return Token(TT_LT, pos_start=pos_start)

    def _make_greater_than(self):
        pos_start = self.pos.copy()
        self._advance()

        if self.current_char == "=":
            return Token(TT_GTE, pos_start=pos_start)

        return Token(TT_GT, pos_start=pos_start)
