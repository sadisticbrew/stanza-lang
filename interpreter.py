from constants import TT_DIVIDE, TT_MINUS, TT_MUL, TT_PLUS
from errors import RTError
from nodes import (
    BinOpNode,
    NumberNode,
    PowerOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignmentNode,
)

"""Symbol Table"""


class SymbolTable:
    def __init__(self) -> None:
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if not value and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


"""RTResult"""


class RTResult:
    def __init__(self) -> None:
        self.error = self.value = None

    def register(self, result):
        if isinstance(result, RTResult):
            if result.error:
                self.error = result.error
            return result.value
        # return result

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


class Number:
    def __init__(self, value) -> None:
        self.value = value
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other_number):
        if isinstance(other_number, Number):
            return Number(other_number.value + self.value), None

    def subbed_from(self, other_number):
        if isinstance(other_number, Number):
            return Number(other_number.value - self.value), None

    def subbed_by(self, other_number):
        if isinstance(other_number, Number):
            return Number(self.value - other_number.value), None

    def multplied_by(self, other_number):
        if isinstance(other_number, Number):
            return Number(self.value * other_number.value), None

    def divided_by(self, other_number):
        if isinstance(other_number, Number):
            if other_number.value == 0:
                return None, RTError(
                    other_number.pos_start,
                    other_number.pos_end,
                    "Attempt to divide by zero!",
                )
            return Number(self.value / other_number.value)

    def raise_to(self, other_number):
        if isinstance(other_number, Number):
            return Number(self.value**other_number.value), None

    def __repr__(self) -> str:
        return f"{self.value}"


"""Interpreter"""


class Interpreter:
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_BinOpNode(self, node: BinOpNode):
        res = RTResult()
        left = res.register(self.visit(node.left_node))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node))
        if res.error:
            return res
        op = node.op
        if op.type == TT_PLUS:
            result, error = left.added_to(right)
        elif op.type == TT_MINUS:
            result, error = left.subbed_from(right)
        elif op.type == TT_MUL:
            result, error = left.multplied_by(right)
        elif op.type == TT_DIVIDE:
            result, error = left.divided_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))
        # print(result)

    def visit_NumberNode(self, node: NumberNode):
        result = RTResult()
        return result.success(
            Number(node.token.value).set_pos(node.pos_start, node.pos_end)
        )

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        res = RTResult()
        number = res.register(self.visit(node.node))
        if res.error:
            return res
        error = None
        if node.op.type == TT_MINUS:
            number, error = number.multplied_by(Number(-1))
        if error:
            return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_PowerOpNode(self, node: PowerOpNode):
        res = RTResult()
        base = res.register(self.visit(node.base))
        if res.error:
            return res
        power = res.register(self.visit(node.exponent))
        if res.error:
            return res
        result, error = base.raise_to(power)
        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_VarAssignmentNode(self, node: VarAssignmentNode):
        res = RTResult()
        var_name = node.var_name
        value = res.register(self.visit(node.value))
        if res.error:
            return res
        self.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_VarAccessNode(self, node: VarAccessNode):
        res = RTResult()
        var_name = node.var_access_tok.value
        value = self.symbol_table.get(var_name)
        if not value:
            return res.failure(
                RTError(node.pos_start, node.pos_end, f"{var_name} not defined.")
            )

        return res.success(value)
