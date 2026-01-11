#!/usr/bin/env python3
"""Kittiwake CLI entry point.

Provides keyboard-first TUI data exploration tool with multiple dataset support,
filtering, aggregation, and export capabilities.
"""

import typer

from .app import KittiwakeApp
from .models import DatasetSession

app = typer.Typer(
    help="Kittiwake - Terminal-based data exploration tool",
    no_args_is_help=False,  # Allow bare 'kw' without showing help
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Launch Kittiwake TUI data explorer with empty workspace.

    Use 'kw load <files>' to pre-load datasets on startup.
    """
    # Only run if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        # Initialize session
        session = DatasetSession()

        # Create app with session (empty workspace)
        kw_app = KittiwakeApp(session=session)

        # Run the TUI app
        kw_app.run()


@app.command()
def load(
    paths: list[str] = typer.Argument(
        ..., help="Dataset files or URLs to load on startup"
    ),
) -> None:
    """Load specified datasets on startup.

    Examples:
        kw load data.csv
        kw load file1.csv file2.parquet
        kw load local.csv https://example.com/data.json

    Args:
        paths: List of file paths or URLs to load automatically

    """
    # Initialize session
    session = DatasetSession()

    # Create app with session
    kw_app = KittiwakeApp(session=session)

    # Store paths for app to load on startup
    kw_app.initial_load_paths = paths

    # Run the TUI app
    kw_app.run()


def cli_app() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    cli_app()
