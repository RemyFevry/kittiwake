"""Export modal widget for exporting analyses to various formats."""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Static

if TYPE_CHECKING:
    from ...app import KittiwakeApp


class ExportModal(ModalScreen[dict | None]):
    """Modal screen for exporting analysis to code formats.

    Features:
    - Format selector: marimo, Python script, Jupyter notebook
    - Output path input with default suggestions
    - Export and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Path validation

    Returns dict with format/path on Export, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    # Export format options
    EXPORT_FORMATS = {
        "marimo": {
            "label": "marimo Notebook (.py)",
            "extension": ".py",
            "description": "Interactive marimo notebook with reactive cells",
        },
        "python": {
            "label": "Python Script (.py)",
            "extension": ".py",
            "description": "Standalone Python script with narwhals code",
        },
        "jupyter": {
            "label": "Jupyter Notebook (.ipynb)",
            "extension": ".ipynb",
            "description": "Jupyter notebook with cells for each operation",
        },
    }

    def __init__(
        self,
        analysis_name: str = "analysis",
        default_format: str = "marimo",
        **kwargs,
    ):
        """Initialize export modal.

        Args:
            analysis_name: Name of the analysis for default filename
            default_format: Default format to select (marimo/python/jupyter)
        """
        super().__init__(**kwargs)
        self.analysis_name = analysis_name
        self.default_format = default_format if default_format in self.EXPORT_FORMATS else "marimo"

    @property
    def kittiwake_app(self) -> "KittiwakeApp":
        """Return the app instance with proper typing."""
        from ...app import KittiwakeApp  # noqa: F401
        return self.app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Create export modal content."""
        with Container(id="export_dialog"):
            yield Static("Export Analysis", id="export_title")

            with Vertical(id="export_form"):
                # Format selector
                yield Label("Select export format:", classes="export_label")

                with RadioSet(id="format_selector"):
                    for format_id, format_info in self.EXPORT_FORMATS.items():
                        yield RadioButton(
                            format_info["label"],
                            id=f"format_{format_id}",
                            value=format_id == self.default_format,
                        )

                # Format description
                yield Label("", id="format_description", classes="export_description")

                # Output path input
                yield Label("Output path:", classes="export_label")
                yield Input(
                    placeholder="path/to/output.py",
                    id="path_input",
                    value=self._get_default_path(self.default_format),
                )

                yield Label(
                    "Tip: Leave empty to export to current directory",
                    classes="export_hint"
                )

            # Buttons
            with Horizontal(id="export_buttons"):
                yield Button("Export", variant="primary", id="export_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Initialize modal state when mounted."""
        # Update description for default format
        self._update_format_description(self.default_format)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle format selection change."""
        if event.pressed and event.pressed.id:
            selected_format = event.pressed.id.replace("format_", "")

            # Update description
            self._update_format_description(selected_format)

            # Update default path
            path_input = self.query_one("#path_input", Input)
            path_input.value = self._get_default_path(selected_format)

    def _update_format_description(self, format_id: str) -> None:
        """Update format description label."""
        description_label = self.query_one("#format_description", Label)
        format_info = self.EXPORT_FORMATS.get(format_id, {})
        description_label.update(format_info.get("description", ""))

    def _get_default_path(self, format_id: str) -> str:
        """Get default output path for format."""
        format_info = self.EXPORT_FORMATS.get(format_id, {})
        extension = format_info.get("extension", ".py")

        # Sanitize analysis name for filename
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.analysis_name)
        safe_name = safe_name.lower()

        return f"{safe_name}{extension}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "export_button":
            self._export_analysis()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _export_analysis(self) -> None:
        """Validate inputs and return export data."""
        # Get selected format
        format_selector = self.query_one("#format_selector", RadioSet)
        selected_button = format_selector.pressed_button

        if not selected_button or not selected_button.id:
            self.notify("Please select an export format", severity="warning")
            return

        selected_format = selected_button.id.replace("format_", "")

        # Get output path
        path_input = self.query_one("#path_input", Input)
        output_path = path_input.value.strip()

        # Use default if empty
        if not output_path:
            output_path = self._get_default_path(selected_format)

        # Validate path
        try:
            path_obj = Path(output_path)

            # Check for valid parent directory
            parent = path_obj.parent
            if not parent.exists() and str(parent) != ".":
                self.notify(
                    f"Parent directory does not exist: {parent}",
                    severity="warning"
                )
                return

            # Warn if file exists (but don't block)
            if path_obj.exists():
                self.notify(
                    f"File already exists and will be overwritten: {output_path}",
                    severity="information",
                )

        except Exception as e:
            self.kittiwake_app.notify_error(f"Invalid path: {e}")
            return

        # Return export data
        export_data = {
            "format": selected_format,
            "path": output_path,
        }

        self.dismiss(export_data)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning data."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in path input field."""
        if event.input.id == "path_input":
            self._export_analysis()


# CSS for export modal
EXPORT_MODAL_CSS = """
ExportModal {
    align: center middle;
}

#export_dialog {
    width: 80;
    height: auto;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#export_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#export_form {
    height: auto;
    padding: 1 0;
}

.export_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

#format_selector {
    width: 100%;
    margin-bottom: 1;
    padding: 1;
}

#format_selector RadioButton {
    margin: 0 0 1 0;
}

.export_description {
    margin-bottom: 1;
    color: $text-muted;
    text-style: italic;
}

#path_input {
    width: 100%;
    margin-bottom: 0;
}

.export_hint {
    margin-top: 0;
    margin-bottom: 1;
    color: $text-muted;
    text-style: italic;
}

#export_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#export_buttons Button {
    margin: 0 1;
}
"""
