#!/usr/bin/env python3
"""
Simplified Kittiwake CLI entry point.
"""

import sys
from pathlib import Path


# Simple CLI for testing
def main():
    if len(sys.argv) > 1:
        print(f"Loading datasets: {sys.argv[1:]}")
    else:
        print("Kittiwake TUI Data Explorer - Use 'kw load <files>' to load datasets")


if __name__ == "__main__":
    main()
