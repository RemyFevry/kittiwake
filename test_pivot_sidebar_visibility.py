#!/usr/bin/env python3
"""Test script to verify pivot sidebar widget visibility."""

from textual.app import App, ComposeResult
from textual.widgets import Footer

from src.kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar


class PivotSidebarTestApp(App):
    """Test app to verify pivot sidebar."""

    CSS = """
    Screen {
        background: $surface;
        layers: base overlay;
    }

    .sidebar {
        height: 100%;
        background: $panel-darken-1;
        border-right: solid $accent;
        opacity: 95%;
        padding: 1;
    }

    #pivot_sidebar {
        layer: overlay;
        dock: left;
        width: 40%;
        display: block;
    }

    #pivot_sidebar.visible {
        display: block;
    }

    #pivot_sidebar.hidden {
        display: none;
    }

    .sidebar-title {
        text-style: bold;
        padding: 1;
        background: $accent;
        color: $text;
        margin-bottom: 1;
    }

    .form-group {
        padding: 1 0;
        margin: 1 0;
    }

    .form-label {
        margin-bottom: 0;
        text-style: bold;
        color: $text;
    }

    .button-row {
        padding: 1 0;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    .button-row Button {
        margin: 0 1;
    }

    .value-section-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        padding: 1 0;
        margin: 1 0;
    }

    .value-section {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
        background: $panel-darken-2;
        height: auto;
    }

    .value-section-buttons {
        padding: 1 0;
        height: auto;
        align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the test app."""
        # Create pivot sidebar with empty columns (will set later)
        sidebar = PivotSidebar(columns=[])
        yield sidebar
        yield Footer()

    def on_mount(self) -> None:
        """Show the sidebar when app mounts."""
        # Set columns first, then show
        test_columns = ["sales", "quantity", "price", "category", "region"]
        sidebar = self.query_one(PivotSidebar)
        sidebar.columns = test_columns
        sidebar.show()


if __name__ == "__main__":
    app = PivotSidebarTestApp()
    app.run()
