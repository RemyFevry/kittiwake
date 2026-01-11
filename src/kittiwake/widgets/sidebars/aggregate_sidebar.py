"""Aggregate sidebar for building aggregation operations (left sidebar, overlay)."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Checkbox, Label, Select


class AggregateSidebar(VerticalScroll):
    """Left sidebar for aggregation configuration (overlay, 30% width).

    Features:
    - Column dropdown selector for column to aggregate
    - Aggregation function checkboxes (count, sum, mean, median, min, max, std)
    - Optional group-by column selector
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Callback-based result handling

    Usage:
        sidebar.columns = ["age", "name", "salary"]
        sidebar.callback = lambda params: handle_aggregate(params)
        sidebar.show()
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]

    # Available aggregation functions
    AGG_FUNCTIONS = [
        ("count", "Count"),
        ("sum", "Sum"),
        ("mean", "Mean"),
        ("median", "Median"),
        ("min", "Min"),
        ("max", "Max"),
        ("std", "Std Dev"),
    ]

    def __init__(self, columns: list[str] | None = None, **kwargs):
        """Initialize aggregate sidebar.

        Args:
            columns: List of column names for the dropdown

        """
        super().__init__(id="aggregate_sidebar", classes="sidebar hidden", **kwargs)
        self.columns: list[str] = columns or []
        self.callback: Callable[[dict], None] | None = None

    def compose(self) -> ComposeResult:
        """Create aggregate sidebar content."""
        yield Label("Aggregate Configuration", classes="sidebar-title")

        with Container(classes="form-group"):
            yield Label("Column to aggregate:", classes="form-label")
            yield Select(
                options=[(col, col) for col in self.columns] if self.columns else [],
                prompt="Select column",
                id="agg_column_select",
                allow_blank=True,
            )

        with Container(classes="form-group"):
            yield Label("Aggregation functions:", classes="form-label")
            # Create checkboxes for each aggregation function
            for func_id, func_label in self.AGG_FUNCTIONS:
                yield Checkbox(
                    func_label,
                    id=f"agg_func_{func_id}",
                    classes="agg-function-checkbox",
                )

        with Container(classes="form-group"):
            yield Label("Group by (optional):", classes="form-label")
            yield Select(
                options=[("(None)", "")] + [(col, col) for col in self.columns]
                if self.columns
                else [("(None)", "")],
                prompt="Select group-by column",
                id="group_by_select",
                allow_blank=True,
            )

        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus first input when sidebar mounts."""
        if self.columns:
            self.query_one("#agg_column_select", Select).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_aggregate()
        elif event.button.id == "cancel_button":
            self.action_dismiss()

    def _apply_aggregate(self) -> None:
        """Validate inputs and trigger callback."""
        agg_column_select = self.query_one("#agg_column_select", Select)
        group_by_select = self.query_one("#group_by_select", Select)

        # Get selected column
        agg_column = agg_column_select.value

        # Validation - check if column is selected
        if not agg_column or agg_column == Select.BLANK:
            self.app.notify("Please select a column to aggregate", severity="warning")
            agg_column_select.focus()
            return

        # Get selected aggregation functions from checkboxes
        selected_funcs = []
        for func_id, _ in self.AGG_FUNCTIONS:
            checkbox = self.query_one(f"#agg_func_{func_id}", Checkbox)
            if checkbox.value:
                selected_funcs.append(func_id)

        # Validation - check if at least one function is selected
        if not selected_funcs:
            self.app.notify(
                "Please select at least one aggregation function", severity="warning"
            )
            return

        # Get group-by column (optional)
        group_by = group_by_select.value
        if group_by == Select.BLANK or not group_by:
            group_by = None

        # Build aggregate params
        params = {
            "agg_column": agg_column,
            "agg_functions": selected_funcs,
            "group_by": group_by,
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

    def show(self) -> None:
        """Show the sidebar with visible class."""
        self.remove_class("hidden")
        self.add_class("visible")
        # Update columns if needed
        if self.columns:
            agg_column_select = self.query_one("#agg_column_select", Select)
            agg_column_select.set_options([(col, col) for col in self.columns])
            group_by_select = self.query_one("#group_by_select", Select)
            group_by_select.set_options(
                [("(None)", "")] + [(col, col) for col in self.columns]
            )

        # Clear checkboxes
        for func_id, _ in self.AGG_FUNCTIONS:
            checkbox = self.query_one(f"#agg_func_{func_id}", Checkbox)
            checkbox.value = False

        self.focus()

    def update_columns(self, columns: list[str]) -> None:
        """Update available columns for aggregation."""
        self.columns = columns
        if self.is_mounted:
            agg_column_select = self.query_one("#agg_column_select", Select)
            agg_column_select.set_options([(col, col) for col in self.columns])
            group_by_select = self.query_one("#group_by_select", Select)
            group_by_select.set_options(
                [("(None)", "")] + [(col, col) for col in self.columns]
            )
