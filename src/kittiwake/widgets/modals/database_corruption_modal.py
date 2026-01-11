"""Database corruption recovery modal for handling DuckDB errors."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

if TYPE_CHECKING:
    from ...app import KittiwakeApp


class DatabaseCorruptionModal(ModalScreen[bool | None]):
    """Modal screen for handling database corruption errors.

    Features:
    - Displays corruption error message
    - Shows warning about data loss
    - Reinitialize and Cancel options
    - Fully keyboard-navigable (Tab, Enter, Esc)

    Returns True to reinitialize database, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        error_message: str,
        db_path: str,
        **kwargs,
    ):
        """Initialize corruption recovery modal.

        Args:
            error_message: The error that triggered this modal
            db_path: Path to the corrupted database file

        """
        super().__init__(**kwargs)
        self.error_message = error_message
        self.db_path = db_path

    @property
    def kittiwake_app(self) -> "KittiwakeApp":
        """Return the app instance with proper typing."""
        from ...app import KittiwakeApp  # noqa: F401

        return self.app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Create corruption recovery modal content."""
        with Container(id="corruption_dialog"):
            yield Static("Database Error", id="corruption_title")

            with Vertical(id="corruption_form"):
                yield Label(
                    "The analysis database encountered an error:",
                    classes="corruption_label",
                )

                yield Static(
                    self.error_message,
                    id="corruption_error_display",
                    classes="error_display",
                )

                yield Static("Database location:", classes="corruption_label")
                yield Static(
                    self.db_path, id="corruption_db_path", classes="path_display"
                )

                yield Static(
                    "⚠️ WARNING: Reinitializing the database will DELETE ALL saved analyses.",
                    classes="corruption_warning",
                )
                yield Static(
                    "This action cannot be undone.", classes="corruption_warning"
                )

            # Buttons
            with Horizontal(id="corruption_buttons"):
                yield Button(
                    "Reinitialize Database", variant="error", id="reinit_button"
                )
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "reinit_button":
            self._confirm_reinitialize()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _confirm_reinitialize(self) -> None:
        """Confirm reinitialize and return True."""

        # Show additional confirmation
        def on_confirmed(confirmed: bool) -> None:
            if confirmed:
                self.dismiss(True)

        # For now, just proceed - could add another confirmation modal
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning True."""
        self.dismiss(None)


# CSS for corruption modal
CORRUPTION_MODAL_CSS = """
DatabaseCorruptionModal {
    align: center middle;
}

#corruption_dialog {
    width: 80;
    height: auto;
    background: $surface;
    border: thick $error;
    padding: 1 2;
}

#corruption_title {
    text-align: center;
    text-style: bold;
    background: $error;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#corruption_form {
    height: auto;
    padding: 1 0;
}

.corruption_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

.error_display {
    margin: 0 0 1 0;
    padding: 1;
    background: $panel-darken-1;
    color: $error;
    text-style: italic;
}

.path_display {
    margin: 0 0 1 0;
    padding: 1;
    background: $panel-darken-1;
    color: $text-muted;
    text-style: italic;
}

.corruption_warning {
    color: $warning;
    text-style: bold;
    margin: 1 0 0 0;
}

#corruption_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#corruption_buttons Button {
    margin: 0 1;
}
"""
