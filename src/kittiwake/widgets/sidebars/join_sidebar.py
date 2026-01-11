"""Join sidebar for building join operations (left sidebar, overlay)."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Select


class JoinSidebar(VerticalScroll):
    """Left sidebar for join configuration (overlay, 30% width).

    Features:
    - Dropdown for right dataset (list of other loaded datasets from tabs)
    - Dropdown for left key column
    - Dropdown for right key column
    - Radio buttons for join type (inner, left, right, outer)
    - Optional suffix inputs for handling duplicate column names
    - Apply and Cancel buttons
    - Fully keyboard-navigable (Tab, Enter, Esc)
    - Message-based result handling

    Usage:
        sidebar.left_dataset_name = "dataset1.csv"
        sidebar.left_columns = ["id", "name", "value"]
        sidebar.available_datasets = [("dataset2.csv", "dataset2_id"), ...]
        sidebar.right_columns = {}  # Will be populated when dataset selected
        sidebar.show()
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]

    # Available join types
    JOIN_TYPES = [
        ("inner", "Inner Join"),
        ("left", "Left Join"),
        ("right", "Right Join"),
        ("outer", "Outer Join"),
    ]

    class JoinRequested(Message):
        """Message posted when user requests a join operation."""

        def __init__(
            self,
            right_dataset: str,
            left_key: str,
            right_key: str,
            join_type: str,
            left_suffix: str,
            right_suffix: str,
        ) -> None:
            """Initialize join requested message.

            Args:
                right_dataset: Name/ID of the right dataset to join with
                left_key: Column name from left dataset to join on
                right_key: Column name from right dataset to join on
                join_type: Type of join (inner, left, right, outer)
                left_suffix: Suffix for duplicate columns from left dataset
                right_suffix: Suffix for duplicate columns from right dataset

            """
            super().__init__()
            self.right_dataset = right_dataset
            self.left_key = left_key
            self.right_key = right_key
            self.join_type = join_type
            self.left_suffix = left_suffix
            self.right_suffix = right_suffix

    def __init__(
        self,
        left_dataset_name: str = "",
        left_columns: list[str] | None = None,
        available_datasets: list[tuple[str, str]] | None = None,
        **kwargs,
    ):
        """Initialize join sidebar.

        Args:
            left_dataset_name: Name of the left (current/active) dataset
            left_columns: List of column names from left dataset
            available_datasets: List of (name, id) tuples for other loaded datasets

        """
        super().__init__(id="join_sidebar", classes="sidebar hidden", **kwargs)
        self.left_dataset_name: str = left_dataset_name
        self.left_columns: list[str] = left_columns or []
        self.available_datasets: list[tuple[str, str]] = available_datasets or []
        self.right_columns: dict[str, list[str]] = {}  # Maps dataset_id -> columns

    def compose(self) -> ComposeResult:
        """Create join sidebar content."""
        yield Label("Join Configuration", classes="sidebar-title")

        # Show current (left) dataset
        with Container(classes="form-group"):
            yield Label(
                f"Current dataset: {self.left_dataset_name}", classes="form-label"
            )

        # Right dataset selection
        with Container(classes="form-group"):
            yield Label("Join with dataset:", classes="form-label")
            yield Select(
                options=[
                    (name, dataset_id) for name, dataset_id in self.available_datasets
                ]
                if self.available_datasets
                else [],
                prompt="Select dataset to join",
                id="right_dataset_select",
                allow_blank=True,
            )

        # Left key column selection
        with Container(classes="form-group"):
            yield Label("Left key column:", classes="form-label")
            yield Select(
                options=[(col, col) for col in self.left_columns]
                if self.left_columns
                else [],
                prompt="Select left key",
                id="left_key_select",
                allow_blank=True,
            )

        # Right key column selection
        with Container(classes="form-group"):
            yield Label("Right key column:", classes="form-label")
            yield Select(
                options=[],  # Will be populated when right dataset is selected
                prompt="Select right key",
                id="right_key_select",
                allow_blank=True,
            )

        # Join type selection
        with Container(classes="form-group"):
            yield Label("Join type:", classes="form-label")
            with RadioSet(id="join_type_radio"):
                for join_id, join_label in self.JOIN_TYPES:
                    yield RadioButton(
                        join_label,
                        id=f"join_type_{join_id}",
                        value=(join_id == "inner"),
                    )

        # Optional suffixes for duplicate columns
        with Container(classes="form-group"):
            yield Label("Column name suffixes (optional):", classes="form-label")
            yield Label("Left suffix:", classes="form-sublabel")
            yield Input(placeholder="_left", id="left_suffix_input")
            yield Label("Right suffix:", classes="form-sublabel")
            yield Input(placeholder="_right", id="right_suffix_input")

        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    def on_mount(self) -> None:
        """Focus first input when sidebar mounts."""
        if self.available_datasets:
            self.query_one("#right_dataset_select", Select).focus()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle right dataset selection to populate right key column options."""
        if event.select.id == "right_dataset_select":
            right_dataset_id = event.value
            if right_dataset_id and right_dataset_id != Select.BLANK:
                # Convert to string to satisfy type checker
                dataset_id_str = str(right_dataset_id)
                # Populate right key columns if available
                if dataset_id_str in self.right_columns:
                    right_key_select = self.query_one("#right_key_select", Select)
                    right_key_select.set_options(
                        [(col, col) for col in self.right_columns[dataset_id_str]]
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "apply_button":
            self._apply_join()
        elif event.button.id == "cancel_button":
            self.action_dismiss()

    def _apply_join(self) -> None:
        """Validate inputs and post JoinRequested message."""
        right_dataset_select = self.query_one("#right_dataset_select", Select)
        left_key_select = self.query_one("#left_key_select", Select)
        right_key_select = self.query_one("#right_key_select", Select)
        join_type_radio = self.query_one("#join_type_radio", RadioSet)
        left_suffix_input = self.query_one("#left_suffix_input", Input)
        right_suffix_input = self.query_one("#right_suffix_input", Input)

        # Validation - check if only 1 dataset loaded
        if not self.available_datasets:
            self.app.notify(
                "Need at least 2 datasets loaded to perform join", severity="warning"
            )
            return

        # Validation - check if right dataset is selected
        right_dataset = right_dataset_select.value
        if not right_dataset or right_dataset == Select.BLANK:
            self.app.notify("Please select a dataset to join with", severity="warning")
            right_dataset_select.focus()
            return

        # Validation - check if left key is selected
        left_key = left_key_select.value
        if not left_key or left_key == Select.BLANK:
            self.app.notify("Please select left key column", severity="warning")
            left_key_select.focus()
            return

        # Validation - check if right key is selected
        right_key = right_key_select.value
        if not right_key or right_key == Select.BLANK:
            self.app.notify("Please select right key column", severity="warning")
            right_key_select.focus()
            return

        # Get selected join type from radio buttons
        join_type = "inner"  # Default
        for join_id, _ in self.JOIN_TYPES:
            radio_button = self.query_one(f"#join_type_{join_id}", RadioButton)
            if radio_button.value:
                join_type = join_id
                break

        # Get optional suffixes
        left_suffix = left_suffix_input.value.strip()
        right_suffix = right_suffix_input.value.strip()

        # Default suffixes if not provided
        if not left_suffix:
            left_suffix = "_left"
        if not right_suffix:
            right_suffix = "_right"

        # Post JoinRequested message
        # Convert values to strings for type safety
        self.post_message(
            self.JoinRequested(
                right_dataset=str(right_dataset),
                left_key=str(left_key),
                right_key=str(right_key),
                join_type=join_type,
                left_suffix=left_suffix,
                right_suffix=right_suffix,
            )
        )

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

        # Update datasets and columns if needed
        if self.available_datasets:
            right_dataset_select = self.query_one("#right_dataset_select", Select)
            right_dataset_select.set_options(
                [(name, dataset_id) for name, dataset_id in self.available_datasets]
            )

        if self.left_columns:
            left_key_select = self.query_one("#left_key_select", Select)
            left_key_select.set_options([(col, col) for col in self.left_columns])

        # Reset radio buttons to inner join
        for join_id, _ in self.JOIN_TYPES:
            radio_button = self.query_one(f"#join_type_{join_id}", RadioButton)
            radio_button.value = join_id == "inner"

        # Clear suffix inputs
        left_suffix_input = self.query_one("#left_suffix_input", Input)
        right_suffix_input = self.query_one("#right_suffix_input", Input)
        left_suffix_input.value = ""
        right_suffix_input.value = ""

        # Clear right key select
        right_key_select = self.query_one("#right_key_select", Select)
        right_key_select.set_options([])

        self.focus()

    def update_datasets(
        self,
        left_dataset_name: str,
        left_columns: list[str],
        available_datasets: list[tuple[str, str]],
    ) -> None:
        """Update available datasets and columns for join.

        Args:
            left_dataset_name: Name of the left (current/active) dataset
            left_columns: List of column names from left dataset
            available_datasets: List of (name, id) tuples for other loaded datasets

        """
        self.left_dataset_name = left_dataset_name
        self.left_columns = left_columns
        self.available_datasets = available_datasets

        if self.is_mounted:
            # Update left dataset label
            label = self.query_one(".form-label", Label)
            label.update(f"Current dataset: {self.left_dataset_name}")

            # Update right dataset options
            right_dataset_select = self.query_one("#right_dataset_select", Select)
            right_dataset_select.set_options(
                [(name, dataset_id) for name, dataset_id in self.available_datasets]
            )

            # Update left key options
            left_key_select = self.query_one("#left_key_select", Select)
            left_key_select.set_options([(col, col) for col in self.left_columns])

    def update_right_columns(self, dataset_id: str, columns: list[str]) -> None:
        """Update columns for a specific right dataset.

        Args:
            dataset_id: ID of the right dataset
            columns: List of column names from that dataset

        """
        self.right_columns[dataset_id] = columns
