"""Tests for the command-line calculator."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import calc


class ArithmeticTests(unittest.TestCase):
    def test_operations(self) -> None:
        cases = (
            (calc.add, 4, 3, 7),
            (calc.subtract, 4, 3, 1),
            (calc.multiply, 4, 3, 12),
            (calc.divide, 9, 3, 3),
        )
        for operation, left, right, expected in cases:
            with self.subTest(operation=operation.__name__):
                self.assertEqual(operation(left, right), expected)

    def test_divide_by_zero_raises(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            calc.divide(1, 0)

    def test_read_number_rejects_invalid_and_non_finite_values(self) -> None:
        for value in ("not a number", "nan", "inf"):
            with self.subTest(value=value), patch("builtins.input", return_value=value):
                with self.assertRaises(ValueError):
                    calc._read_number("Number: ")


class InteractiveCalculatorTests(unittest.TestCase):
    def run_calculator(self, responses: list[str]) -> str:
        output = io.StringIO()
        with patch("builtins.input", side_effect=responses), redirect_stdout(output):
            calc.main()
        return output.getvalue()

    def test_calculates_decimal_values_and_exits(self) -> None:
        output = self.run_calculator(["+", "2.5", "1.25", "QUIT"])
        self.assertIn("Result: 3.75", output)
        self.assertIn("Goodbye!", output)

    def test_invalid_operation_does_not_stop_calculator(self) -> None:
        output = self.run_calculator(["%", "*", "4", "3", "q"])
        self.assertIn("Invalid operation", output)
        self.assertIn("Result: 12", output)

    def test_division_by_zero_does_not_stop_calculator(self) -> None:
        output = self.run_calculator(["/", "5", "0", "+", "2", "3", "exit"])
        self.assertIn("Division by zero is not allowed", output)
        self.assertIn("Result: 5", output)

    def test_overflow_result_is_reported(self) -> None:
        output = self.run_calculator(["+", "1e308", "1e308", "-", "5", "2", "quit"])
        self.assertIn("outside the supported numeric range", output)
        self.assertIn("Result: 3", output)

    def test_invalid_number_does_not_stop_calculator(self) -> None:
        output = self.run_calculator(["+", "oops", "+", "4", "2", "ex"])
        self.assertIn("Invalid input", output)
        self.assertIn("Result: 6", output)

    def test_end_of_input_exits_cleanly(self) -> None:
        output = io.StringIO()
        with patch("builtins.input", side_effect=EOFError), redirect_stdout(output):
            calc.main()
        self.assertIn("Goodbye!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
