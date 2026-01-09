"""Entry point for kittiwake package."""


# Import main components
from .cli import app as cli_app


def main():
    """Main entry point for CLI."""
    # Use the Typer app from cli.py
    cli_app()


if __name__ == "__main__":
    main()
