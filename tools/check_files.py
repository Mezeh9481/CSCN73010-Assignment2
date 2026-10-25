"""Check text whitespace, final newlines, and YAML syntax for pre-commit."""

import sys
from pathlib import Path

import yaml


def check_file(filename):
    """Return human-readable problems found in one text file."""
    path = Path(filename)
    content = path.read_bytes()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [f"{filename}: text is not UTF-8"]

    problems = []
    if content and not content.endswith(b"\n"):
        problems.append(f"{filename}: missing final newline")
    for number, line in enumerate(text.splitlines(), start=1):
        if line != line.rstrip(" \t"):
            problems.append(f"{filename}:{number}: trailing whitespace")

    if path.suffix in {".yaml", ".yml"}:
        try:
            yaml.safe_load(text)
        except yaml.YAMLError as error:
            problems.append(f"{filename}: invalid YAML: {error}")
    return problems


def main():
    """Report all file problems and return a failing status when any exist."""
    problems = []
    for filename in sys.argv[1:]:
        problems.extend(check_file(filename))
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
