"""Filter sidebar for building filter operations (left sidebar, overlay)."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Input, Label, Select


class FilterSidebar(VerticalScroll):
    """Left sidebar for filter configuration (overlay, 30% width).

    Features:
    - Column dropdown selector (populated with dataset columns)
    - Operator dropdown (=, !=, >, <, >=, <=, contains)
    - Value text input
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Callback-based result handling

    Usage:
        sidebar.columns = ["age", "name"]
        sidebar.callback = lambda params: handle_filter(params)
        sidebar.show()
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
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

    def __init__(self, columns: list[str] | None = None, **kwargs):
        """Initialize filter sidebar.

        Args:
            columns: List of column names for the dropdown

        """
        super().__init__(id="filter_sidebar", classes="sidebar hidden", **kwargs)
        self.columns: list[str] = columns or []
        self.callback: Callable[[dict], None] | None = None

    def compose(self) -> ComposeResult:
        """Create filter sidebar content."""
        yield Label("Filter Configuration", classes="sidebar-title")

        with Container(classes="form-group"):
            yield Label("Column:", classes="form-label")
            yield Select(
                options=[(col, col) for col in self.columns] if self.columns else [],
                prompt="Select column",
                id="column_select",
                allow_blank=True,
            )

        with Container(classes="form-group"):
            yield Label("Operator:", classes="form-label")
            yield Select(
                options=self.OPERATORS,
                prompt="Select operator",
                id="operator_select",
                allow_blank=False,
            )

        with Container(classes="form-group"):
            yield Label("Value:", classes="form-label")
            yield Input(
                placeholder="Enter value to filter by",
                id="value_input",
            )

        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus first input when sidebar mounts."""
        if self.columns:
            self.query_one("#column_select", Select).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_filter()
        elif event.button.id == "cancel_button":
            self.action_dismiss()

    def _apply_filter(self) -> None:
        """Validate inputs and trigger callback."""
        column_select = self.query_one("#column_select", Select)
        operator_select = self.query_one("#operator_select", Select)
        value_input = self.query_one("#value_input", Input)

        # Get selected values
        column = column_select.value
        operator = operator_select.value
        value = value_input.value.strip()

        # Validation - check if values are selected/entered
        if not column or column == Select.BLANK:
            self.app.notify("Please select a column", severity="warning")
            column_select.focus()
            return

        if not operator or operator == Select.BLANK:
            self.app.notify("Please select an operator", severity="warning")
            operator_select.focus()
            return

        if not value:
            self.app.notify("Please enter a value", severity="warning")
            value_input.focus()
            return

        # Build filter params
        params = {
            "column": column,
            "operator": operator,
            "value": value,
        }

        # Trigger callback with params
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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in value input field."""
        if event.input.id == "value_input":
            self._apply_filter()

    def show(self) -> None:
        """Show the sidebar with visible class."""
        self.remove_class("hidden")
        self.add_class("visible")
        # Update columns if needed
        if self.columns:
            column_select = self.query_one("#column_select", Select)
            column_select.set_options([(col, col) for col in self.columns])
        self.focus()

    def update_columns(self, columns: list[str]) -> None:
        """Update available columns for filtering."""
        self.columns = columns
        if self.is_mounted:
            column_select = self.query_one("#column_select", Select)
            column_select.set_options([(col, col) for col in self.columns])
