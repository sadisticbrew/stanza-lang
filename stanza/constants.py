import string
from enum import Enum, auto

DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

"""TOKENS"""


class TT(Enum):
    INT = auto()
    FLOAT = auto()
    PLUS = auto()
    MINUS = auto()
    DIVIDE = auto()
    MUL = auto()
    LPAREN = auto()
    RPAREN = auto()
    MODULO = auto()
    EXPO = auto()
    EOF = auto()
    EQ = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    EE = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    COMMA = auto()
    ARROW = auto()
    STRING = auto()


SIMPLE_TOKENS = {
    "+": TT.PLUS,
    "-": TT.MINUS,
    "/": TT.DIVIDE,
    "*": TT.MUL,
    "(": TT.LPAREN,
    ")": TT.RPAREN,
    "%": TT.MODULO,
    "^": TT.EXPO,
    "=": TT.EQ,
    ",": TT.COMMA,
    "<": TT.LT,
    ">": TT.GT,
}

COMPLEX_TOKENS = {
    "->": TT.ARROW,
    "==": TT.EE,
    "!=": TT.NE,
    "<=": TT.LTE,
    ">=": TT.GTE,
}

KEYWORDS = [
    "let",
    "not",
    "and",
    "or",
    "if",
    "then",
    "else",
    "elif",
    "for",
    "step",
    "do",
    "to",
    "while",
    "in",
    "fn",
]

ESC_CHARS = {"n": "\n", "t": "\t", '"': '"'}

BOOLEANS = ["fact", "cap"]
