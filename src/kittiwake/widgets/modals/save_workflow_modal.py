"""Save workflow modal widget for saving operation workflows."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, TextArea

from kittiwake.utils.security import InputValidator, SecurityError


class WorkflowSaveRequested:
    """Message emitted when workflow save is requested.

    Attributes:
        name: Workflow name
        description: Optional workflow description
        include_schema: Whether to include current dataset schema

    """

    def __init__(self, name: str, description: str | None, include_schema: bool):
        """Initialize workflow save request message.

        Args:
            name: Workflow name
            description: Optional workflow description
            include_schema: Whether to include current dataset schema

        """
        self.name = name
        self.description = description
        self.include_schema = include_schema


class SaveWorkflowModal(ModalScreen[dict | None]):
    """Modal screen for saving operation workflow with name, description, and schema option.

    Features:
    - Name input (required, 1-100 characters, alphanumeric + _ and -)
    - Description textarea (optional, max 500 characters)
    - Checkbox: "Include current dataset schema" (default: checked)
    - Save and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Input validation for name constraints

    Returns dict with name/description/include_schema on Save, None on Cancel.

    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        default_name: str = "",
        default_description: str = "",
        default_include_schema: bool = True,
        **kwargs,
    ):
        """Initialize save workflow modal.

        Args:
            default_name: Default name to prefill (e.g., for updates)
            default_description: Default description to prefill
            default_include_schema: Default checkbox state for schema inclusion

        """
        super().__init__(**kwargs)
        self.default_name = default_name
        self.default_description = default_description
        self.default_include_schema = default_include_schema

    def compose(self) -> ComposeResult:
        """Create save workflow modal content."""
        with Container(id="save_workflow_dialog"):
            yield Label("Save Operation Workflow", id="save_workflow_title")

            with Vertical(id="save_workflow_form"):
                # Name input
                yield Label(
                    "Name (required, 1-100 chars, alphanumeric + _ -):",
                    classes="save_workflow_label",
                )
                yield Input(
                    placeholder="Enter workflow name",
                    id="name_input",
                    value=self.default_name,
                    max_length=100,
                )

                # Description textarea
                yield Label(
                    "Description (optional, max 500 chars):",
                    classes="save_workflow_label",
                )
                yield TextArea(
                    text=self.default_description,
                    id="description_input",
                    language="markdown",
                )

                # Schema inclusion checkbox
                yield Checkbox(
                    "Include current dataset schema",
                    value=self.default_include_schema,
                    id="include_schema_checkbox",
                )

            # Buttons
            with Horizontal(id="save_workflow_buttons"):
                yield Button("Save", variant="primary", id="save_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus name input when modal opens."""
        self.query_one("#name_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event

        """
        if event.button.id == "save_button":
            self._save_workflow()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _save_workflow(self) -> None:
        """Validate inputs and return workflow data."""
        name_input = self.query_one("#name_input", Input)
        description_input = self.query_one("#description_input", TextArea)
        include_schema_checkbox = self.query_one("#include_schema_checkbox", Checkbox)

        # Get values
        name = name_input.value.strip()
        description = description_input.text.strip()
        include_schema = include_schema_checkbox.value

        # Validation using InputValidator
        try:
            # Validate workflow name
            if not name:
                self.notify("Please enter a workflow name", severity="warning")
                name_input.focus()
                return

            # Use custom validation for workflow name
            if len(name) < 1 or len(name) > 100:
                self.notify(
                    "Workflow name must be 1-100 characters", severity="warning"
                )
                name_input.focus()
                return

            # Check for valid characters (alphanumeric, underscore, hyphen)
            import re

            if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
                self.notify(
                    "Workflow name can only contain letters, numbers, underscore (_), and hyphen (-)",
                    severity="warning",
                )
                name_input.focus()
                return

            # Validate description length
            if len(description) > 500:
                self.notify(
                    "Description must be max 500 characters", severity="warning"
                )
                description_input.focus()
                return

            # Sanitize text inputs for safety
            description = InputValidator.sanitize_text_input(
                description, max_length=500
            )

        except SecurityError as e:
            self.notify(f"Validation error: {e}", severity="error")
            name_input.focus()
            return

        # Return workflow data
        workflow_data = {
            "name": name,
            "description": description if description else None,
            "include_schema": include_schema,
        }

        self.dismiss(workflow_data)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning data."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in name input field.

        Args:
            event: Input submitted event

        """
        if event.input.id == "name_input":
            # Move focus to description
            description_input = self.query_one("#description_input", TextArea)
            description_input.focus()


# CSS for save workflow modal
SAVE_WORKFLOW_MODAL_CSS = """
SaveWorkflowModal {
    align: center middle;
}

#save_workflow_dialog {
    width: 70;
    height: auto;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#save_workflow_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#save_workflow_form {
    height: auto;
    padding: 1 0;
}

.save_workflow_label {
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

#include_schema_checkbox {
    margin-top: 1;
    margin-bottom: 1;
}

#save_workflow_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#save_workflow_buttons Button {
    margin: 0 1;
}
"""
