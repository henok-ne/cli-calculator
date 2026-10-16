"""Comprehensive tests for calc.py — covers arithmetic, dispatcher, expression evaluator & formatting."""

import subprocess
import sys
import pytest

import calc
from calc import (
    add,
    sub,
    subtract,
    multi,
    multiply,
    div,
    divide,
    power,
    modulo,
    floor_divide,
    calculate,
    safe_evaluate,
    parse_number,
    format_result,
)

# ── Pure arithmetic ───────────────────────────────────────────────────

class TestArithmetic:
    def test_add(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0.5, 0.5) == 1.0
        assert add(0, 0) == 0

    def test_sub(self):
        assert sub(5, 3) == 2
        assert subtract(5, 3) == 2
        assert sub(0, 5) == -5
        assert sub(-3, -3) == 0

    def test_multi(self):
        assert multi(3, 4) == 12
        assert multiply(3, 4) == 12
        assert multi(-2, 5) == -10
        assert multi(0, 999) == 0

    def test_div(self):
        assert div(6, 3) == 2
        assert divide(6, 3) == 2
        assert div(5, 2) == 2.5
        assert div(-6, 3) == -2

    def test_div_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            div(5, 0)
        with pytest.raises(ZeroDivisionError):
            divide(0, 0)

    def test_power(self):
        assert power(2, 3) == 8
        assert power(5, 0) == 1
        assert power(9, 0.5) == 3.0
        assert power(2, -1) == 0.5

    def test_modulo(self):
        assert modulo(7, 3) == 1
        assert modulo(10, 5) == 0
        assert modulo(-7, 3) == 2

    def test_modulo_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            modulo(5, 0)

    def test_floor_divide(self):
        assert floor_divide(7, 3) == 2
        assert floor_divide(-7, 3) == -3
        assert floor_divide(10, 2) == 5

    def test_floor_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            floor_divide(5, 0)


# ── Dispatcher ────────────────────────────────────────────────────────

class TestCalculate:
    def test_basic_ops(self):
        assert calculate(10, 5, "+") == 15
        assert calculate(10, 5, "-") == 5
        assert calculate(10, 5, "*") == 50
        assert calculate(10, 5, "/") == 2

    def test_extended_ops(self):
        assert calculate(2, 3, "**") == 8
        assert calculate(2, 3, "^") == 8
        assert calculate(7, 3, "%") == 1
        assert calculate(7, 3, "//") == 2

    def test_alias_x(self):
        assert calculate(3, 4, "x") == 12
        assert calculate(3, 4, "X") == 12

    def test_whitespace_trim(self):
        assert calculate(2, 3, " + ") == 5

    def test_unknown_operator(self):
        with pytest.raises(ValueError, match="Unsupported operator"):
            calculate(2, 3, "&")
        with pytest.raises(ValueError):
            calculate(2, 3, "sqrt")

    def test_division_by_zero_via_calculate(self):
        with pytest.raises(ZeroDivisionError):
            calculate(5, 0, "/")
        with pytest.raises(ZeroDivisionError):
            calculate(5, 0, "%")


# ── Safe expression evaluator ─────────────────────────────────────────

class TestSafeEvaluate:
    def test_simple(self):
        assert safe_evaluate("2 + 3") == 5
        assert safe_evaluate("5 - 3") == 2
        assert safe_evaluate("4 * 3") == 12
        assert safe_evaluate("8 / 2") == 4

    def test_precedence(self):
        assert safe_evaluate("2 + 3 * 4") == 14
        assert safe_evaluate("2 * 3 + 4") == 10
        assert safe_evaluate("10 - 4 / 2") == 8.0

    def test_parentheses(self):
        assert safe_evaluate("(2 + 3) * 4") == 20
        assert safe_evaluate("((2 + 3) * 2) + 1") == 11
        assert safe_evaluate("(10 - 4) / 2") == 3.0

    def test_power(self):
        assert safe_evaluate("2 ** 3") == 8
        assert safe_evaluate("2 ** 3 ** 2") == 512  # right-associative: 2**(3**2)
        assert safe_evaluate("2 ^ 3") == 8  # caret alias

    def test_modulo_and_floor(self):
        assert safe_evaluate("7 % 3") == 1
        assert safe_evaluate("7 // 3") == 2

    def test_unary(self):
        assert safe_evaluate("-5") == -5
        assert safe_evaluate("+5") == 5
        assert safe_evaluate("-5 + 3") == -2
        assert safe_evaluate("--5") == 5
        assert safe_evaluate("-(2 + 3)") == -5

    def test_floats(self):
        assert safe_evaluate("2.5 + 0.5") == 3.0
        assert safe_evaluate("0.1 + 0.2") == pytest.approx(0.3)
        assert safe_evaluate("-2.5 * 2") == -5.0
        assert safe_evaluate(".5 * 4") == 2.0

    def test_complex_expressions(self):
        assert safe_evaluate("2 + 3 * (4 - 1)") == 11
        assert safe_evaluate("10 / 2 + 3 * 2") == 11.0
        assert safe_evaluate("(2 + 3) * (4 + 1)") == 25

    def test_x_alias_in_expression(self):
        assert safe_evaluate("3 x 4") == 12
        assert safe_evaluate("3 X 4") == 12

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            safe_evaluate("5 / 0")
        with pytest.raises(ZeroDivisionError):
            safe_evaluate("10 % 0")
        with pytest.raises(ZeroDivisionError):
            safe_evaluate("5 // 0")

    def test_empty_expression(self):
        with pytest.raises(ValueError, match="Empty"):
            safe_evaluate("")
        with pytest.raises(ValueError, match="Empty"):
            safe_evaluate("   ")

    def test_invalid_syntax(self):
        with pytest.raises(ValueError, match="Invalid syntax"):
            safe_evaluate("2 +")
        with pytest.raises(ValueError, match="Invalid syntax"):
            safe_evaluate("(2 + 3")

    def test_disallowed_code(self):
        # Function calls, names, attributes must be rejected
        with pytest.raises(ValueError):
            safe_evaluate("__import__('os').system('ls')")
        with pytest.raises(ValueError):
            safe_evaluate("abs(-5)")
        with pytest.raises(ValueError):
            safe_evaluate("2 & 3")
        with pytest.raises(ValueError):
            safe_evaluate("lambda x: x")

    def test_bitwise_rejected(self):
        with pytest.raises(ValueError):
            safe_evaluate("5 | 3")
        with pytest.raises(ValueError):
            safe_evaluate("5 & 3")


# ── Helpers ───────────────────────────────────────────────────────────

class TestParseNumber:
    def test_int(self):
        assert parse_number("42") == 42
        assert isinstance(parse_number("42"), int)

    def test_float(self):
        assert parse_number("3.14") == 3.14
        assert parse_number(".5") == 0.5
        assert parse_number("1e3") == 1000.0

    def test_negative(self):
        assert parse_number("-7") == -7
        assert parse_number("-3.5") == -3.5

    def test_whitespace(self):
        assert parse_number("  42  ") == 42

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_number("abc")
        with pytest.raises(ValueError):
            parse_number("")


class TestFormatResult:
    def test_int(self):
        assert format_result(5) == "5"
        assert format_result(-3) == "-3"

    def test_float_integer(self):
        assert format_result(3.0) == "3"
        assert format_result(-2.0) == "-2"

    def test_float(self):
        assert format_result(2.5) == "2.5"
        assert format_result(0.12345678901) == "0.123456789"

    def test_large(self):
        assert format_result(1e10) == "10000000000"


# ── CLI one-shot (subprocess smoke) ───────────────────────────────────

class TestCLI:
    def test_cli_expression(self):
        result = subprocess.run(
            [sys.executable, "calc.py", "2 + 2"],
            capture_output=True, text=True, cwd="."
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "4"

    def test_cli_complex(self):
        result = subprocess.run(
            [sys.executable, "calc.py", "(3 + 5) * 2"],
            capture_output=True, text=True, cwd="."
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "16"

    def test_cli_error_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, "calc.py", "5 / 0"],
            capture_output=True, text=True, cwd="."
        )
        assert result.returncode != 0
        assert "Error" in result.stderr or "Error" in result.stdout

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, "calc.py", "--help"],
            capture_output=True, text=True, cwd="."
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()
