#!/usr/bin/env python3
"""
CLI Calculator — A clean, tested command-line calculator.

Features:
  - Interactive REPL with expression evaluation
  - Basic arithmetic: +, -, *, /, **, %, //
  - Safe AST-based expression parsing (no eval)
  - Float & integer support, parentheses, unary operators
  - History, help, and graceful error handling
  - Non-interactive mode: `python calc.py "2 + 3 * 4"`

Usage:
  python calc.py                  # start REPL
  python calc.py "2 + 2"          # evaluate once
  python calc.py -e "(3+5)*2"     # evaluate once
  python calc.py --help           # show help
"""

from __future__ import annotations

import argparse
import ast
import operator
import sys
from typing import Callable, Union

Number = Union[int, float]

# ── Pure arithmetic operations ────────────────────────────────────────

def add(x: Number, y: Number) -> Number:
    """Return x + y."""
    return x + y

def sub(x: Number, y: Number) -> Number:
    """Return x - y."""
    return x - y

def subtract(x: Number, y: Number) -> Number:
    """Alias for sub — clearer API for callers/tests."""
    return x - y

def multi(x: Number, y: Number) -> Number:
    """Return x * y (kept for backwards compat)."""
    return x * y

def multiply(x: Number, y: Number) -> Number:
    """Return x * y."""
    return x * y

def div(x: Number, y: Number) -> Number:
    """Return x / y. Raises ZeroDivisionError if y == 0."""
    if y == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return x / y

def divide(x: Number, y: Number) -> Number:
    """Alias for div."""
    return div(x, y)

def power(x: Number, y: Number) -> Number:
    """Return x ** y."""
    return x ** y

def modulo(x: Number, y: Number) -> Number:
    """Return x % y."""
    if y == 0:
        raise ZeroDivisionError("Modulo by zero is not allowed.")
    return x % y

def floor_divide(x: Number, y: Number) -> Number:
    """Return x // y."""
    if y == 0:
        raise ZeroDivisionError("Floor division by zero is not allowed.")
    return x // y


# ── Dispatcher ──────────────────────────────────────────────────────────

OPERATIONS: dict[str, Callable[[Number, Number], Number]] = {
    "+": add,
    "-": sub,
    "*": multi,
    "/": div,
    "**": power,
    "^": power,       # ^ as power for UX (caret is intuitive)
    "%": modulo,
    "//": floor_divide,
    "x": multi,       # allow 'x' as multiply
    "X": multi,
}

# Human-readable descriptions
OP_HELP: dict[str, str] = {
    "+": "addition",
    "-": "subtraction",
    "*": "multiplication",
    "/": "division",
    "** / ^": "exponentiation (power)",
    "%": "modulo (remainder)",
    "//": "floor division",
}


def calculate(num1: Number, num2: Number, op: str) -> Number:
    """
    Dispatch a binary operation.

    Args:
        num1, num2: operands
        op: operator symbol (one of OPERATIONS keys)

    Returns:
        Result of applying the operator.

    Raises:
        ValueError: if operator is unknown
        ZeroDivisionError: on division by zero
    """
    op = op.strip()
    if op not in OPERATIONS:
        raise ValueError(f"Unsupported operator '{op}'. Supported: {', '.join(OPERATIONS.keys())}")
    return OPERATIONS[op](num1, num2)


# ── Safe expression evaluator (AST-based, no eval) ─────────────────────

_ALLOWED_BINOPS: dict[type, Callable[[Number, Number], Number]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_ALLOWED_UNARYOPS: dict[type, Callable[[Number], Number]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> Number:
    """Recursively evaluate an AST node. Only whitelisted nodes allowed."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")
    # Python <3.8 compat fallback (ast.Num)
    if isinstance(node, ast.Num):  # type: ignore
        return node.n  # type: ignore

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BINOPS:
            raise ValueError(f"Operator '{op_type.__name__}' is not allowed")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        func = _ALLOWED_BINOPS[op_type]
        try:
            return func(left, right)
        except ZeroDivisionError as e:
            raise ZeroDivisionError("Division by zero is not allowed.") from e

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARYOPS:
            raise ValueError(f"Unary operator '{op_type.__name__}' is not allowed")
        operand = _eval_node(node.operand)
        return _ALLOWED_UNARYOPS[op_type](operand)

    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def safe_evaluate(expression: str) -> Number:
    """
    Safely evaluate a mathematical expression string.

    Supports: + - * / ** % // parentheses unary +/- floats.

    Example:
        safe_evaluate("2 + 3*(4-1)") -> 11
        safe_evaluate("2 ** 3")     -> 8
        safe_evaluate("-5 + 2.5")   -> -2.5

    Raises:
        ValueError: on syntax errors or disallowed constructs
        ZeroDivisionError: on division by zero
    """
    if not expression or not expression.strip():
        raise ValueError("Empty expression")

    # UX: allow ^ as exponent, x/X as multiply before parsing
    # But be careful: ^ in Python AST is BitXor (not allowed). Transform before parse.
    # Replace ^ with ** (but avoid messing up ** already present - simple approach)
    expr = expression.strip()
    # Support 'x' as multiply in expressions like "3 x 4" -> "3 * 4"
    # Only do word-boundary replacement to avoid breaking variable names (none allowed anyway)
    # Simple token replacement
    # For ^ : single char exponent
    if "^" in expr:
        expr = expr.replace("^", "**")
    # For 'x' between numbers/parentheses: regex replacement
    import re
    # replace " 5 x 3" or "5x3" patterns -> "*"
    expr = re.sub(r'(\d|\))\s*[xX]\s*(\d|\(|\-)', r'\1 * \2', expr)

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e.msg}") from e

    result = _eval_node(tree)
    return result


# ── Helpers ─────────────────────────────────────────────────────────────

def parse_number(s: str) -> Number:
    """Parse string to int or float. Raises ValueError on failure."""
    s = s.strip()
    try:
        # Try int first to preserve type for integer results
        if "." not in s and "e" not in s.lower():
            return int(s)
        return float(s)
    except ValueError:
        # Try float fallback (handles '1e3', '.5', etc.)
        try:
            return float(s)
        except ValueError as e:
            raise ValueError(f"'{s}' is not a valid number") from e


def format_result(value: Number) -> str:
    """Pretty-format a result: hide trailing .0, limit float noise."""
    if isinstance(value, float):
        # Avoid 2.9999999999 artefacts
        if value.is_integer():
            return str(int(value))
        # 10 significant digits, strip trailing zeros
        formatted = f"{value:.10g}"
        return formatted
    return str(value)


# ── CLI / REPL ──────────────────────────────────────────────────────────

WELCOME = """\
┌─────────────────────────────────────────┐
│  🧮  CLI Calculator                      │
│  Type an expression (e.g. 2 + 3 * 4)   │
│  Type 'help' for commands, 'exit' to quit │
└─────────────────────────────────────────┘
"""

HELP_TEXT = """\
Commands:
  help, h          Show this help
  history          Show calculation history
  clear, c         Clear history and screen
  exit, quit, q, ex  Quit

Operators:
  +   addition            5 + 3 = 8
  -   subtraction         5 - 3 = 2
  *   multiplication      5 * 3 = 15
  /   division            6 / 3 = 2
  **  exponentiation      2 ** 3 = 8
  ^   exponentiation      2 ^ 3 = 8  (alias)
  %   modulo              7 % 3 = 1
  //  floor division      7 // 3 = 2

Expressions:
  Supports parentheses and full expressions:
    (2 + 3) * 4      → 20
    -5 + 2.5         → -2.5
    2 ** 3 + 1       → 9

Legacy step-by-step mode:
  When prompted, you can also enter: <num1> <operator> <num2>
  e.g. "5 * 3" works the same as expression mode.

Examples:
  calc> 2 + 2
  = 4
  calc> (10 - 4) / 2
  = 3
"""

EXIT_COMMANDS = {"exit", "quit", "q", "ex", "exit()", "quit()"}
HELP_COMMANDS = {"help", "h", "?"}
CLEAR_COMMANDS = {"clear", "c", "cls"}
HISTORY_COMMANDS = {"history", "hist", "hst"}


def repl() -> None:
    """Run the interactive Read-Eval-Print Loop."""
    print(WELCOME)
    history: list[tuple[str, Number]] = []

    while True:
        try:
            raw = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 👋")
            break

        if not raw:
            continue

        lower = raw.lower()

        if lower in EXIT_COMMANDS:
            print("Goodbye! 👋")
            break

        if lower in HELP_COMMANDS:
            print(HELP_TEXT)
            continue

        if lower in CLEAR_COMMANDS:
            history.clear()
            # ANSI clear screen if available; fallback to newlines
            if sys.stdout.isatty():
                print("\033[2J\033[H", end="")
            else:
                print("\n" * 2)
            print(WELCOME)
            continue

        if lower in HISTORY_COMMANDS:
            if not history:
                print("(no history yet)")
            else:
                for idx, (expr, res) in enumerate(history, 1):
                    print(f"  {idx:>3}. {expr} = {format_result(res)}")
            continue

        # Try to evaluate as full expression first
        try:
            result = safe_evaluate(raw)
            formatted = format_result(result)
            print(f"  = {formatted}")
            history.append((raw, result))
            continue
        except ZeroDivisionError as e:
            print(f"  ✘ Error: {e}")
            continue
        except ValueError:
            # Might be legacy "num op num" with bad spacing or single-operator prompt fallback
            pass

        # Fallback: try legacy two-number + operator parsing: "5 + 3" already handled above,
        # but we keep explicit error messaging for unsupported operators etc.
        # If expression failed, report the ValueError reason
        try:
            result = safe_evaluate(raw)
            print(f"  = {format_result(result)}")
            history.append((raw, result))
        except (ValueError, ZeroDivisionError, ArithmeticError, OverflowError) as e:
            print(f"  ✘ Error: {e}")
        except Exception as e:  # pragma: no cover - safety net
            print(f"  ✘ Unexpected error: {e}")


def main() -> None:
    """CLI entry-point: handles args or launches REPL."""
    parser = argparse.ArgumentParser(
        prog="calc",
        description="A friendly CLI calculator — evaluate expressions or launch an interactive REPL.",
        epilog="Examples:  calc \"2 + 2\"   calc \"(3+5)*2\"   calc --interactive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "expression",
        nargs="?",
        help="mathematical expression to evaluate (e.g. \"2 + 3 * 4\")",
    )
    parser.add_argument(
        "-e", "--eval",
        dest="eval_expr",
        help="expression to evaluate (alternative to positional arg)",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="force interactive REPL even if an expression is given",
    )
    parser.add_argument(
        "--no-welcome",
        action="store_true",
        help="suppress welcome banner in REPL",
    )

    args = parser.parse_args()

    expr = args.eval_expr or args.expression

    if expr and not args.interactive:
        try:
            result = safe_evaluate(expr)
            print(format_result(result))
            sys.exit(0)
        except ZeroDivisionError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:  # pragma: no cover
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # If expression + interactive, evaluate first then drop to REPL
    if expr and args.interactive:
        try:
            result = safe_evaluate(expr)
            print(f"= {format_result(result)}")
        except Exception as e:
            print(f"Error: {e}")

    if args.no_welcome:
        global WELCOME
        WELCOME = ""

    repl()


if __name__ == "__main__":
    main()
