from lexer import Token

"""NODES"""


class NumberNode:
    def __init__(self, token: Token) -> None:
        self.token = token

    def __repr__(self) -> str:
        return f"{self.token}"


class BinOpNode:
    def __init__(self, left_node, op_token, right_node) -> None:
        self.op = op_token
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self) -> str:
        return f"({self.left_node}, {self.op}, {self.right_node})"


class UnaryOpNode:
    def __init__(self, op_token, node) -> None:
        self.op = op_token
        self.node = node

    def __repr__(self) -> str:
        return f"({self.op},{self.node})"


class PowerOpNode:
    def __init__(self, base, exponent) -> None:
        self.base = base
        self.exponent = exponent

    def __repr__(self) -> str:
        return f"({self.base}, EXP, {self.exponent})"
