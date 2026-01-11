"""Pivot table widget with hierarchical display and expand/collapse support."""

from dataclasses import dataclass
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import DataTable, Label

try:
    import narwhals as nw

    NARWHALS_AVAILABLE = True
except ImportError:
    NARWHALS_AVAILABLE = False


@dataclass
class PivotMetadata:
    """Metadata about pivot table structure."""

    row_dimensions: list[str]
    column_dimension: str | None
    value_columns: list[str]
    agg_functions: list[str]
    total_rows: int = 0
    total_cols: int = 0


class PivotTableWidget(Container):
    """Interactive pivot table widget with hierarchical row groups.

    Features:
    - Displays pivot table results with row/column dimensions
    - Hierarchical display of row dimension groups
    - Expand/collapse functionality for row groups
    - Column headers showing dimension values and aggregations
    - Pagination for large pivot tables
    - Keyboard navigation (arrow keys, Enter to expand/collapse)

    Example:
        >>> import narwhals as nw
        >>> import pandas as pd
        >>> from kittiwake.widgets.pivot_table import PivotTableWidget
        >>>
        >>> # Create sample data
        >>> data = {
        ...     "category": ["A", "A", "B", "B"],
        ...     "region": ["East", "West", "East", "West"],
        ...     "amount": [10, 20, 30, 40]
        ... }
        >>> df = nw.from_native(pd.DataFrame(data))
        >>>
        >>> # Create pivot
        >>> pivot_df = df.pivot(
        ...     on="region",
        ...     index="category",
        ...     values="amount",
        ...     aggregate_function="sum"
        ... )
        >>>
        >>> # Create widget
        >>> widget = PivotTableWidget()
        >>> widget.load_pivot(
        ...     pivot_df,
        ...     row_dimensions=["category"],
        ...     column_dimension="region",
        ...     value_columns=["amount"],
        ...     agg_functions=["sum"]
        ... )
    """

    BINDINGS = [
        Binding("enter", "toggle_expand", "Expand/Collapse", show=False),
        Binding("ctrl+enter", "expand_all", "Expand All", show=False),
        Binding("ctrl+shift+e", "collapse_all", "Collapse All", show=False),
    ]

    can_focus = True
    can_focus_children = True

    DEFAULT_CSS = """
    PivotTableWidget {
        height: 1fr;
        layout: vertical;
    }

    PivotTableWidget:focus {
        border: tall $accent;
    }

    PivotTableWidget > DataTable {
        height: 1fr;
    }

    PivotTableWidget > Label {
        height: auto;
        padding: 0 1;
        text-style: dim;
    }
    """

    current_page = reactive(0)
    total_pages = reactive(1)
    page_size = reactive(100)

    def __init__(self, page_size: int = 100, **kwargs):
        """Initialize pivot table widget.

        Args:
            page_size: Number of row groups per page (default 100)

        """
        super().__init__(**kwargs)
        self.page_size = page_size
        self.data_table: DataTable | None = None
        self.status_label: Label | None = None
        self.metadata: PivotMetadata | None = None

        self._pivot_df: Any = None
        self._expanded_groups: dict[tuple, bool] = {}
        self._flat_rows: list[dict] = []
        self._row_groups: dict[tuple, list[int]] = {}

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield DataTable(id="pivot_table", zebra_stripes=True, show_cursor=True)
        yield Label("", id="pivot_status")

    def on_mount(self) -> None:
        """Initialize table when mounted."""
        self.data_table = self.query_one("#pivot_table", DataTable)
        self.status_label = self.query_one("#pivot_status", Label)

        self.data_table.cursor_type = "row"
        self.data_table.zebra_stripes = True

        self.focus()

    def load_pivot(
        self,
        pivot_df: Any,
        row_dimensions: list[str],
        column_dimension: str | None = None,
        value_columns: list[str] | None = None,
        agg_functions: list[str] | None = None,
    ) -> None:
        """Load pivot table data into widget.

        Args:
            pivot_df: Narwhals DataFrame with pivot results
            row_dimensions: List of column names used as row dimensions (index)
            column_dimension: Column name used as column dimension (optional)
            value_columns: List of value columns that were aggregated
            agg_functions: List of aggregation functions applied

        Raises:
            ValueError: If narwhals is not available or data is invalid

        """
        if not NARWHALS_AVAILABLE:
            raise ValueError("narwhals library is required for pivot tables")

        if pivot_df is None:
            raise ValueError("pivot_df cannot be None")

        self._pivot_df = pivot_df

        if value_columns is None:
            value_columns = []
        if agg_functions is None:
            agg_functions = []

        self.metadata = PivotMetadata(
            row_dimensions=row_dimensions,
            column_dimension=column_dimension,
            value_columns=value_columns,
            agg_functions=agg_functions,
        )

        self._build_row_groups()
        self._expand_all_groups()

        row_count = len(self._flat_rows)
        if row_count > 0:
            self.total_pages = (row_count + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1

        self.current_page = 0
        self._load_page()

    def _build_row_groups(self) -> None:
        """Build hierarchical row groups from pivot data."""
        if self._pivot_df is None or self.metadata is None:
            return

        self._flat_rows = []
        self._row_groups = {}

        df_dict = self._pivot_df.to_dict(as_series=False)
        num_rows = len(self._pivot_df)

        for i in range(num_rows):
            row_data = {}
            for col in df_dict:
                row_data[col] = df_dict[col][i]

            group_key = tuple(row_data[dim] for dim in self.metadata.row_dimensions)

            if group_key not in self._row_groups:
                self._row_groups[group_key] = []

            row_data["_group_key"] = group_key
            row_data["_is_group_header"] = (i == 0) or (
                group_key
                != tuple(self._flat_rows[-1]["_group_key"] if self._flat_rows else None)
            )

            self._row_groups[group_key].append(len(self._flat_rows))
            self._flat_rows.append(row_data)

        if self.metadata:
            self.metadata.total_rows = len(self._flat_rows)
            self.metadata.total_cols = len(df_dict) if df_dict else 0

    def _expand_all_groups(self) -> None:
        """Expand all row groups."""
        for group_key in self._row_groups:
            self._expanded_groups[group_key] = True

    def _collapse_all_groups(self) -> None:
        """Collapse all row groups (show only headers)."""
        for group_key in self._row_groups:
            self._expanded_groups[group_key] = False

    def _load_page(self) -> None:
        """Load current page of rows into data table."""
        if not self.data_table:
            return

        self.data_table.clear(columns=True)

        if not self._flat_rows or self.metadata is None:
            self._update_status("No data")
            return

        visible_rows = self._get_visible_rows()

        if len(visible_rows) == 0:
            self._update_status("No data")
            return

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(visible_rows))
        page_rows = visible_rows[start_idx:end_idx]

        self._add_columns(page_rows)
        self._add_rows(page_rows)
        self._update_status()

    def _get_visible_rows(self) -> list[dict]:
        """Get list of visible rows based on expand/collapse state."""
        visible = []

        for row_data in self._flat_rows:
            group_key = row_data["_group_key"]

            if row_data["_is_group_header"]:
                visible.append(row_data)
            elif self._expanded_groups.get(group_key, True):
                visible.append(row_data)

        return visible

    def _add_columns(self, page_rows: list[dict]) -> None:
        """Add columns to data table.

        Args:
            page_rows: Rows to determine columns from

        """
        if not page_rows or self.metadata is None:
            return

        first_row = page_rows[0]
        columns = [col for col in first_row.keys() if not col.startswith("_")]

        for col in columns:
            if col in self.metadata.row_dimensions:
                header = self._create_row_dimension_header(col)
            elif col == self.metadata.column_dimension:
                header = self._create_column_dimension_header(col)
            else:
                header = self._create_value_header(col)

            self.data_table.add_column(header, key=col, width=40)

    def _add_rows(self, page_rows: list[dict]) -> None:
        """Add rows to data table.

        Args:
            page_rows: Rows to add

        """
        for row_data in page_rows:
            row_values = []
            for col in row_data:
                if col.startswith("_"):
                    continue

                value = row_data[col]

                if row_data["_is_group_header"] and col in (
                    self.metadata.row_dimensions if self.metadata else []
                ):
                    prefix = (
                        "▼ "
                        if self._expanded_groups.get(row_data["_group_key"], True)
                        else "▶ "
                    )
                    row_values.append(f"{prefix}{value}")
                else:
                    row_values.append(self._format_value(value))

            self.data_table.add_row(*row_values)

    def _create_row_dimension_header(self, col_name: str) -> Text:
        """Create styled header for row dimension column.

        Args:
            col_name: Column name

        Returns:
            Rich Text object with styled header

        """
        header = Text()
        header.append("📁 ", style="bold cyan")
        header.append(col_name, style="bold cyan")
        return header

    def _create_column_dimension_header(self, col_name: str) -> Text:
        """Create styled header for column dimension.

        Args:
            col_name: Column name

        Returns:
            Rich Text object with styled header

        """
        header = Text()
        header.append("📊 ", style="bold yellow")
        header.append(col_name, style="bold yellow")
        return header

    def _create_value_header(self, col_name: str) -> Text:
        """Create styled header for value column.

        Args:
            col_name: Column name

        Returns:
            Rich Text object with styled header

        """
        header = Text()
        header.append(col_name, style="bold green")
        return header

    def _format_value(self, value: Any) -> str:
        """Format cell value for display.

        Args:
            value: Value to format

        Returns:
            Formatted string representation

        """
        if value is None:
            return ""

        try:
            if isinstance(value, float):
                return f"{value:.2f}"
            return str(value)
        except Exception:
            return ""

    def _update_status(self, error: str | None = None) -> None:
        """Update status label with pagination info.

        Args:
            error: Error message if applicable

        """
        if not self.status_label:
            return

        if error:
            self.status_label.update(error)
            return

        if not self.metadata:
            self.status_label.update("")
            return

        visible_rows = len(self._get_visible_rows())
        start_row = self.current_page * self.page_size + 1
        end_row = min((self.current_page + 1) * self.page_size, visible_rows)

        row_info = f"Rows {start_row}-{end_row} of {visible_rows}"
        group_info = f"Groups {len(self._row_groups)}"
        col_info = f"Cols {self.metadata.total_cols}"

        status = f"{row_info} | {group_info} | {col_info}"
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
        """Navigate to last page."""
        self.current_page = self.total_pages - 1
        self._load_page()

    def action_toggle_expand(self) -> None:
        """Toggle expand/collapse for currently selected row group."""
        if not self.data_table or not self.metadata:
            return

        coord = self.data_table.cursor_coordinate
        if not coord:
            return

        visible_rows = self._get_visible_rows()
        if coord.row >= len(visible_rows):
            return

        row_data = visible_rows[coord.row]
        if not row_data["_is_group_header"]:
            return

        group_key = row_data["_group_key"]
        current_state = self._expanded_groups.get(group_key, True)
        self._expanded_groups[group_key] = not current_state

        self._load_page()

    def action_expand_all(self) -> None:
        """Expand all row groups."""
        self._expand_all_groups()
        self._load_page()

    def action_collapse_all(self) -> None:
        """Collapse all row groups."""
        self._collapse_all_groups()
        self._load_page()
