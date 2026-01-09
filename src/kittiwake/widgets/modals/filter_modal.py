"""Filter modal widget for building filter operations."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select


class FilterModal(ModalScreen[dict | None]):
    """Modal screen for building filter operations.

    Features:
    - Column dropdown selector (populated with dataset columns)
    - Operator dropdown (=, !=, >, <, >=, <=, contains)
    - Value text input
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)

    Returns dict with column/operator/value on Apply, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    # Operator choices (display, value) format for Select widget
    OPERATORS = [
        ("Equals (=)", "=="),
        ("Not Equals (!=)", "!="),
        ("Greater Than (>)", ">"),
        ("Less Than (<)", "<"),
        ("Greater or Equal (>=)", ">="),
        ("Less or Equal (<=)", "<="),
        ("Contains", "contains"),
    ]

    def __init__(
        self,
        columns: list[str],
        **kwargs,
    ):
        """Initialize filter modal.

        Args:
            columns: List of column names for the dropdown
        """
        super().__init__(**kwargs)
        self.columns = columns

    def compose(self) -> ComposeResult:
        """Create filter modal content."""
        with Container(id="filter_dialog"):
            yield Label("Filter Operation", id="filter_title")

            with Vertical(id="filter_form"):
                # Column selector
                yield Label("Column:", classes="filter_label")
                yield Select(
                    options=[(col, col) for col in self.columns],
                    prompt="Select column",
                    id="column_select",
                    allow_blank=False,
                )

                # Operator selector
                yield Label("Operator:", classes="filter_label")
                yield Select(
                    options=self.OPERATORS,
                    prompt="Select operator",
                    id="operator_select",
                    allow_blank=False,
                )

                # Value input
                yield Label("Value:", classes="filter_label")
                yield Input(
                    placeholder="Enter value to filter by",
                    id="value_input",
                )

            # Buttons
            with Horizontal(id="filter_buttons"):
                yield Button("Apply", variant="primary", id="apply_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_filter()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _apply_filter(self) -> None:
        """Validate inputs and return filter operation."""
        column_select = self.query_one("#column_select", Select)
        operator_select = self.query_one("#operator_select", Select)
        value_input = self.query_one("#value_input", Input)

        # Get selected values
        column = column_select.value
        operator = operator_select.value
        value = value_input.value.strip()

        # Validation - check if values are selected/entered
        if not column:
            self.notify("Please select a column", severity="warning")
            return

        if not operator:
            self.notify("Please select an operator", severity="warning")
            return

        if not value:
            self.notify("Please enter a value", severity="warning")
            return

        # Return operation dict (code generation will be in T035)
        operation = {
            "column": column,
            "operator": operator,
            "value": value,
        }

        self.dismiss(operation)

    def _build_filter_operation(
        self, filter_dict: dict
    ) -> tuple[str, str, dict]:
        """Generate narwhals filter operation code from filter dict.

        Args:
            filter_dict: Dict with keys 'column', 'operator', 'value'

        Returns:
            Tuple of (code_string, display_string, params_dict)
            - code: Executable narwhals expression (e.g., 'df.filter(nw.col("age") > 25)')
            - display: Human-readable string (e.g., "Filter: age > 25")
            - params: Original filter_dict for editing later
        """
        column = filter_dict["column"]
        operator = filter_dict["operator"]
        value = filter_dict.get("value", "")

        # Generate code string based on operator
        if operator == "contains":
            # String contains operation - case-insensitive
            value_lower = value.lower()
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.contains("{value_lower}"))'
            display = f"Filter: {column} contains {value}"
            
        elif operator == "not contains":
            # String not contains operation - case-insensitive
            value_lower = value.lower()
            code = f'df = df.filter(~nw.col("{column}").str.to_lowercase().str.contains("{value_lower}"))'
            display = f"Filter: {column} not contains {value}"
            
        elif operator == "starts with":
            # String starts with operation - case-insensitive
            value_lower = value.lower()
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.starts_with("{value_lower}"))'
            display = f"Filter: {column} starts with {value}"
            
        elif operator == "ends with":
            # String ends with operation - case-insensitive
            value_lower = value.lower()
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.ends_with("{value_lower}"))'
            display = f"Filter: {column} ends with {value}"
            
        elif operator == "is true":
            # Boolean true check
            code = f'df = df.filter(nw.col("{column}") == True)'
            display = f"Filter: {column} is true"
            
        elif operator == "is false":
            # Boolean false check
            code = f'df = df.filter(nw.col("{column}") == False)'
            display = f"Filter: {column} is false"
            
        elif operator == "is null":
            # Null check
            code = f'df = df.filter(nw.col("{column}").is_null())'
            display = f"Filter: {column} is null"
            
        elif operator == "is not null":
            # Not null check
            code = f'df = df.filter(~nw.col("{column}").is_null())'
            display = f"Filter: {column} is not null"
            
        else:
            # Comparison operators (==, !=, >, <, >=, <=)
            # Try to detect numeric values
            try:
                numeric_value = float(value)
                # Use numeric value without quotes
                code = f'df = df.filter(nw.col("{column}") {operator} {numeric_value})'
            except ValueError:
                # String value - use quotes and escape any existing quotes
                escaped_value = value.replace('"', '\\"')
                code = f'df = df.filter(nw.col("{column}") {operator} "{escaped_value}")'
            
            # Display string
            display = f"Filter: {column} {operator} {value}"

        # Return params for potential editing later
        params = filter_dict.copy()

        return (code, display, params)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning data."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in value input field."""
        if event.input.id == "value_input":
            self._apply_filter()


# CSS for filter modal
FILTER_MODAL_CSS = """
FilterModal {
    align: center middle;
}

#filter_dialog {
    width: 60;
    height: auto;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#filter_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#filter_form {
    height: auto;
    padding: 1 0;
}

.filter_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

#column_select, #operator_select {
    width: 100%;
    margin-bottom: 1;
}

#value_input {
    width: 100%;
    margin-bottom: 1;
}

#filter_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#filter_buttons Button {
    margin: 0 1;
}
"""
