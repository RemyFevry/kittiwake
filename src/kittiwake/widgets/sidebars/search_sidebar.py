"""Search sidebar for full-text search across all columns (left sidebar, overlay)."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Input, Label


class SearchSidebar(VerticalScroll):
    """Left sidebar for search configuration (overlay, 30% width).

    Features:
    - Text input field for search query
    - Apply and Cancel buttons
    - Keyboard-navigable (Tab, Enter, Esc)
    - Enter key in input field triggers Apply
    - Callback-based result handling

    Usage:
        sidebar.callback = lambda params: handle_search(params)
        sidebar.show()
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]

    def __init__(self, **kwargs):
        """Initialize search sidebar."""
        super().__init__(id="search_sidebar", classes="sidebar hidden", **kwargs)
        self.callback: Callable[[dict], None] | None = None

    def compose(self) -> ComposeResult:
        """Create search sidebar content."""
        yield Label("Search Data", classes="sidebar-title")

        with Container(classes="form-group"):
            yield Label("Search query (searches across all columns):", classes="form-label")
            yield Input(
                placeholder="Search text...",
                id="search_query",
            )

        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus search input when sidebar mounts."""
        self.query_one("#search_query", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_search()
        elif event.button.id == "cancel_button":
            self.action_dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field to trigger Apply."""
        if event.input.id == "search_query":
            self._apply_search()

    def _apply_search(self) -> None:
        """Apply search and trigger callback."""
        query_input = self.query_one("#search_query", Input)
        query_text = query_input.value.strip()

        # Allow empty query (clears search)
        params = {
            "query": query_text,
        }

        # Trigger callback
        if self.callback:
            self.callback(params)

        # Dismiss sidebar
        self.action_dismiss()

    def action_dismiss(self) -> None:
        """Hide the sidebar and return focus to main table."""
        self.add_class("hidden")
        self.remove_class("visible")

        # Try to focus data table
        try:
            data_table = self.app.query_one("#dataset_table_left")
            data_table.focus()
        except Exception:
            pass

    def show(self) -> None:
        """Show the sidebar with visible class."""
        self.remove_class("hidden")
        self.add_class("visible")
        self.focus()
