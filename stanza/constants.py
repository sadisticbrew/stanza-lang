import string

DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

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
TT_EXPO = "EXPO"
TT_EOF = "EOF"
TT_EQ = "EQ"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EE = "EE"
TT_NE = "NE"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"

KEYWORDS = [
    "let",
    "NOT",
    "AND",
    "OR",
    "IF",
    "THEN",
    "ELSE",
    "ELIF",
    "FOR",
    "STEP",
    "DO",
    "TO",
    "WHILE",
    "IN",
]
BOOLEANS = ["fact", "cap"]
