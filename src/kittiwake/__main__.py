"""Entry point for kittiwake package."""

# Import main components
from .cli import app as cli_app


def main():
    """Run the Kittiwake CLI application."""
    # Use the Typer app from cli.py
    cli_app()


if __name__ == "__main__":
    main()
