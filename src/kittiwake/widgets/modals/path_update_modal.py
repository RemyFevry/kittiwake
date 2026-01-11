"""Path update modal for handling missing dataset files."""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

if TYPE_CHECKING:
    from ...app import KittiwakeApp


class PathUpdateModal(ModalScreen[str | None]):
    """Modal screen for updating missing dataset path.

    Features:
    - Displays original (missing) path
    - Input for new path
    - Browse/Update and Skip buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Path validation

    Returns new path string on Update, None on Skip/Cancel.
    """

    BINDINGS = [
        ("escape", "skip", "Skip"),
    ]

    def __init__(
        self,
        analysis_name: str,
        original_path: str,
        **kwargs,
    ):
        """Initialize path update modal.

        Args:
            analysis_name: Name of the analysis being loaded
            original_path: The original (missing) dataset path

        """
        super().__init__(**kwargs)
        self.analysis_name = analysis_name
        self.original_path = original_path

    @property
    def kittiwake_app(self) -> "KittiwakeApp":
        """Return the app instance with proper typing."""
        from ...app import KittiwakeApp  # noqa: F401

        return self.app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Create path update modal content."""
        with Container(id="path_update_dialog"):
            yield Static("Dataset File Not Found", id="path_update_title")

            with Vertical(id="path_update_form"):
                # Analysis name
                yield Label(
                    f"Analysis: {self.analysis_name}", classes="path_update_info"
                )

                # Original path
                yield Label("Original path (not found):", classes="path_update_label")
                yield Static(
                    self.original_path,
                    id="original_path_display",
                    classes="path_display",
                )

                # New path input
                yield Label(
                    "Enter new path to dataset file:", classes="path_update_label"
                )
                yield Input(
                    placeholder="path/to/dataset.csv",
                    id="new_path_input",
                    value=self.original_path,
                )

                yield Label(
                    "Tip: Enter full path or relative path to the file",
                    classes="path_update_hint",
                )

            # Buttons
            with Horizontal(id="path_update_buttons"):
                yield Button("Update Path", variant="primary", id="update_button")
                yield Button("Skip Loading", variant="default", id="skip_button")

    def on_mount(self) -> None:
        """Focus new path input when modal opens."""
        self.query_one("#new_path_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "update_button":
            self._update_path()
        elif event.button.id == "skip_button":
            self.action_skip()

    def _update_path(self) -> None:
        """Validate new path and return it."""
        new_path_input = self.query_one("#new_path_input", Input)
        new_path = new_path_input.value.strip()

        # Validation
        if not new_path:
            self.notify("Please enter a path to the dataset file", severity="warning")
            new_path_input.focus()
            return

        # Check if file exists
        try:
            path_obj = Path(new_path)

            if not path_obj.exists():
                self.notify(
                    f"File not found: {new_path}. Please check the path and try again.",
                    severity="warning",
                )
                new_path_input.focus()
                return

            if not path_obj.is_file():
                self.notify(f"Path is not a file: {new_path}", severity="warning")
                new_path_input.focus()
                return

        except Exception as e:
            self.kittiwake_app.notify_error(f"Invalid path: {e}")
            new_path_input.focus()
            return

        # Return new path
        self.dismiss(new_path)

    def action_skip(self) -> None:
        """Skip loading and close modal without returning path."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in path input field."""
        if event.input.id == "new_path_input":
            self._update_path()


# CSS for path update modal
PATH_UPDATE_MODAL_CSS = """
PathUpdateModal {
    align: center middle;
}

#path_update_dialog {
    width: 80;
    height: auto;
    background: $surface;
    border: thick $warning;
    padding: 1 2;
}

#path_update_title {
    text-align: center;
    text-style: bold;
    background: $warning;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#path_update_form {
    height: auto;
    padding: 1 0;
}

.path_update_info {
    margin-bottom: 1;
    color: $text;
    text-style: italic;
}

.path_update_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

.path_display {
    margin-bottom: 1;
    padding: 1;
    background: $panel-darken-1;
    color: $text-muted;
    text-style: italic;
}

#new_path_input {
    width: 100%;
    margin-bottom: 0;
}

.path_update_hint {
    margin-top: 0;
    margin-bottom: 1;
    color: $text-muted;
    text-style: italic;
}

#path_update_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#path_update_buttons Button {
    margin: 0 1;
}
"""
