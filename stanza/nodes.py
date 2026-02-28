from .lexer import Token

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
    def __init__(self, var_name, value, pos_start, pos_end) -> None:
        self.var_name = var_name
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self) -> str:
        return f"({self.var_name}, EQ, {self.value})"


class VarReassignmentNode(VarAssignmentNode):
    def __init__(self, var_name, value, pos_start, pos_end) -> None:
        super().__init__(var_name, value, pos_start, pos_end)


class VarAccessNode:
    def __init__(self, var_access_tok: Token) -> None:
        self.var_access_tok = var_access_tok
        self.pos_start = self.var_access_tok.pos_start
        self.pos_end = self.var_access_tok.pos_end

    def __repr__(self) -> str:
        return f"({self.var_access_tok})"


class ComparisionNode:
    def __init__(self, left, comp_tok, right) -> None:
        self.left_node = left
        self.comp_tok = comp_tok
        self.right_node = right


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_expr = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (
            self.else_expr.pos_end if self.else_expr else self.cases[-1][1].pos_end
        )

    def __repr__(self) -> str:
        return f"IfNode(cases={repr(self.cases)}, else_expr={repr(self.else_expr)})"


class ForNode:
    def __init__(
        self, var_name_tok, start_value_node, end_value_node, body, step_value_node=None
    ) -> None:
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.body = body
        self.step_value_node = step_value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body.pos_end

    def __repr__(self) -> str:
        return f"ForNode(var_name={self.var_name_tok.value} from {self.start_value_node} to {self.end_value_node} do {self.body} (step={self.step_value_node}))"


class WhileNode:
    def __init__(self, condition_node, body) -> None:
        self.condition_node = condition_node
        self.body = body

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body.pos_end

    def __repr__(self) -> str:
        return f"WhileNode(cond={self.condition_node}, body={self.body})"
