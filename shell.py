import errors

DIGITS = "0123456789"


"""TOKENS"""

TT_INT = "TT_INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_DIVIDE = "DIVIDE"
TT_MUL = "MUL"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_MODULO = "MODULO"
TT_EOF = "EOF"

"""POSITION"""


class Position:
    """Keeps track of the position of the lexer."""

    def __init__(self, idx, ln, col, fn, ftxt) -> None:
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


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
                return [], errors.IllegalCharacterError(
                    pos_start, self.pos, f"' {char} '"
                )
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


def run(filename, text):
    # Generate tokens
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error:
        return tokens, error
