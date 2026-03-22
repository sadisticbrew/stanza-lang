from .constants import (
    COMPLEX_TOKENS,
    DIGITS,
    ESC_CHARS,
    KEYWORDS,
    LETTERS,
    SIMPLE_TOKENS,
    TT,
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

    def _peek(self):
        peek_idx = self.pos.idx + 1
        return self.text[peek_idx] if peek_idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char:
            char = self.current_char

            if char in " \t":
                self._advance()
                continue

            if char in DIGITS:
                tokens.append(self._make_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._make_identifier())
                continue

            if char == '"':
                tokens.append(self._make_string())
                continue

            next_char = self._peek()
            if next_char:
                two_chars = self.current_char + next_char
                if two_chars in COMPLEX_TOKENS:
                    tokens.append(
                        Token(COMPLEX_TOKENS[two_chars], pos_start=self.pos.copy())
                    )
                    self._advance()
                    self._advance()
                    continue

            if char == "!" and next_char != "=":
                pos_start = self.pos.copy()
                self._advance()
                return [], ExpectedCharError(
                    pos_start, self.pos, "Expected '=' after '!'"
                )

            if char in SIMPLE_TOKENS:
                tokens.append(Token(SIMPLE_TOKENS[char], pos_start=self.pos.copy()))
                self._advance()
                continue

            pos_start = self.pos.copy()
            bad_char = char
            self._advance()
            return [], IllegalCharacterError(pos_start, self.pos, f"' {bad_char} '")
        tokens.append(Token(TT.EOF, pos_start=self.pos))
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
            return Token(TT.INT, int(num_str), pos_start=pos_start, pos_end=self.pos)
        else:
            return Token(
                TT.FLOAT, float(num_str), pos_start=pos_start, pos_end=self.pos
            )

    def _make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()
        while self.current_char and self.current_char in LETTERS + "_":
            id_str += self.current_char
            self._advance()
        token_type = TT.KEYWORD if id_str in KEYWORDS else TT.IDENTIFIER
        return Token(token_type, id_str, pos_start, pos_end=self.pos)

    def _make_string(self):
        string_str = ""
        pos_start = self.pos.copy()
        self._advance()
        escape_char = False

        while self.current_char is not None and (
            self.current_char != '"' or escape_char
        ):
            if escape_char:
                string_str += ESC_CHARS.get(self.current_char, self.current_char)
            else:
                if self.current_char == "\\":
                    escape_char = True
                else:
                    string_str += self.current_char
            self._advance()

        escape_char = False
        self._advance()

        return Token(TT.STRING, string_str, pos_start, pos_end=self.pos)
