"""Dataset table widget with pagination support."""

import json

import pyperclip
from rich.text import Text
from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Label

from ..models.dataset import Dataset
from ..services.type_detector import detect_column_type_category
from ..utils.type_colors import get_type_color, get_type_icon


class DatasetTable(Container):
    """Interactive data table widget with pagination.

    Features:
    - Displays data in paginated table format
    - 500-1000 rows per page
    - Column headers with types
    - Navigation with arrow keys, Page Up/Down
    - Current page indicator
    """

    BINDINGS = [
        Binding("v", "view_cell", "View Cell", show=False),
        Binding("ctrl+y", "copy_cell", "Copy Cell", show=False),
        Binding("ctrl+shift+f", "filter_columns", "Filter Columns", show=False),
    ]

    # Enable focus to receive key events
    can_focus = True
    can_focus_children = True

    DEFAULT_CSS = """
    DatasetTable {
        height: 1fr;
        layout: vertical;
    }

    DatasetTable:focus {
        border: tall $accent;
    }

    DatasetTable > DataTable {
        height: 1fr;
    }

    DatasetTable > Label {
        height: auto;
        padding: 0 1;
    }
    """

    current_page = reactive(0)
    total_pages = reactive(1)
    page_size = reactive(500)

    def __init__(self, dataset: Dataset | None = None, page_size: int = 500, **kwargs):
        """Initialize dataset table.

        Args:
            dataset: Dataset to display
            page_size: Number of rows per page (default 500)

        """
        super().__init__(**kwargs)
        self.dataset = dataset
        self.page_size = page_size
        self.data_table: DataTable | None = None
        self.status_label: Label | None = None
        self.hidden_columns: set[str] = set()  # Track hidden columns

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield DataTable(id="data_table", zebra_stripes=True, show_cursor=True)
        yield Label("", id="table_status")

    def on_mount(self) -> None:
        """Initialize table when mounted."""
        self.data_table = self.query_one("#data_table", DataTable)
        self.status_label = self.query_one("#table_status", Label)

        # Enable table features
        self.data_table.cursor_type = "cell"
        self.data_table.zebra_stripes = True

        # Request focus to receive key events
        self.focus()

        if self.dataset:
            self.load_dataset(self.dataset)

    def on_focus(self) -> None:
        """Handle focus gain event - notify parent of focused dataset."""
        if self.dataset:
            self.post_message(self.FocusGained(self.dataset))

    def load_dataset(self, dataset: Dataset) -> None:
        """Load a dataset into the table.

        Args:
            dataset: Dataset to display

        """
        self.dataset = dataset
        self.current_page = 0

        # Use filtered row count if operations have been applied
        row_count = dataset.get_filtered_row_count()
        if row_count > 0:
            self.total_pages = (row_count + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1

        self._load_page()

        # Focus this table and trigger focus event to update operations sidebar
        self.focus()
        self.post_message(self.FocusGained(dataset))

    def _load_page(self) -> None:
        """Load current page into data table."""
        if not self.data_table or not self.dataset:
            return

        # Clear existing data
        self.data_table.clear(columns=True)

        # Get page data
        page_data = self.dataset.get_page(self.current_page, self.page_size)

        if page_data is None or len(page_data) == 0:
            self._update_status("No data")
            return

        # Add columns with type info and width limit
        try:
            schema = self.dataset.schema
            for col_name in page_data.columns:
                # Skip hidden columns
                if col_name in self.hidden_columns:
                    continue

                col_type = schema.get(col_name, "Unknown")
                header = self._create_column_header(col_name, col_type)
                # Set column width to 40 characters - DataTable will handle overflow
                self.data_table.add_column(
                    header, key=col_name, width=min(40, len(col_name) + 4)
                )
        except Exception:
            # Fallback: just use column names
            for col_name in page_data.columns:
                # Skip hidden columns
                if col_name in self.hidden_columns:
                    continue

                self.data_table.add_column(
                    col_name, key=col_name, width=min(40, len(col_name) + 4)
                )

        # Add rows with full cell values (no truncation)
        try:
            # Convert to list of lists for DataTable
            for i in range(len(page_data)):
                row_data = []
                for col in page_data.columns:
                    # Skip hidden columns
                    if col in self.hidden_columns:
                        continue

                    try:
                        value = page_data[col][i]
                        # Convert to string, handle None/NaN
                        if value is None or (
                            hasattr(value, "__ne__") and value != value
                        ):
                            row_data.append("")
                        else:
                            # Store full value - column width will handle display
                            str_val = str(value)
                            # Format JSON values as compact
                            if str_val.startswith("[") or str_val.startswith("{"):
                                try:
                                    parsed = json.loads(str_val)
                                    if isinstance(parsed, (list, dict)):
                                        # Compact JSON for display
                                        str_val = json.dumps(
                                            parsed, separators=(",", ":")
                                        )
                                except (json.JSONDecodeError, ValueError):
                                    pass
                            row_data.append(str_val)
                    except Exception:
                        row_data.append("")
                self.data_table.add_row(*row_data)
        except Exception as e:
            self._update_status(f"Error loading data: {e}")
            return

        self._update_status()

    def _create_column_header(self, col_name: str, dtype: str) -> Text:
        """Create styled header with type indicator.

        Args:
            col_name: Column name
            dtype: Narwhals dtype string

        Returns:
            Rich Text object with styled header

        """
        # Detect type category
        type_category = detect_column_type_category(dtype)

        # Get visual indicators
        icon = get_type_icon(type_category)
        color = get_type_color(type_category)

        # Build styled header
        header = Text()
        header.append(f"{icon} ", style=f"bold {color}")
        header.append(col_name, style=color)
        header.append(f"\n({dtype})", style="dim")

        return header

    def _update_status(self, error: str | None = None) -> None:
        """Update status label with pagination info."""
        if not self.status_label:
            return

        if error:
            self.status_label.update(error)
            return

        if not self.dataset:
            self.status_label.update("")
            return

        # Use filtered row count if operations have been applied
        row_count = self.dataset.get_filtered_row_count()
        start_row = self.current_page * self.page_size + 1
        end_row = min((self.current_page + 1) * self.page_size, row_count)

        # Calculate visible vs total columns
        total_cols = len(self.dataset.schema)
        visible_cols = total_cols - len(self.hidden_columns)
        col_info = f" | Cols {visible_cols}/{total_cols}" if self.hidden_columns else ""

        status = (
            f"Page {self.current_page + 1}/{self.total_pages} | "
            f"Rows {start_row:,}-{end_row:,} of {row_count:,}{col_info} | "
            f"{self.dataset.name}"
        )
        self.status_label.update(status)

    def next_page(self) -> bool:
        """Navigate to next page.

        Returns:
            True if page changed, False if already on last page

        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._load_page()
            return True
        return False

    def previous_page(self) -> bool:
        """Navigate to previous page.

        Returns:
            True if page changed, False if already on first page

        """
        if self.current_page > 0:
            self.current_page -= 1
            self._load_page()
            return True
        return False

    def first_page(self) -> None:
        """Navigate to first page."""
        if self.current_page != 0:
            self.current_page = 0
            self._load_page()

    def last_page(self) -> None:
        """Go to last page."""
        self.current_page = self.total_pages - 1
        self._load_page()

    def scroll_columns(self, direction: int) -> bool:
        """Scroll columns left or right by 5 columns.

        Args:
            direction: -1 for left, 1 for right

        Returns:
            True if scrolled, False if no more columns in that direction

        """
        if not self.data_table or not self.data_table.columns:
            return False

        num_cols = len(self.data_table.columns)

        if num_cols == 0:
            return False

        # Press arrow keys 5 times in the specified direction
        scroll_action = (
            self.data_table.action_cursor_left
            if direction < 0
            else self.data_table.action_cursor_right
        )

        for _ in range(5):
            scroll_action()

        return True

    def action_copy_cell(self) -> None:
        """Copy cell content to system clipboard.

        Triggered by pressing Ctrl+Y on a cell.
        Copies the full cell value to clipboard and shows a notification.
        """
        if not self.data_table or not self.dataset:
            return

        coord = self.data_table.cursor_coordinate
        if not coord:
            return

        try:
            # Get column key from coordinate
            if coord.column >= len(self.data_table.columns):
                return

            # Get the cell value directly from DataTable
            cell_value = self.data_table.get_cell_at(coord)

            # Handle None/empty values - copy empty string
            if cell_value is None or cell_value == "":
                copy_value = ""
            else:
                # Copy full content as string (no truncation)
                copy_value = str(cell_value)

            # Copy to clipboard
            pyperclip.copy(copy_value)

            # Show brief notification
            self.notify("Copied to clipboard", timeout=2)
        except Exception as e:
            self.notify(f"Error copying cell: {e}", severity="error")

    def action_view_cell(self) -> None:
        """Show full cell content in a toast notification.

        Triggered by pressing 'v' key on a cell.
        Gets the full value directly from the DataTable (no longer truncated).
        """
        if not self.data_table or not self.dataset:
            return

        coord = self.data_table.cursor_coordinate
        if not coord:
            return

        try:
            # Get column key from coordinate
            if coord.column >= len(self.data_table.columns):
                return

            col_key = list(self.data_table.columns.keys())[coord.column]
            # ColumnKey objects have a .value attribute containing the column name string
            col_name = str(col_key.value) if hasattr(col_key, "value") else str(col_key)

            # Calculate actual row index in dataset (accounting for pagination)
            actual_row = self.current_page * self.page_size + coord.row

            # Get the cell value directly from DataTable (it now has full values)
            cell_value = self.data_table.get_cell_at(coord)

            # Format the value for display
            if cell_value is None or cell_value == "":
                formatted_value = "(null)"
            else:
                str_value = str(cell_value)
                # Try to format as pretty JSON if it looks like JSON
                if str_value.startswith("[") or str_value.startswith("{"):
                    try:
                        parsed = json.loads(str_value)
                        if isinstance(parsed, (list, dict)):
                            formatted_value = json.dumps(parsed, indent=2)
                        else:
                            formatted_value = str_value
                    except (json.JSONDecodeError, ValueError):
                        formatted_value = str_value
                else:
                    formatted_value = str_value

            # Show full cell content in a toast notification
            pyperclip.copy(formatted_value)
            self.notify(f"Copied to clipboard:\n{formatted_value}", timeout=10)
        except Exception as e:
            self.notify(f"Error viewing cell: {e}", severity="error")

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header click to open quick filter modal.

        Args:
            event: HeaderSelected event with column information

        """
        # Get column information - ColumnKey has a .value attribute
        column_key_raw = (
            event.column_key.value
            if hasattr(event.column_key, "value")
            else str(event.column_key)
        )
        column_key = str(column_key_raw) if column_key_raw is not None else ""

        # Get dtype from dataset schema
        if not self.dataset or not column_key:
            return

        dtype = self.dataset.schema.get(column_key, "Unknown")

        # Launch worker to show modal (async operation)
        self._show_quick_filter_modal(column_key, dtype)

    @work(exclusive=True)
    async def _show_quick_filter_modal(self, column_key: str, dtype: str) -> None:
        """Show quick filter modal in a worker (async context).

        Args:
            column_key: Column name
            dtype: Column data type

        """
        from .modals import ColumnHeaderQuickFilter

        # Open quick filter modal with pre-populated column
        result = await self.app.push_screen_wait(
            ColumnHeaderQuickFilter(column_key, dtype)
        )

        # If user submitted a filter (not cancelled)
        if result:
            # Post message to parent (main screen) to handle filter creation
            self.post_message(self.QuickFilterRequested(result))

    def action_filter_columns(self) -> None:
        """Open column filter modal to show/hide columns.

        Triggered by pressing Ctrl+Shift+F.
        Opens modal with column list, type filters, and search.
        """
        if not self.dataset:
            self.notify("No dataset loaded", severity="warning")
            return

        # Launch worker to show modal (async operation)
        self._show_column_filter_modal()

    @work(exclusive=True)
    async def _show_column_filter_modal(self) -> None:
        """Show column filter modal in a worker (async context)."""
        from .modals import ColumnFilterModal

        # Get all columns and schema from dataset
        columns = list(self.dataset.schema.keys())
        schema = self.dataset.schema

        # Open column filter modal
        result = await self.app.push_screen_wait(
            ColumnFilterModal(columns, schema, self.hidden_columns.copy())
        )

        # If user cancelled, do nothing
        if result is None:
            return

        # Modal returns None on cancel, otherwise we dismissed via dismiss(None)
        # The modal modifies self.hidden_columns directly through the reference
        # But we need to refresh the table
        self._load_page()

    class FocusGained(Message):
        """Message posted when this table gains focus."""

        def __init__(self, dataset: Dataset | None) -> None:
            """Initialize message with dataset reference.

            Args:
                dataset: The dataset currently displayed in this table

            """
            super().__init__()
            self.dataset = dataset

    class QuickFilterRequested(Message):
        """Message posted when user requests a quick filter from column header."""

        def __init__(self, filter_data: dict) -> None:
            """Initialize message with filter data.

            Args:
                filter_data: Dict with column, operator, value, type_category

            """
            super().__init__()
            self.filter_data = filter_data
