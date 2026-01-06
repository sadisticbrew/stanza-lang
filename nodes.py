from lexer import Token

"""NODES"""


class NumberNode:
    def __init__(self, token: Token) -> None:
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self) -> str:
        return f"{self.token}"


class BinOpNode:
    def __init__(self, left_node, op_token, right_node) -> None:
        self.op = op_token
        self.left_node = left_node
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self) -> str:
        return f"({self.left_node}, {self.op}, {self.right_node})"


class UnaryOpNode:
    def __init__(self, op_token, node) -> None:
        self.op = op_token
        self.node = node
        self.pos_start = self.op.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self) -> str:
        return f"({self.op},{self.node})"


class PowerOpNode:
    def __init__(self, base, exponent) -> None:
        self.base = base
        self.exponent = exponent
        self.pos_start = self.base.pos_start
        self.pos_end = self.exponent.pos_end

    def __repr__(self) -> str:
        return f"({self.base}, EXP, {self.exponent})"


class VarAssignmentNode:
    def __init__(self, var_name, value) -> None:
        self.var_name = var_name
        self.value = value

    def __repr__(self) -> str:
        return f"({self.var_name}, EQ, {self.value})"


class VarAccessNode:
    def __init__(self, var_access_tok: Token) -> None:
        self.var_access_tok = var_access_tok
        self.pos_start = self.var_access_tok.pos_start
        self.pos_end = self.var_access_tok.pos_end

    def __repr__(self) -> str:
        return f"({self.var_access_tok})"
