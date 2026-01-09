"""Save analysis modal widget for saving operation history."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea


class SaveAnalysisModal(ModalScreen[dict | None]):
    """Modal screen for saving analysis with name and description.

    Features:
    - Name input (required, 1-100 characters)
    - Description textarea (optional, max 500 characters)
    - Save and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Validation for name constraints

    Returns dict with name/description on Save, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        default_name: str = "",
        default_description: str = "",
        **kwargs,
    ):
        """Initialize save analysis modal.

        Args:
            default_name: Default name to prefill (e.g., for updates)
            default_description: Default description to prefill
        """
        super().__init__(**kwargs)
        self.default_name = default_name
        self.default_description = default_description

    def compose(self) -> ComposeResult:
        """Create save analysis modal content."""
        with Container(id="save_analysis_dialog"):
            yield Label("Save Analysis", id="save_analysis_title")

            with Vertical(id="save_analysis_form"):
                # Name input
                yield Label("Name (required, 1-100 chars):", classes="save_analysis_label")
                yield Input(
                    placeholder="Enter analysis name",
                    id="name_input",
                    value=self.default_name,
                    max_length=100,
                )

                # Description textarea
                yield Label("Description (optional, max 500 chars):", classes="save_analysis_label")
                yield TextArea(
                    text=self.default_description,
                    id="description_input",
                    language="markdown",
                )

            # Buttons
            with Horizontal(id="save_analysis_buttons"):
                yield Button("Save", variant="primary", id="save_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus name input when modal opens."""
        self.query_one("#name_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "save_button":
            self._save_analysis()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _save_analysis(self) -> None:
        """Validate inputs and return analysis data."""
        name_input = self.query_one("#name_input", Input)
        description_input = self.query_one("#description_input", TextArea)

        # Get values
        name = name_input.value.strip()
        description = description_input.text.strip()

        # Validation
        if not name:
            self.notify("Please enter an analysis name", severity="warning")
            name_input.focus()
            return

        if len(name) < 1 or len(name) > 100:
            self.notify("Name must be 1-100 characters", severity="warning")
            name_input.focus()
            return

        # Check for invalid characters (no path separators)
        if "/" in name or "\\" in name:
            self.notify("Name cannot contain path separators (/ or \\)", severity="warning")
            name_input.focus()
            return

        if len(description) > 500:
            self.notify("Description must be max 500 characters", severity="warning")
            description_input.focus()
            return

        # Return analysis data
        analysis_data = {
            "name": name,
            "description": description if description else None,
        }

        self.dismiss(analysis_data)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning data."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in name input field."""
        if event.input.id == "name_input":
            # Move focus to description or save
            description_input = self.query_one("#description_input", TextArea)
            description_input.focus()


# CSS for save analysis modal
SAVE_ANALYSIS_MODAL_CSS = """
SaveAnalysisModal {
    align: center middle;
}

#save_analysis_dialog {
    width: 70;
    height: auto;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#save_analysis_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#save_analysis_form {
    height: auto;
    padding: 1 0;
}

.save_analysis_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

#name_input {
    width: 100%;
    margin-bottom: 1;
}

#description_input {
    width: 100%;
    height: 8;
    margin-bottom: 1;
}

#save_analysis_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#save_analysis_buttons Button {
    margin: 0 1;
}
"""
