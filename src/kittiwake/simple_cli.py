#!/usr/bin/env python3
"""Simplified Kittiwake CLI entry point."""

import sys


# Simple CLI for testing
def main():
    """Print loaded datasets or welcome message.

    Displays list of datasets if provided as arguments, otherwise shows welcome message.
    """
    if len(sys.argv) > 1:
        print(f"Loading datasets: {sys.argv[1:]}")
    else:
        print("Kittiwake TUI Data Explorer - Use 'kw load <files>' to load datasets")


if __name__ == "__main__":
    main()
