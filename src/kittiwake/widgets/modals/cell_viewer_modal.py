"""Modal for viewing full cell content."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class CellViewerModal(ModalScreen):
    """Modal to display full cell content."""

    def __init__(self, cell_value: str, column_name: str, row_index: int, **kwargs):
        """Initialize cell viewer modal.

        Args:
            cell_value: Full cell content to display
            column_name: Name of the column
            row_index: Row number

        """
        super().__init__(**kwargs)
        self.cell_value = cell_value
        self.column_name = column_name
        self.row_index = row_index

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="cell_viewer"):
            yield Static(
                f"Column: {self.column_name}  |  Row: {self.row_index}",
                id="header",
                classes="header-label",
            )
            with Horizontal(id="content_container"):
                yield Static(self.cell_value, id="cell_content", classes="scrollable")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_btn":
            self.app.pop_screen()
