from .constants import (
    TT_DIVIDE,
    TT_EE,
    TT_GT,
    TT_GTE,
    TT_KEYWORD,
    TT_LT,
    TT_LTE,
    TT_MINUS,
    TT_MODULO,
    TT_MUL,
    TT_NE,
    TT_PLUS,
)
from .errors import RTError
from .nodes import (
    BinOpNode,
    NumberNode,
    PowerOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignmentNode,
    VarReassignmentNode,
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


class Boolean:
    def __init__(self, value) -> None:
        self.value = bool(value)
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def __repr__(self) -> str:
        return "fact" if self.value else "cap"


class Number:
    def __init__(self, value) -> None:
        self.value = value
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "Attempt to Divide by zero!",
                )
            return Number(self.value / other.value), None
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "Attempt to divide by zero (modulo)!",
                )
            return Number(self.value % other.value), None
        return NotImplemented  # This helps coverage tools know this path exists

    def __pow__(self, other_number):
        if isinstance(other_number, Number):
            return Number(self.value**other_number.value), None
        return NotImplemented

    def stanza_eq(self, other):
        if isinstance(other, Number):
            return (
                (Boolean(self.value == other.value), None)
                if self.value == other.value
                else (Boolean(self.value == other.value), None)
            )
        return Boolean(False), None

    def stanza_ne(self, other):
        if isinstance(other, Number):
            return (
                (Boolean(self.value != other.value), None)
                if self.value != other.value
                else (Boolean(self.value != other.value), None)
            )
        return Boolean(False), None

    def compare(self, other, tok_type):
        if isinstance(other, Number):
            if tok_type == TT_GT:
                return Boolean(self.value > other.value), None
            elif tok_type == TT_LT:
                return Boolean(self.value < other.value), None
            elif tok_type == TT_GTE:
                return Boolean(self.value >= other.value), None
            elif tok_type == TT_LTE:
                return Boolean(self.value <= other.value), None
        return None, RTError(other.pos_start, other.pos_end, "Expected a number")

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
            result, error = left + right
        elif op.type == TT_MINUS:
            result, error = left - right
        elif op.type == TT_MUL:
            result, error = left * right
        elif op.type == TT_DIVIDE:
            result, error = left / right
        elif op.type == TT_MODULO:
            result, error = left % right
        elif op.type == TT_EE:
            result, error = left.stanza_eq(right)
        elif op.type == TT_NE:
            result, error = left.stanza_ne(right)
        elif op.type in (TT_GT, TT_GTE, TT_LTE, TT_LT):
            result, error = left.compare(right, op.type)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

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
            number, error = number * Number(-1)

        if node.op.matches(TT_KEYWORD, "NOT"):
            if isinstance(number, Boolean):
                number = Boolean(not number.value)

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
        result, error = base**power
        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_VarAssignmentNode(self, node: VarAssignmentNode):
        res = RTResult()
        var_name = node.var_name
        value = res.register(self.visit(node.value))
        if res.error:
            return res
        check = self.symbol_table.get(var_name)
        if check:
            return res.failure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"Variable {var_name} already assigned",
                )
            )
        self.symbol_table.set(var_name, value)
        return res.success(None)

    def visit_VarReassignmentNode(self, node: VarReassignmentNode):
        res = RTResult()
        var_name = node.var_name
        check = self.symbol_table.get(var_name)
        if check:
            value = res.register(self.visit(node.value))
            self.symbol_table.set(var_name, value)
            return res.success(None)
        return res.failure(
            RTError(
                node.pos_start,
                node.pos_end,
                f"Variable {var_name} not defined",
            )
        )

    def visit_VarAccessNode(self, node: VarAccessNode):
        res = RTResult()
        var_name = node.var_access_tok.value
        value = self.symbol_table.get(var_name)
        if not value:
            return res.failure(
                RTError(node.pos_start, node.pos_end, f"{var_name} not defined.")
            )

        return res.success(value)
