"""Entry point for kittiwake package."""

import sys
from pathlib import Path

# Import main components
from .app import KittiwakeApp
from .models import DatasetSession
from .cli import app as cli_app


def main():
    """Main entry point for CLI."""
    # Use the Typer app from cli.py
    cli_app()


if __name__ == "__main__":
    main()
