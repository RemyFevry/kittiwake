"""Column filter modal for showing/hiding columns by name and type."""

import re
from typing import Literal

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Static

from ...services.type_detector import detect_column_type_category
from ...utils.type_colors import TYPE_ICONS_ASCII, get_type_color

TypeCategory = Literal["numeric", "text", "date", "boolean", "list", "dict", "unknown"]


class ColumnFilterModal(ModalScreen[dict | None]):
    """Modal screen for filtering columns by name and type.

    Features:
    - Text search with regex support for column names
    - Type checkboxes to filter by column type
    - Show/hide columns based on filter criteria
    - Display count of visible vs total columns
    - Reset button to show all columns

    Returns dict with hidden_columns list on Apply, None on Cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        columns: list[str],
        schema: dict[str, str],
        hidden_columns: set[str] | None = None,
        **kwargs,
    ):
        """Initialize column filter modal.

        Args:
            columns: List of all column names in the dataset
            schema: Dict mapping column names to narwhals dtype strings
            hidden_columns: Set of currently hidden column names (default: empty)

        """
        super().__init__(**kwargs)
        self.columns = columns
        self.schema = schema
        self.hidden_columns = hidden_columns or set()

        # Track which columns match the current filter
        self.filtered_columns: list[str] = columns.copy()

        # Build type category map
        self.column_types: dict[str, TypeCategory] = {}
        for col in columns:
            dtype = schema.get(col, "Unknown")
            self.column_types[col] = detect_column_type_category(dtype)

        # Track selected type filters
        self.selected_types: set[TypeCategory] = {
            "numeric",
            "text",
            "date",
            "boolean",
            "list",
            "dict",
            "unknown",
        }

    def compose(self) -> ComposeResult:
        """Create column filter modal content."""
        with Container(id="column_filter_dialog"):
            yield Label("Filter Columns", id="column_filter_title")

            with Vertical(id="column_filter_form"):
                # Column name search
                yield Label("Search by name (regex supported):", classes="filter_label")
                yield Input(
                    placeholder="e.g., age|name|.*price.*",
                    id="column_search_input",
                )

                # Type filters
                yield Label("Filter by type:", classes="filter_label")
                with Horizontal(id="type_filters"):
                    yield Checkbox("Numeric (#)", value=True, id="type_numeric")
                    yield Checkbox('Text (")', value=True, id="type_text")
                    yield Checkbox("Date (@)", value=True, id="type_date")
                    yield Checkbox("Boolean (?)", value=True, id="type_boolean")

                with Horizontal(id="type_filters_2"):
                    yield Checkbox("List ([)", value=True, id="type_list")
                    yield Checkbox("Dict ({)", value=True, id="type_dict")
                    yield Checkbox("Unknown (·)", value=True, id="type_unknown")

                # Column list (scrollable)
                yield Label("", id="column_count_label")
                with ScrollableContainer(id="column_list_container"):
                    yield Static("", id="column_list")

            # Buttons
            with Horizontal(id="column_filter_buttons"):
                yield Button("Apply", variant="primary", id="apply_button")
                yield Button("Reset All", variant="default", id="reset_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Initialize column list when modal opens."""
        self._update_column_list()
        self.query_one("#column_search_input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "column_search_input":
            self._update_column_list()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle type filter checkbox changes."""
        checkbox_id = event.checkbox.id

        # Map checkbox IDs to type categories
        type_map = {
            "type_numeric": "numeric",
            "type_text": "text",
            "type_date": "date",
            "type_boolean": "boolean",
            "type_list": "list",
            "type_dict": "dict",
            "type_unknown": "unknown",
        }

        if checkbox_id in type_map:
            type_category = type_map[checkbox_id]
            if event.value:
                self.selected_types.add(type_category)
            else:
                self.selected_types.discard(type_category)

            self._update_column_list()

    def _update_column_list(self) -> None:
        """Update the column list based on current filters."""
        search_input = self.query_one("#column_search_input", Input)
        search_text = search_input.value.strip()

        # Filter columns by search text (regex support)
        filtered = []
        for col in self.columns:
            # Check type filter
            if self.column_types[col] not in self.selected_types:
                continue

            # Check name filter
            if search_text:
                try:
                    # Try regex match
                    if not re.search(search_text, col, re.IGNORECASE):
                        continue
                except re.error:
                    # Fallback to simple case-insensitive substring match
                    if search_text.lower() not in col.lower():
                        continue

            filtered.append(col)

        self.filtered_columns = filtered

        # Build column list display
        column_list = self.query_one("#column_list", Static)

        if not filtered:
            column_list.update("No columns match the current filters.")
        else:
            lines = []
            for col in filtered:
                # Get type info
                type_cat = self.column_types[col]
                icon = TYPE_ICONS_ASCII.get(type_cat, "·")
                color = get_type_color(type_cat)

                # Check if currently hidden
                status = "✗ HIDDEN" if col in self.hidden_columns else "✓ VISIBLE"
                status_color = "red" if col in self.hidden_columns else "green"

                lines.append(
                    f"[{color}]{icon}[/{color}] [{status_color}]{status}[/{status_color}] {col}"
                )

            column_list.update("\n".join(lines))

        # Update count label
        visible_count = len([c for c in filtered if c not in self.hidden_columns])
        total_count = len(self.columns)
        count_label = self.query_one("#column_count_label", Label)
        count_label.update(
            f"Showing {visible_count} of {total_count} columns "
            f"({len(filtered)} matching filters)"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_filter()
        elif event.button.id == "reset_button":
            self._reset_all()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def _apply_filter(self) -> None:
        """Apply current filter: hide all filtered columns, show all others."""
        # Hide all columns that match the current filter
        # Show all columns that don't match

        # Strategy: Toggle visibility of filtered columns
        # If any filtered column is visible, hide all filtered columns
        # If all filtered columns are hidden, show all filtered columns

        if not self.filtered_columns:
            self.notify("No columns to apply filter to", severity="warning")
            return

        # Check if any filtered column is currently visible
        any_visible = any(
            col not in self.hidden_columns for col in self.filtered_columns
        )

        if any_visible:
            # Hide all filtered columns
            for col in self.filtered_columns:
                self.hidden_columns.add(col)
            action = "hidden"
        else:
            # Show all filtered columns
            for col in self.filtered_columns:
                self.hidden_columns.discard(col)
            action = "shown"

        # Validation: ensure at least one column remains visible
        if len(self.hidden_columns) >= len(self.columns):
            self.notify(
                "Cannot hide all columns - at least one must remain visible",
                severity="error",
            )
            # Restore the first column
            if self.columns:
                self.hidden_columns.discard(self.columns[0])

        self.notify(f"{len(self.filtered_columns)} column(s) {action}", timeout=2)
        self._update_column_list()

    def _reset_all(self) -> None:
        """Reset all filters and show all columns."""
        self.hidden_columns.clear()

        # Reset search
        search_input = self.query_one("#column_search_input", Input)
        search_input.value = ""

        # Reset type filters
        for checkbox in self.query(Checkbox):
            checkbox.value = True

        self.selected_types = {
            "numeric",
            "text",
            "date",
            "boolean",
            "list",
            "dict",
            "unknown",
        }

        self._update_column_list()
        self.notify("All columns visible", timeout=2)

    def action_cancel(self) -> None:
        """Cancel and close modal without returning data."""
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search input field."""
        if event.input.id == "column_search_input":
            self._apply_filter()


# CSS for column filter modal
COLUMN_FILTER_MODAL_CSS = """
ColumnFilterModal {
    align: center middle;
}

#column_filter_dialog {
    width: 80;
    height: auto;
    max-height: 90%;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#column_filter_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#column_filter_form {
    height: auto;
    padding: 1 0;
}

.filter_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

#column_search_input {
    width: 100%;
    margin-bottom: 1;
}

#type_filters, #type_filters_2 {
    width: 100%;
    height: auto;
    margin-bottom: 1;
}

#type_filters Checkbox, #type_filters_2 Checkbox {
    margin: 0 1;
}

#column_count_label {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $accent;
}

#column_list_container {
    width: 100%;
    height: 20;
    border: solid $accent;
    padding: 1;
    margin-bottom: 1;
}

#column_list {
    width: 100%;
    height: auto;
}

#column_filter_buttons {
    width: 100%;
    height: auto;
    align: center middle;
    margin-top: 1;
}

#column_filter_buttons Button {
    margin: 0 1;
}
"""
