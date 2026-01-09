"""Help overlay widget showing keyboard shortcuts."""

from textual.app import ComposeResult
from textual.containers import Container, Grid, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label, Static

from ..utils.keybindings import KeybindingsRegistry


class HelpOverlay(ModalScreen):
    """Modal overlay showing keyboard shortcuts and help.

    Features:
    - Context-aware shortcuts (changes based on screen)
    - Grouped by category
    - Press ? to toggle, Escape to close
    - Centered modal with semi-transparent background
    """

    BINDINGS = [
        ("escape", "dismiss", "Close help"),
        ("?", "dismiss", "Close help"),
    ]

    def __init__(
        self,
        screen_name: str = "main",
        keybindings: KeybindingsRegistry | None = None,
        **kwargs,
    ):
        """Initialize help overlay.

        Args:
            screen_name: Name of screen to show help for
            keybindings: KeybindingsRegistry instance
        """
        super().__init__(**kwargs)
        self.screen_name = screen_name
        self.keybindings = keybindings or KeybindingsRegistry()

    def compose(self) -> ComposeResult:
        """Create help overlay content."""
        with Container(id="help_dialog"):
            yield Static("Keyboard Shortcuts", id="help_title")

            with VerticalScroll(id="help_content"):
                # Navigation section
                yield Label("Navigation", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("Arrow Keys", classes="help_key")
                    yield Label("Navigate table cells", classes="help_desc")
                    yield Label("Page Up/Down", classes="help_key")
                    yield Label("Navigate table pages", classes="help_desc")
                    yield Label("Tab", classes="help_key")
                    yield Label("Next dataset", classes="help_desc")
                    yield Label("Shift+Tab", classes="help_key")
                    yield Label("Previous dataset", classes="help_desc")

                # Data Operations section
                yield Label("Data Operations", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("F", classes="help_key")
                    yield Label("Filter rows", classes="help_desc")
                    yield Label("A", classes="help_key")
                    yield Label("Aggregate (group by)", classes="help_desc")
                    yield Label("P", classes="help_key")
                    yield Label("Pivot table", classes="help_desc")
                    yield Label("S", classes="help_key")
                    yield Label("Sort", classes="help_desc")
                    yield Label("J", classes="help_key")
                    yield Label("Join datasets", classes="help_desc")
                    yield Label("U", classes="help_key")
                    yield Label("Unique values", classes="help_desc")

                # Column Operations section
                yield Label("Column Operations", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("C", classes="help_key")
                    yield Label("Select columns", classes="help_desc")
                    yield Label("D", classes="help_key")
                    yield Label("Drop columns", classes="help_desc")
                    yield Label("R", classes="help_key")
                    yield Label("Rename columns", classes="help_desc")
                    yield Label("W", classes="help_key")
                    yield Label("Add/transform columns", classes="help_desc")

                # Null Handling section
                yield Label("Null Handling", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("N, F", classes="help_key")
                    yield Label("Fill null values", classes="help_desc")
                    yield Label("N, D", classes="help_key")
                    yield Label("Drop null values", classes="help_desc")

                # View Controls section
                yield Label("View Controls", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("H", classes="help_key")
                    yield Label("Show first N rows", classes="help_desc")
                    yield Label("T", classes="help_key")
                    yield Label("Show last N rows", classes="help_desc")
                    yield Label("M", classes="help_key")
                    yield Label("Sample random rows", classes="help_desc")
                    yield Label("Ctrl+P", classes="help_key")
                    yield Label("Toggle split pane", classes="help_desc")

                # History section
                yield Label("History", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("Ctrl+Z", classes="help_key")
                    yield Label("Undo operation", classes="help_desc")
                    yield Label("Ctrl+Shift+Z", classes="help_key")
                    yield Label("Redo operation", classes="help_desc")

                # Session Management section
                yield Label("Session Management", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("Ctrl+S", classes="help_key")
                    yield Label("Save analysis", classes="help_desc")
                    yield Label("Ctrl+W", classes="help_key")
                    yield Label("Close dataset", classes="help_desc")
                    yield Label("Ctrl+C", classes="help_key")
                    yield Label("Quit application", classes="help_desc")

                # General section
                yield Label("General", classes="help_section_title")
                with Grid(classes="help_section"):
                    yield Label("?", classes="help_key")
                    yield Label("Toggle this help", classes="help_desc")
                    yield Label("Q", classes="help_key")
                    yield Label("Quit screen", classes="help_desc")
                    yield Label("Escape", classes="help_key")
                    yield Label("Close dialog/cancel", classes="help_desc")

            yield Static("Press ? or Escape to close", id="help_footer")

    def action_dismiss(self) -> None:
        """Dismiss the help overlay."""
        self.app.pop_screen()


# CSS for help overlay
HELP_OVERLAY_CSS = """
HelpOverlay {
    align: center middle;
}

#help_dialog {
    width: 80;
    height: 35;
    background: $surface;
    border: thick $primary;
    padding: 1;
}

#help_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#help_content {
    height: 28;
    border: none;
    padding: 1;
}

.help_section_title {
    text-style: bold;
    color: $secondary;
    margin-top: 1;
    margin-bottom: 1;
}

.help_section {
    grid-size: 2;
    grid-columns: 1fr 2fr;
    grid-gutter: 1;
    margin-bottom: 1;
}

.help_key {
    text-style: bold;
    color: $accent;
}

.help_desc {
    color: $text;
}

#help_footer {
    text-align: center;
    text-style: italic;
    color: $text-muted;
    margin-top: 1;
}
"""
