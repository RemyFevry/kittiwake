"""Pivot sidebar for building pivot table operations (left sidebar, overlay)."""

from collections.abc import Callable
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Checkbox, Label, Select, SelectionList
from textual.widgets.selection_list import Selection


class ValueAggregationSection(Container):
    """A section for configuring one value column with its aggregations.

    This widget allows users to:
    - Select a value column from a dropdown
    - Select which aggregation functions to apply to this value (multi-select)
    - Remove this value section
    """

    # Available aggregation functions
    AGG_FUNCTIONS = [
        ("count", "Count"),
        ("sum", "Sum"),
        ("mean", "Mean"),
        ("min", "Min"),
        ("max", "Max"),
        ("first", "First"),
        ("last", "Last"),
        ("len", "Len"),
    ]

    def __init__(
        self,
        section_id: int,
        columns: list[str],
        on_remove: Callable[[int], None],
        **kwargs: Any,
    ) -> None:
        """Initialize a value aggregation section.

        Args:
            section_id: Unique ID for this section
            columns: Available columns to select from
            on_remove: Callback when remove button is clicked
            **kwargs: Additional arguments for Container
        """
        super().__init__(
            id=f"value_section_{section_id}", classes="value-section", **kwargs
        )
        self.section_id = section_id
        self.available_columns = columns
        self.on_remove_callback = on_remove

    def compose(self) -> ComposeResult:
        """Create the value section content."""
        # Title for this value section
        yield Label(
            f"─── Value #{self.section_id + 1} ───",
            classes="value-section-title",
        )

        # Column selection - NO Container wrapper
        yield Label("Column:", classes="form-label")
        yield Select(
            options=[(col, col) for col in self.available_columns],
            prompt="Select value column",
            id=f"value_column_{self.section_id}",
            allow_blank=True,
        )

        # Aggregations - NO Container wrapper
        yield Label("Aggregations:", classes="form-label")
        # Create individual checkboxes for each aggregation function
        for func_id, func_label in self.AGG_FUNCTIONS:
            yield Checkbox(
                func_label,
                id=f"value_agg_{self.section_id}_{func_id}",
                classes="agg-function-checkbox",
            )

        # Remove button
        yield Button(
            "Remove Value",
            variant="error",
            id=f"remove_value_{self.section_id}",
            classes="remove-value-btn",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle remove button press."""
        if event.button.id == f"remove_value_{self.section_id}":
            event.stop()
            self.on_remove_callback(self.section_id)

    def get_config(self) -> dict[str, Any] | None:
        """Get the configuration for this value section.

        Returns:
            Dict with 'column' and 'agg_functions' keys, or None if invalid
        """
        try:
            value_select = self.query_one(f"#value_column_{self.section_id}", Select)
            column = value_select.value

            if not column or column == Select.BLANK:
                return None

            # Get selected aggregations from Checkboxes
            agg_functions = []
            for func_id, _ in self.AGG_FUNCTIONS:
                try:
                    checkbox = self.query_one(
                        f"#value_agg_{self.section_id}_{func_id}", Checkbox
                    )
                    if checkbox.value:
                        agg_functions.append(func_id)
                except Exception:
                    pass

            if not agg_functions:
                return None

            return {"column": column, "agg_functions": agg_functions}
        except Exception:
            return None


class PivotSidebar(VerticalScroll):
    """Left sidebar for pivot table configuration (overlay, 30% width).

    Features:
    - SelectionList for "index" columns (rows) - multi-select
    - SelectionList for "columns" columns (spread across columns) - multi-select
    - Dynamic value sections where each can have different aggregations
    - Add/remove value sections
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Callback-based result handling

    Usage:
        sidebar.columns = ["age", "name", "salary"]
        sidebar.callback = lambda params: handle_pivot(params)
        sidebar.show()
    """

    # Expose AGG_FUNCTIONS from ValueAggregationSection for easier access
    AGG_FUNCTIONS = ValueAggregationSection.AGG_FUNCTIONS

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]

    def __init__(self, columns: list[str] | None = None, **kwargs: Any) -> None:
        """Initialize pivot sidebar.

        Args:
            columns: List of column names
            **kwargs: Additional arguments for VerticalScroll
        """
        super().__init__(id="pivot_sidebar", classes="sidebar hidden", **kwargs)
        self.columns: list[str] = columns or []
        self.value_columns: list[str] = (
            columns or []
        )  # Separate list for value dropdowns
        self.callback: Callable[[dict], None] | None = None
        self.value_sections: list[int] = []  # Track section IDs
        self.next_section_id: int = 0

    def compose(self) -> ComposeResult:
        """Create pivot sidebar content."""
        yield Label("Pivot Table Configuration", classes="sidebar-title")

        # Add help text
        yield Label(
            "Configure pivot: select index columns, pivot columns, and values to aggregate",
            classes="form-label",
        )

        # Index columns section
        with Container(classes="form-group", id="index_container"):
            yield Label(
                "Index (rows) - Select multiple with Space:", classes="form-label"
            )
            # Set explicit height for SelectionList
            index_list = SelectionList[str](id="index_selection_list")
            index_list.styles.height = 8
            yield index_list

        # Columns section
        with Container(classes="form-group", id="columns_container"):
            yield Label(
                "Columns (spread) - Select multiple with Space:", classes="form-label"
            )
            # Set explicit height for SelectionList
            columns_list = SelectionList[str](id="columns_selection_list")
            columns_list.styles.height = 8
            yield columns_list

        # Values section container
        with Container(classes="form-group", id="values_container"):
            yield Label("Values & Aggregations:", classes="form-label")
            # Value sections will be dynamically added here
            yield Container(id="value_sections_container")
        yield Button("+ Add Value", variant="success", id="add_value_button")

        # Action buttons
        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Initialize selection lists when mounted."""
        # Note: Don't populate or add sections here
        # They will be added when show() is called with columns set
        pass

    def _populate_selection_lists(self) -> None:
        """Populate index and columns selection lists with column options."""
        # Update index selection list
        index_list = self.query_one("#index_selection_list", SelectionList)
        index_list.clear_options()
        for col in self.columns:
            index_list.add_option(Selection(col, col, initial_state=False))

        # Update columns selection list
        columns_list = self.query_one("#columns_selection_list", SelectionList)
        columns_list.clear_options()
        for col in self.columns:
            columns_list.add_option(Selection(col, col, initial_state=False))

    def _add_value_section(self) -> None:
        """Add a new value aggregation section."""
        section_id = self.next_section_id
        self.next_section_id += 1
        self.value_sections.append(section_id)

        section = ValueAggregationSection(
            section_id=section_id,
            columns=self.value_columns,  # Use value_columns instead of columns
            on_remove=self._remove_value_section,
        )

        container = self.query_one("#value_sections_container", Container)
        container.mount(section)

    def _remove_value_section(self, section_id: int) -> None:
        """Remove a value aggregation section.

        Args:
            section_id: ID of the section to remove
        """
        if section_id in self.value_sections:
            self.value_sections.remove(section_id)

        # Remove the widget
        try:
            section = self.query_one(
                f"#value_section_{section_id}", ValueAggregationSection
            )
            section.remove()
        except Exception:
            pass

        # Ensure at least one section remains
        if not self.value_sections:
            self._add_value_section()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_pivot()
        elif event.button.id == "cancel_button":
            self.action_dismiss()
        elif event.button.id == "add_value_button":
            self._add_value_section()

    def _apply_pivot(self) -> None:
        """Validate inputs and trigger callback."""
        # Get selected index columns
        index_list = self.query_one("#index_selection_list", SelectionList)
        index_cols = list(index_list.selected)

        # Get selected columns columns
        columns_list = self.query_one("#columns_selection_list", SelectionList)
        columns_cols = list(columns_list.selected)

        # Get value configurations
        value_configs = []
        for section_id in self.value_sections:
            try:
                section = self.query_one(
                    f"#value_section_{section_id}", ValueAggregationSection
                )
                config = section.get_config()
                if config:
                    value_configs.append(config)
            except Exception:
                pass

        # Validation
        if not index_cols:
            self.app.notify(
                "Please select at least one index column", severity="warning"
            )
            return

        if not columns_cols:
            self.app.notify(
                "Please select at least one columns column", severity="warning"
            )
            return

        if not value_configs:
            self.app.notify(
                "Please configure at least one value with aggregations",
                severity="warning",
            )
            return

        # Build params
        params = {
            "index": index_cols if len(index_cols) > 1 else index_cols[0],
            "columns": columns_cols if len(columns_cols) > 1 else columns_cols[0],
            "values": value_configs,
        }

        # Trigger callback
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

        # Repopulate selection lists in case columns changed
        if self.columns:
            self._populate_selection_lists()

        # Deselect all options in SelectionLists
        try:
            index_list = self.query_one("#index_selection_list", SelectionList)
            index_list.deselect_all()
        except Exception:
            pass

        try:
            columns_list = self.query_one("#columns_selection_list", SelectionList)
            columns_list.deselect_all()
        except Exception:
            pass

        # Clear value sections - only if they exist
        # Check if we already have the default section
        container = self.query_one("#value_sections_container", Container)
        if not container.children or len(self.value_sections) == 0:
            # No sections yet, add one
            self.value_sections.clear()
            self.next_section_id = 0
            self._add_value_section()
        else:
            # Sections exist, just reset the first one and remove others
            # Keep only the first section
            sections_to_remove = self.value_sections[1:]
            for section_id in sections_to_remove:
                try:
                    section = self.query_one(
                        f"#value_section_{section_id}", ValueAggregationSection
                    )
                    section.remove()
                    self.value_sections.remove(section_id)
                except Exception:
                    pass

            # Reset the first section
            if self.value_sections:
                try:
                    first_section = self.query_one(
                        f"#value_section_{self.value_sections[0]}",
                        ValueAggregationSection,
                    )
                    # Reset value dropdown
                    value_select = first_section.query_one(
                        f"#value_column_{self.value_sections[0]}", Select
                    )
                    value_select.clear()
                    # Reset all aggregation checkboxes
                    for func_id, _ in ValueAggregationSection.AGG_FUNCTIONS:
                        try:
                            checkbox = first_section.query_one(
                                f"#value_agg_{self.value_sections[0]}_{func_id}",
                                Checkbox,
                            )
                            checkbox.value = False
                        except Exception:
                            pass
                except Exception:
                    pass

        self.focus()

    def update_columns(
        self, columns: list[str], value_columns: list[str] | None = None
    ) -> None:
        """Update available columns for pivot.

        Args:
            columns: List of all column names (for index/columns selection)
            value_columns: List of numerical column names (for values dropdown).
                          If None, uses all columns (backward compatible).
        """
        self.columns = columns
        self.value_columns = value_columns if value_columns is not None else columns
        if self.is_mounted:
            self._populate_selection_lists()
            # Update existing value sections with numerical columns only
            for section_id in self.value_sections:
                try:
                    section = self.query_one(
                        f"#value_section_{section_id}", ValueAggregationSection
                    )
                    section.available_columns = self.value_columns
                    select = section.query_one(f"#value_column_{section_id}", Select)
                    select.set_options([(col, col) for col in self.value_columns])
                except Exception:
                    pass
