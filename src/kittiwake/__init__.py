"""Kittiwake TUI Data Explorer."""

from .app import KittiwakeApp
from .models import DatasetSession


def main() -> None:
    """Run the Kittiwake CLI application."""
    import sys
    from pathlib import Path

    # Handle command line arguments
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        paths = []

    # Create session and app
    session = DatasetSession()
    app = KittiwakeApp(session=session)

    # Set initial paths if provided
    if paths:
        app.initial_load_paths = [str(p) for p in paths]

    # Run application
    app.run()


if __name__ == "__main__":
    main()
