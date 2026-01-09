"""Dataset table widget with pagination support."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import DataTable, Label

from ..models.dataset import Dataset


class DatasetTable(Container):
    """Interactive data table widget with pagination.

    Features:
    - Displays data in paginated table format
    - 500-1000 rows per page
    - Column headers with types
    - Navigation with arrow keys, Page Up/Down
    - Current page indicator
    """

    DEFAULT_CSS = """
    DatasetTable {
        height: 1fr;
        layout: vertical;
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

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield DataTable(id="data_table", zebra_stripes=True, show_cursor=True)
        yield Label("", id="table_status")

    def on_mount(self) -> None:
        """Initialize table when mounted."""
        self.data_table = self.query_one("#data_table", DataTable)
        self.status_label = self.query_one("#table_status", Label)

        # Enable table features
        self.data_table.cursor_type = "row"
        self.data_table.zebra_stripes = True

        if self.dataset:
            self.load_dataset(self.dataset)

    def load_dataset(self, dataset: Dataset) -> None:
        """Load a dataset into the table.

        Args:
            dataset: Dataset to display
        """
        self.dataset = dataset
        self.current_page = 0

        if dataset.row_count > 0:
            self.total_pages = (
                dataset.row_count + self.page_size - 1
            ) // self.page_size
        else:
            self.total_pages = 1

        self._load_page()

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

        # Add columns with type info
        try:
            schema = self.dataset.schema
            for col_name in page_data.columns:
                col_type = schema.get(col_name, "Unknown")
                header = f"{col_name}\n({col_type})"
                self.data_table.add_column(header, key=col_name)
        except Exception:
            # Fallback: just use column names
            for col_name in page_data.columns:
                self.data_table.add_column(col_name, key=col_name)

        # Add rows
        try:
            # Convert to list of lists for DataTable
            for i in range(len(page_data)):
                row_data = []
                for col in page_data.columns:
                    try:
                        value = page_data[col][i]
                        # Convert to string, handle None/NaN
                        if value is None or (
                            hasattr(value, "__ne__") and value != value
                        ):
                            row_data.append("")
                        else:
                            row_data.append(str(value))
                    except Exception:
                        row_data.append("")
                self.data_table.add_row(*row_data)
        except Exception as e:
            self._update_status(f"Error loading data: {e}")
            return

        self._update_status()

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

        start_row = self.current_page * self.page_size + 1
        end_row = min((self.current_page + 1) * self.page_size, self.dataset.row_count)

        status = (
            f"Page {self.current_page + 1}/{self.total_pages} | "
            f"Rows {start_row:,}-{end_row:,} of {self.dataset.row_count:,} | "
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
        """Navigate to last page."""
        if self.current_page != self.total_pages - 1:
            self.current_page = self.total_pages - 1
            self._load_page()
