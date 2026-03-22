from .constants import TT
from .errors import RTError
from .nodes import (
    BinOpNode,
    CallNode,
    ForNode,
    FuncDefNode,
    IfNode,
    NumberNode,
    PowerOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignmentNode,
    VarReassignmentNode,
    WhileNode,
)

"""Context"""


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None) -> None:
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


"""Symbol Table"""


class SymbolTable:
    def __init__(self, parent=None) -> None:
        self.symbols = {}
        self.parent = parent

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

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


class Value:
    """Base class for all runtime values to handle shared properties."""

    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self


class Boolean(Value):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = bool(value)

    def is_true(self):
        return self.value

    def __repr__(self) -> str:
        return "fact" if self.value else "cap"


class Function(Value):
    def __init__(self, name, args_node, body_node, original_context) -> None:
        super().__init__()
        self.name = name.value if name else "|anonymous|"
        self.args_node = args_node
        self.body_node = body_node
        self.set_context(original_context)

    def execute(self, args, curr_interpreter):
        res = RTResult()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) != len(self.args_node):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"Expected {len(self.args_node)} arguments, got {len(args)}",
                    self.context,
                )
            )

        for i, arg in enumerate(args):
            new_context.symbol_table.set(self.args_node[i].value, arg)

        out = res.register(curr_interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success(out)

    def __repr__(self) -> str:
        return f"function {self.name}"


class Number(Value):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
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
                    self.context,
                )
            return Number(self.value / other.value), None
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "Attempt to divide by zero!",
                    self.context,
                )
            return Number(self.value % other.value), None
        return NotImplemented

    def __pow__(self, other_number):
        if isinstance(other_number, Number):
            return Number(self.value**other_number.value), None
        return NotImplemented

    def stanza_eq(self, other):
        if isinstance(other, Number):
            return Boolean(self.value == other.value), None
        return Boolean(False), None

    def stanza_ne(self, other):
        if isinstance(other, Number):
            return Boolean(self.value != other.value), None
        return Boolean(False), None

    def compare(self, other, tok_type, context):
        if isinstance(other, Number):
            if tok_type == TT.GT:
                return Boolean(self.value > other.value), None
            elif tok_type == TT.LT:
                return Boolean(self.value < other.value), None
            elif tok_type == TT.GTE:
                return Boolean(self.value >= other.value), None
            elif tok_type == TT.LTE:
                return Boolean(self.value <= other.value), None
        return None, RTError(
            other.pos_start, other.pos_end, "Expected a number", context
        )

    def is_true(self):
        return self.value != 0

    def __repr__(self) -> str:
        return f"{self.value}"


"""Interpreter"""


class Interpreter:
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table

    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_BinOpNode(self, node: BinOpNode, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res
        op = node.op
        if op.type == TT.PLUS:
            result, error = left + right
        elif op.type == TT.MINUS:
            result, error = left - right
        elif op.type == TT.MUL:
            result, error = left * right
        elif op.type == TT.DIVIDE:
            result, error = left / right
        elif op.type == TT.MODULO:
            result, error = left % right
        elif op.type == TT.EE:
            result, error = left.stanza_eq(right)
        elif op.type == TT.NE:
            result, error = left.stanza_ne(right)
        elif op.type in (TT.GT, TT.GTE, TT.LTE, TT.LT):
            result, error = left.compare(right, op.type, context)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_NumberNode(self, node: NumberNode, context):
        result = RTResult()
        return result.success(
            Number(node.token.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_UnaryOpNode(self, node: UnaryOpNode, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res
        error = None
        if node.op.type == TT.MINUS:
            number, error = number * Number(-1)

        if node.op.matches(TT.KEYWORD, "not"):
            if isinstance(number, Boolean):
                number = Boolean(not number.value)

        if error:
            return res.failure(error)

        return res.success(
            number.set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_PowerOpNode(self, node: PowerOpNode, context):
        res = RTResult()
        base = res.register(self.visit(node.base, context))
        if res.error:
            return res
        power = res.register(self.visit(node.exponent, context))
        if res.error:
            return res
        result, error = base**power
        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_VarAssignmentNode(self, node: VarAssignmentNode, context):
        res = RTResult()
        var_name = node.var_name
        value = res.register(self.visit(node.value, context))
        if res.error:
            return res
        check = context.symbol_table.get(var_name)
        if check:
            return res.failure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"Variable {var_name} already assigned",
                    context,
                )
            )
        context.symbol_table.set(var_name, value)
        return res.success(None)

    def visit_VarReassignmentNode(self, node: VarReassignmentNode, context):
        res = RTResult()
        var_name = node.var_name
        check = context.symbol_table.get(var_name)
        if check:
            value = res.register(self.visit(node.value, context))
            context.symbol_table.set(var_name, value)
            return res.success(None)
        return res.failure(
            RTError(
                node.pos_start,
                node.pos_end,
                f"Variable {var_name} not defined",
                context,
            )
        )

    def visit_VarAccessNode(self, node: VarAccessNode, context):
        res = RTResult()
        var_name = node.var_access_tok.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(
                RTError(
                    node.pos_start, node.pos_end, f"{var_name} not defined.", context
                )
            )

        return res.success(value)

    def visit_IfNode(self, node: IfNode, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)
        if node.else_expr:
            else_value = res.register(self.visit(node.else_expr, context))
            if res.error:
                return res
            return res.success(else_value)
        return res.success(None)

    def visit_ForNode(self, node: ForNode, context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error:
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        def condition() -> (
            bool
        ):  # because assignment of lambda function to a variable is explicitly discouraged by PEP 8.
            if step_value.value >= 0:
                return i < end_value.value
            return i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.visit(node.body, context))
            if res.error:
                return res
        return res.success(None)

    def visit_WhileNode(self, node: WhileNode, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body, context))
            if res.error:
                return res
        return res.success(None)

    def visit_FuncDefNode(self, node: FuncDefNode, context):
        res = RTResult()
        func = Function(node.func_name_tok, node.arg_name_toks, node.body_node, context)
        if func.name == "|anonymous|":
            return res.success(func)
        context.symbol_table.set(func.name, func)
        return res.success(func)

    def visit_CallNode(self, node: CallNode, context):
        res = RTResult()
        name = node.node_to_call
        args = node.arg_nodes
        func = res.register(self.visit(name, context))
        if res.error:
            return res
        if not isinstance(func, Function):
            return res.failure(
                RTError(
                    node.pos_start, node.pos_end, f"{func} is not a function", context
                )
            )
        evaluated_args = []
        for arg in args:
            evaluated_arg = res.register(self.visit(arg, context))
            evaluated_args.append(evaluated_arg)
        output = res.register(func.execute(evaluated_args, self))
        if res.error:
            return res
        return res.success(output)
