# 🧮 CLI Calculator

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-43%20passing-brightgreen)](#testing)

A clean, friendly command-line calculator written in Python. Evaluate full mathematical expressions safely — with no `eval()` — or use an interactive REPL.

> **New in v2:** Full expression parsing (`(2+3)*4`), float support, `**` / `%` / `//`, history, `--help` CLI flags, and a proper test suite.

---

## ✨ Features

- **Arithmetic:** `+` addition · `-` subtraction · `*` multiplication · `/` division
- **Advanced:** `**` / `^` exponentiation · `%` modulo · `//` floor division
- **Expressions:** parentheses, unary `+/-`, floats, operator precedence — e.g. `(4 + 2) * 3 / 2`
- **Safe evaluation:** AST-based parser (no `eval`/`exec`), rejects arbitrary code
- **Input validation & error handling:** clear errors for bad input, division by zero, syntax errors
- **Dual modes:**
  - **REPL** — interactive prompt with `help`, `history`, `clear`, `exit`
  - **One-shot** — `python calc.py "2 + 2"` for scripts & piping
- **Pure functions** with type hints, docstrings — easy to test & extend

---

## 🚀 Quick Start

### Requirements
- Python 3.8+ (no external dependencies)

### Run

```bash
# Interactive REPL
python calc.py

# One-shot evaluation
python calc.py "2 + 3 * 4"
# → 14

python calc.py -e "(10 - 4) / 2"
# → 3

python calc.py "2 ** 8"
# → 256

# Help
python calc.py --help
```

### Install as a command (optional)

```bash
pip install -e .
calc "5 * 5"
# → 25

calc --interactive
```

---

## 💬 REPL Usage

```
┌─────────────────────────────────────────┐
│  🧮  CLI Calculator                      │
│  Type an expression (e.g. 2 + 3 * 4)   │
│  Type 'help' for commands, 'exit' to quit │
└─────────────────────────────────────────┘

calc> 2 + 2
  = 4
calc> (3 + 5) * 2
  = 16
calc> 7 % 3
  = 1
calc> 2 ^ 8
  = 256
calc> history
    1. 2 + 2 = 4
    2. (3 + 5) * 2 = 16
    3. 7 % 3 = 1
    4. 2 ^ 8 = 256
calc> help
  ... shows operators, examples, commands
calc> exit
Goodbye! 👋
```

**REPL commands**

| Command | Action |
|---------|--------|
| `help`, `h`, `?` | Show help |
| `history` | Show past calculations |
| `clear`, `c` | Clear history & screen |
| `exit`, `quit`, `q`, `ex` | Quit |

---

## 📖 Examples

```python
from calc import calculate, safe_evaluate, add, sub, div

calculate(5, 3, "+")          # 8
calculate(5, 3, "*")          # 15
calculate(7, 3, "//")         # 2

safe_evaluate("2 + 3 * 4")   # 14  (precedence respected)
safe_evaluate("(2+3)*4")     # 20
safe_evaluate("-5 + 2.5")    # -2.5
safe_evaluate("2 ** 10")     # 1024
```

### Operator reference

| Op | Name | Example |
|----|------|---------|
| `+` | addition | `5 + 3 = 8` |
| `-` | subtraction | `5 - 3 = 2` |
| `*` | multiplication | `5 * 3 = 15` |
| `/` | division | `6 / 3 = 2` |
| `**` or `^` | exponentiation | `2 ** 3 = 8` |
| `%` | modulo | `7 % 3 = 1` |
| `//` | floor division | `7 // 3 = 2` |

---

## 🧪 Testing

```bash
pip install pytest
pytest -v          # run all tests
pytest --cov       # with coverage (requires pytest-cov)
```

43 tests cover arithmetic functions, the dispatcher, expression evaluation, error handling, and formatting.

---

## 📁 Project Structure

```
cli-calculator/
├── calc.py              # Main calculator — pure functions + CLI + REPL
├── pyproject.toml       # Project metadata & build config
├── tests/
│   └── test_calc.py     # Comprehensive test suite
├── .github/
│   └── workflows/ci.yml # CI: lint + tests on push
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🛠 Design Decisions

| Concern | Choice |
|---------|--------|
| **Security** | AST parser with allow-list; `eval()` never used |
| **Dependencies** | Zero runtime deps — stdlib only |
| **Backwards compat** | Legacy `add`/`sub`/`multi`/`div` names kept |
| **Output** | `format_result` hides `3.0` → `3`, uses `:.10g` to avoid float noise |
| **Exit codes** | `0` on success, `1` on error — pipe-friendly |

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to extend the calculator.

---

## 🤝 Contributing

PRs welcome! Please:
1. Fork & branch
2. `pytest` passes
3. Follow existing style (functions return values, don't print; add type hints & tests)

---

## 📝 Changelog

### v2.0.0
- Rewrite: remove duplicated code, fix ZeroDivision bug
- Add float, `**`, `%`, `//`, parentheses, precedence
- Add safe AST expression evaluator
- Add CLI args (`expression`, `-e`, `-i`, `--help`)
- Add REPL commands (`help`, `history`, `clear`)
- Add `pyproject.toml`, tests, CI, LICENSE

### v1.0.0
- Initial release: `+ - * /`, integer-only, basic loop

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

*Built with Python. Keep it simple, keep it correct.*
