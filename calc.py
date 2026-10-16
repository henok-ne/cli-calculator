"""A small interactive command-line calculator."""

import math
from typing import Callable

Number = float
Operation = Callable[[Number, Number], Number]


def add(left: Number, right: Number) -> Number:
    """Return the sum of two numbers."""
    return left + right


def subtract(left: Number, right: Number) -> Number:
    """Return the difference between two numbers."""
    return left - right


def multiply(left: Number, right: Number) -> Number:
    """Return the product of two numbers."""
    return left * right


def divide(left: Number, right: Number) -> Number:
    """Return the quotient of two numbers."""
    return left / right


OPERATIONS: dict[str, Operation] = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}
EXIT_COMMANDS = {"q", "quit", "exit", "ex"}


def _read_number(prompt: str) -> Number:
    """Read a finite number from standard input."""
    raw_value = input(prompt).strip()
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError("Please enter a valid number.") from error

    if not math.isfinite(value):
        raise ValueError("Please enter a finite number.")
    return value


def _format_number(value: Number) -> str:
    """Avoid displaying a decimal suffix for whole-number results."""
    if value == 0:
        return "0"

    formatted = str(value)
    return formatted[:-2] if formatted.endswith(".0") else formatted


def main() -> None:
    """Run the calculator until the user enters an exit command."""
    print("CLI Calculator — type 'quit' to exit.")

    while True:
        try:
            choice = input("Operation (+, -, *, /): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if choice in EXIT_COMMANDS:
            print("Goodbye!")
            return

        operation = OPERATIONS.get(choice)
        if operation is None:
            print("Invalid operation. Choose +, -, *, or /, or type 'quit' to exit.")
            continue

        try:
            left = _read_number("First number: ")
            right = _read_number("Second number: ")
            result = operation(left, right)
        except ValueError as error:
            print(f"Invalid input: {error}")
            continue
        except ZeroDivisionError:
            print("Error: Division by zero is not allowed.")
            continue
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if not math.isfinite(result):
            print("Error: Result is outside the supported numeric range.")
            continue

        print(f"Result: {_format_number(result)}")


if __name__ == "__main__":
    main()
