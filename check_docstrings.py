#!/usr/bin/env python3
"""Script to find public methods without docstrings."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


def check_file_for_missing_docstrings(filepath: Path) -> List[Tuple[str, int]]:
    """Check a Python file for public methods missing docstrings.

    Args:
        filepath: Path to Python file to check

    Returns:
        List of (method_name, line_number) tuples for methods missing docstrings
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return []

    missing = []

    for node in ast.walk(tree):
        # Check class methods and functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name

            # Skip private methods (start with _)
            if name.startswith("_"):
                continue

            # Check if it has a docstring
            docstring = ast.get_docstring(node)
            if docstring is None:
                missing.append((name, node.lineno))

    return missing


def main():
    """Main entry point."""
    src_dir = Path("src/kittiwake")

    if not src_dir.exists():
        print(f"Error: {src_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Find all Python files
    py_files = list(src_dir.rglob("*.py"))

    # Track results
    results = {}
    total_missing = 0

    for py_file in sorted(py_files):
        missing = check_file_for_missing_docstrings(py_file)
        if missing:
            results[py_file] = missing
            total_missing += len(missing)

    # Print results
    if results:
        print("=" * 80)
        print(f"Public methods missing docstrings: {total_missing}")
        print("=" * 80)
        print()

        for filepath, missing_methods in results.items():
            try:
                rel_path = filepath.relative_to(Path.cwd())
            except ValueError:
                rel_path = filepath
            print(f"\n{rel_path}:")
            for method_name, lineno in missing_methods:
                print(f"  Line {lineno:4d}: {method_name}()")
    else:
        print("All public methods have docstrings!")

    return 0 if not results else 1


if __name__ == "__main__":
    sys.exit(main())
