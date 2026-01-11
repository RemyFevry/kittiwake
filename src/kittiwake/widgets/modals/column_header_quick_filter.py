"""Quick filter modal triggered from column header clicks."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from ...services.type_detector import detect_column_type_category
from ...utils.type_colors import get_operators_for_type


class ColumnHeaderQuickFilter(ModalScreen[dict | None]):
    """Modal screen for quick filter from column header.

    Features:
    - Pre-populated column (from header click)
    - Type-filtered operators (based on column type)
    - Value text input
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)

    Returns dict with column/operator/value on Apply, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        column_name: str,
        column_dtype: str,
        **kwargs,
    ):
        """Initialize quick filter modal.

        Args:
            column_name: Name of the column to filter
            column_dtype: Narwhals dtype string for the column

        """
        super().__init__(**kwargs)
        self.column_name = column_name
        self.column_dtype = column_dtype

        # Detect type and get appropriate operators
        self.type_category = detect_column_type_category(column_dtype)
        self.operators = get_operators_for_type(self.type_category)

    def compose(self) -> ComposeResult:
        """Create quick filter modal content."""
        with Container(id="filter_dialog"):
            yield Label(f"Quick Filter: {self.column_name}", id="filter_title")

            with Vertical(id="filter_form"):
                # Column info (read-only display)
                yield Label("Column:", classes="filter_label")
                yield Label(
                    f"{self.column_name} ({self.column_dtype})",
                    id="column_display",
                    classes="filter_value_display",
                )

                # Operator selector (type-filtered)
                yield Label("Operator:", classes="filter_label")
                yield Select(
                    options=[(op, op) for op in self.operators],
                    prompt="Select operator",
                    id="operator_select",
                    allow_blank=False,
                )

                # Value input
                yield Label("Value:", classes="filter_label")
                yield Input(
                    placeholder=self._get_placeholder_for_type(),
                    id="value_input",
                )

            # Buttons
            with Horizontal(id="filter_buttons"):
                yield Button("Apply", variant="primary", id="apply_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def _get_placeholder_for_type(self) -> str:
        """Get appropriate placeholder text based on column type.

        Returns:
            Placeholder text for the value input field

        """
        placeholders = {
            "numeric": "Enter number (e.g., 42, 3.14)",
            "text": "Enter text to match",
            "date": "Enter date (e.g., 2024-01-15)",
            "boolean": "Value not needed for boolean filters",
            "unknown": "Enter value",
        }
        return placeholders.get(self.type_category, "Enter value")

    def on_mount(self) -> None:
        """Focus the operator select when modal opens."""
        self.query_one("#operator_select", Select).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_filter()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _apply_filter(self) -> None:
        """Validate inputs and return filter operation."""
        operator_select = self.query_one("#operator_select", Select)
        value_input = self.query_one("#value_input", Input)

        # Get selected values
        operator = operator_select.value
        value = value_input.value.strip()

        # Validation - check if operator is selected
        if not operator:
            self.notify("Please select an operator", severity="warning")
            return

        # For boolean operators, value may not be required
        if self.type_category == "boolean":
            # Boolean operators like "is true", "is false" don't need a value
            if operator in ["is true", "is false", "is null", "is not null"]:
                value = ""  # No value needed
        else:
            # For other types, value is required
            if not value:
                self.notify("Please enter a value", severity="warning")
                return

        # Return operation dict
        operation = {
            "column": self.column_name,
            "operator": operator,
            "value": value,
            "type_category": self.type_category,
        }

        self.dismiss(operation)

    def action_cancel(self) -> None:
        """Cancel the quick filter modal."""
        self.dismiss(None)
