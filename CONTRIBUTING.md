# Contributing to CLI Calculator

Thank you for considering a contribution!

## Getting Started

```bash
git clone https://github.com/henok-ne/cli-calculator
cd cli-calculator
python -m venv .venv && source .venv/bin/activate
pip install pytest pytest-cov ruff
```

## Development Workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make changes to `calc.py` — keep functions pure (return values, don't print).
3. Add tests in `tests/test_calc.py`.
4. Run checks:

```bash
pytest -v
python -m ruff check calc.py
python calc.py "2 + 2"   # manual smoke test
```

5. Commit with a clear message and open a PR.

## Style Guide

- Type hints and docstrings for public functions.
- Use `format_result()` for display; keep arithmetic functions side-effect free.
- Extend `OPERATIONS` and `_ALLOWED_BINOPS` rather than adding ad-hoc `if/elif`.
- Safe evaluator must never use `eval`/`exec` — only `ast.parse` allow-list.

## Adding a New Operator

Example: adding `sqrt` is out-of-scope (unary), but a binary operator like `//` was added as:

1. Define `def floor_divide(x, y): ...` with ZeroDivision check.
2. Register in `OPERATIONS = { "//": floor_divide, ... }`.
3. Map AST node in `_ALLOWED_BINOPS` if it has an `ast` representation.
4. Add tests.

## Reporting Bugs

Open an issue with: Python version, exact input, expected vs actual output, and traceback if any.
