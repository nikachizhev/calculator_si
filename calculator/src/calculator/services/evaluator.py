"""Safe arithmetic expression evaluator."""

from __future__ import annotations

import ast
import math
import operator


class CalculationError(ValueError):
    """Raised when an expression is invalid or unsupported."""


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CONSTANTS = {"pi": math.pi, "e": math.e}


def _factorial(value: int | float) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CalculationError("Факториал определён только для целых неотрицательных чисел")
    if value > 100:
        raise CalculationError("Слишком большой факториал")
    return math.factorial(value)


_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "ln": math.log,
    "log": math.log10,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "degrees": math.degrees,
    "radians": math.radians,
    "factorial": _factorial,
}


def calculate(expression: str) -> int | float:
    if not isinstance(expression, str) or not expression.strip():
        raise CalculationError("Введите выражение")
    if len(expression) > 200:
        raise CalculationError("Выражение слишком длинное")
    try:
        result = _evaluate(ast.parse(expression.replace("^", "**"), mode="eval").body)
    except CalculationError:
        raise
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        raise CalculationError("Некорректное выражение") from None
    if isinstance(result, float) and not math.isfinite(result):
        raise CalculationError("Результат вне допустимого диапазона")
    return result


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise CalculationError("Слишком большая степень")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCTIONS
        and len(node.args) == 1
        and not node.keywords
    ):
        return _FUNCTIONS[node.func.id](_evaluate(node.args[0]))
    raise CalculationError("Недопустимая операция или функция")

