from constants import (
    DIGITS,
    TT_DIVIDE,
    TT_EOF,
    TT_EXPO,
    TT_FLOAT,
    TT_INT,
    TT_LPAREN,
    TT_MINUS,
    TT_MODULO,
    TT_MUL,
    TT_PLUS,
    TT_RPAREN,
)
from errors import IllegalCharacterError, Position


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
            if self.current_char in " \t":
                self._advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos.copy()))
                self._advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == "/":
                tokens.append(Token(TT_DIVIDE, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == "%":
                tokens.append(Token(TT_MODULO, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == "^":
                tokens.append(Token(TT_EXPO, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos.copy()))
                self._advance()

            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos.copy()))
                self._advance()

            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self._advance()
                return [], IllegalCharacterError(pos_start, self.pos, f"' {char} '")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
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
