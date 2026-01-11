"""Main screen for data exploration."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..models.dataset_session import DatasetAddResult, DatasetSession
from ..models.operations import Operation
from ..utils.keybindings import KeybindingsRegistry
from ..widgets import DatasetTable, DatasetTabs, HelpOverlay, SummaryPanel
from ..widgets.modals.mode_switch_modal import ModeSwitchPromptModal
from ..widgets.modals.save_analysis_modal import SaveAnalysisModal
from ..widgets.modals.save_workflow_modal import SaveWorkflowModal
from ..widgets.sidebars import (
    AggregateSidebar,
    FilterSidebar,
    JoinSidebar,
    OperationsSidebar,
    PivotSidebar,
    SearchSidebar,
)

if TYPE_CHECKING:
    from ..app import KittiwakeApp


class MainScreen(Screen):
    """Main data exploration screen with tabs and paginated table."""

    # Reactive variable for split pane mode
    split_pane_active = reactive(False)

    BINDINGS = [
        Binding("a", "aggregate", "Aggregate"),
        Binding("p", "pivot", "Pivot"),
        Binding("?", "help", "Help"),
        Binding("ctrl+s", "save_analysis", "Save"),
        Binding("ctrl+shift+s", "save_workflow", "Save Workflow"),
        Binding("ctrl+l", "load_analysis", "Load"),
        Binding("ctrl+d", "toggle_split_pane", "Split Pane"),
        Binding("ctrl+f", "filter_data", "Filter"),
        Binding(
            "ctrl+h", "search_data", "Search"
        ),  # Changed from ctrl+slash for French AZERTY Mac compatibility
        Binding("ctrl+j", "open_join_sidebar", "Join"),
        Binding("ctrl+e", "execute_next", "Execute Next"),
        Binding("ctrl+shift+e", "execute_all", "Execute All"),
        Binding("ctrl+m", "toggle_execution_mode", "Toggle Mode"),
        Binding("ctrl+r", "reload_dataset", "Reload"),
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+shift+z", "redo", "Redo"),
        Binding("ctrl+g", "toggle_summary_panel", "Results", show=False),
        Binding("tab", "next_dataset", "Next Dataset"),
        Binding("shift+tab", "prev_dataset", "Prev Dataset"),
        Binding("page_down", "next_page", "Next Page", show=False),
        Binding("page_up", "prev_page", "Prev Page", show=False),
        Binding("ctrl+w", "close_dataset", "Close"),
        Binding("ctrl+left", "scroll_columns_left", "←5 Cols", show=False),
        Binding("ctrl+right", "scroll_columns_right", "5 Cols→", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self, session: DatasetSession, keybindings: KeybindingsRegistry, **kwargs
    ):
        super().__init__(**kwargs)
        self.session = session
        self.keybindings = keybindings
        self.dataset_tabs: DatasetTabs | None = None
        self.dataset_table_left: DatasetTable | None = None
        self.dataset_table_right: DatasetTable | None = None
        self.filter_sidebar: FilterSidebar | None = None
        self.search_sidebar: SearchSidebar | None = None
        self.aggregate_sidebar: AggregateSidebar | None = None
        self.pivot_sidebar: PivotSidebar | None = None
        self.join_sidebar: JoinSidebar | None = None
        self.operations_sidebar: OperationsSidebar | None = None
        self.summary_panel: SummaryPanel | None = None

    @property
    def kittiwake_app(self) -> "KittiwakeApp":
        """Return the app instance with proper typing."""
        from ..app import KittiwakeApp  # noqa: F401

        return self.app  # type: ignore[return-value]

    def _get_all_operations(self, dataset) -> list:
        """Get all operations (executed + queued) for display in sidebar.

        Returns operations in order: executed operations first, then queued operations.
        """
        if not dataset:
            return []

        # Combine executed and queued operations
        all_ops = []

        # Add executed operations
        if hasattr(dataset, "executed_operations"):
            all_ops.extend(dataset.executed_operations)

        # Add queued operations
        if hasattr(dataset, "queued_operations"):
            all_ops.extend(dataset.queued_operations)

        return all_ops

    def _refresh_operations_sidebar_if_focused(self, dataset) -> None:
        """Refresh operations sidebar if the given dataset is currently focused.

        Args:
            dataset: The dataset whose operations may need refreshing
        """
        if not self.operations_sidebar or not dataset:
            return

        # Only refresh if this dataset is currently displayed in the sidebar
        if self.operations_sidebar.current_dataset_name == dataset.name:
            self.operations_sidebar.refresh_operations(
                self._get_all_operations(dataset)
            )

    def compose(self) -> ComposeResult:
        """Compose screen UI with sidebar architecture."""
        yield Header()

        # Left sidebars (overlay layer) - initially hidden
        yield FilterSidebar()
        yield SearchSidebar()
        yield AggregateSidebar()
        yield PivotSidebar()
        yield JoinSidebar()

        # Main content with tabs and table(s)
        with Vertical(id="main_container"):
            yield DatasetTabs(session=self.session, id="dataset_tabs")

            # Horizontal layout for data table + operations sidebar (push layout)
            with Horizontal(id="content_area"):
                # Single table view (default)
                yield DatasetTable(id="dataset_table_left")

                # Second table for split pane (initially hidden)
                yield DatasetTable(id="dataset_table_right", classes="hidden")

                # Right sidebar for operations history (push, initially hidden)
                yield OperationsSidebar()

        # Summary panel (overlay layer) - initially hidden
        yield SummaryPanel()

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        self.dataset_tabs = self.query_one("#dataset_tabs", DatasetTabs)
        self.dataset_table_left = self.query_one("#dataset_table_left", DatasetTable)
        self.dataset_table_right = self.query_one("#dataset_table_right", DatasetTable)
        self.filter_sidebar = self.query_one("#filter_sidebar", FilterSidebar)
        self.search_sidebar = self.query_one("#search_sidebar", SearchSidebar)
        self.aggregate_sidebar = self.query_one("#aggregate_sidebar", AggregateSidebar)
        self.pivot_sidebar = self.query_one("#pivot_sidebar", PivotSidebar)
        self.join_sidebar = self.query_one("#join_sidebar", JoinSidebar)
        self.operations_sidebar = self.query_one(
            "#operations_sidebar", OperationsSidebar
        )
        self.summary_panel = self.query_one("#summary_panel", SummaryPanel)

        # Load active dataset if one exists
        # Note: load_dataset() will trigger focus event which updates operations sidebar
        active_dataset = self.session.get_active_dataset()
        if active_dataset:
            self.dataset_table_left.load_dataset(active_dataset)

    def watch_split_pane_active(self, active: bool) -> None:
        """React to split pane mode changes."""
        if self.dataset_table_right:
            if active:
                self.dataset_table_right.remove_class("hidden")
            else:
                self.dataset_table_right.add_class("hidden")

    def on_dataset_tabs_tab_changed(self, message: DatasetTabs.TabChanged) -> None:
        """Handle tab change - update table view.

        Note: Operations sidebar will update automatically via focus event.
        """
        active_dataset = self.session.get_active_dataset()

        # Always update left pane with active dataset
        if active_dataset and self.dataset_table_left:
            self.dataset_table_left.load_dataset(active_dataset)

    def on_dataset_table_focus_gained(self, message: DatasetTable.FocusGained) -> None:
        """Handle table focus change - update operations sidebar.

        Args:
            message: FocusGained message with dataset reference
        """
        dataset = message.dataset

        if self.operations_sidebar and dataset:
            # Update execution mode for focused dataset
            self.operations_sidebar.execution_mode = (
                dataset.execution_mode if hasattr(dataset, "execution_mode") else "lazy"
            )

            # Update dataset name display
            self.operations_sidebar.current_dataset_name = dataset.name

            # Refresh operations for focused dataset
            self.operations_sidebar.refresh_operations(
                self._get_all_operations(dataset)
            )

    def on_dataset_tabs_tab_closed(self, message: DatasetTabs.TabClosed) -> None:
        """Handle tab close - update table view or show empty state."""
        active_dataset = self.session.get_active_dataset()
        if active_dataset and self.dataset_table_left:
            self.dataset_table_left.load_dataset(active_dataset)
            # Note: Operations sidebar will update via focus event
        else:
            # No datasets left - show empty state
            if self.dataset_table_left:
                self.dataset_table_left.dataset = None
                self.dataset_table_left._update_status("No dataset loaded")

            # Clear operations sidebar
            if self.operations_sidebar:
                self.operations_sidebar.current_dataset_name = None
                self.operations_sidebar.refresh_operations([])

            # Disable split pane if no datasets
            if self.split_pane_active:
                self.action_toggle_split_pane()

    def action_toggle_split_pane(self) -> None:
        """Toggle split pane mode for side-by-side dataset comparison."""
        # Check if we have at least 2 datasets
        if len(self.session.datasets) < 2 and not self.split_pane_active:
            self.notify(
                "Need at least 2 datasets for split pane mode", severity="warning"
            )
            return

        if not self.split_pane_active:
            # Enable split pane
            self._enable_split_pane()
        else:
            # Disable split pane
            self._disable_split_pane()

    def _enable_split_pane(self) -> None:
        """Enable split pane mode."""
        if len(self.session.datasets) < 2:
            return

        # Get first two datasets
        dataset_1 = self.session.datasets[0]
        dataset_2 = self.session.datasets[1]

        # Enable split pane in session
        try:
            self.session.enable_split_pane(dataset_1.id, dataset_2.id)
        except ValueError as e:
            self.notify(f"Cannot enable split pane: {e}", severity="error")
            return

        # Load datasets into both panes
        if self.dataset_table_left and self.dataset_table_right:
            self.dataset_table_left.load_dataset(dataset_1)
            self.dataset_table_right.load_dataset(dataset_2)

        self.split_pane_active = True
        self.notify("Split pane enabled (Ctrl+D to toggle)")

    def _disable_split_pane(self) -> None:
        """Disable split pane mode."""
        # Disable in session
        self.session.disable_split_pane()

        # Reload active dataset in left pane
        active_dataset = self.session.get_active_dataset()
        if active_dataset and self.dataset_table_left:
            self.dataset_table_left.load_dataset(active_dataset)

        self.split_pane_active = False
        self.notify("Split pane disabled")

    def action_filter_data(self) -> None:
        """Open FilterSidebar to build filter operation (Ctrl+F)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to filter", severity="warning")
            return

        # Get column names from the dataset
        if not active_dataset.schema:
            self.kittiwake_app.notify_error("Dataset schema not available")
            return

        columns = list(active_dataset.schema.keys())
        if not columns:
            self.notify("No columns available in dataset", severity="warning")
            return

        # Setup filter sidebar callback
        def handle_filter_result(params: dict) -> None:
            """Handle filter sidebar result."""
            # Build operation code using OperationBuilder
            from ..services.operation_builder import OperationBuilder

            code, display, params_dict = OperationBuilder.build_filter_operation(params)

            # Create Operation entity
            operation = Operation(
                code=code,
                display=display,
                operation_type="filter",
                params=params_dict,
            )

            # Add operation to dataset
            try:
                active_dataset.apply_operation(operation)
                self.notify(f"Applied: {display}")

                # Refresh the table to show filtered data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar with all operations (executed + queued)
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

            except Exception as e:
                self.kittiwake_app.notify_error(f"Filter operation failed: {e}")

        # Show filter sidebar
        if self.filter_sidebar:
            self.filter_sidebar.update_columns(columns)
            self.filter_sidebar.callback = handle_filter_result
            self.filter_sidebar.show()

    def action_search_data(self) -> None:
        """Open SearchSidebar for full-text search (Ctrl+H)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to search", severity="warning")
            return

        # Check schema availability
        if not active_dataset.schema:
            self.notify("Dataset schema not available", severity="warning")
            return

        # Get all columns - SearchModal will handle type filtering internally
        all_columns = list(active_dataset.schema.keys())

        if not all_columns:
            self.notify("No columns available for search", severity="warning")
            return

        # Setup search sidebar callback
        def handle_search_result(params: dict) -> None:
            """Handle search sidebar result."""
            query = params.get("query", "").strip()
            if not query:
                self.notify("Empty search query", severity="warning")
                return

            # Build operation using OperationBuilder with schema for smart type handling
            from ..services.operation_builder import OperationBuilder

            code, display, params_dict = OperationBuilder.build_search_operation(
                params, all_columns, active_dataset.schema
            )

            # Create Operation entity
            operation = Operation(
                code=code,
                display=display,
                operation_type="search",
                params=params_dict,
            )

            # Add operation to dataset
            try:
                active_dataset.apply_operation(operation)
                self.notify(f"Applied: {display}")

                # Refresh the table to show search results
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar with all operations (executed + queued)
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

            except Exception as e:
                self.kittiwake_app.notify_error(f"Search operation failed: {e}")

        # Show search sidebar
        if self.search_sidebar:
            self.search_sidebar.callback = handle_search_result
            self.search_sidebar.show()

    def action_aggregate(self) -> None:
        """Open AggregateSidebar to build aggregation operation (A key)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to aggregate", severity="warning")
            return

        # Get column names from the dataset
        if not active_dataset.schema:
            self.kittiwake_app.notify_error("Dataset schema not available")
            return

        columns = list(active_dataset.schema.keys())
        if not columns:
            self.notify("No columns available in dataset", severity="warning")
            return

        # Filter to only numerical columns for aggregation
        from ..services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in active_dataset.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        # Check if there are any numerical columns
        if not numerical_columns:
            self.notify(
                "Aggregation requires at least one numerical column",
                severity="warning",
            )
            return

        # Setup aggregate sidebar callback
        def handle_aggregate_result(params: dict) -> None:
            """Handle aggregate sidebar result."""
            # Import code generator
            from ..services.narwhals_ops import generate_aggregate_code

            # Convert params format from sidebar (agg_column, agg_functions list)
            # to format expected by generate_aggregate_code (agg_col, agg_func)
            code_params = {
                "agg_col": params["agg_column"],
                "agg_func": params["agg_functions"],
            }

            # Add group_by if provided
            if params.get("group_by"):
                code_params["group_by"] = params["group_by"]

            # Generate code and display string
            try:
                code, display = generate_aggregate_code(code_params)
            except ValueError as e:
                self.kittiwake_app.notify_error(f"Invalid aggregation parameters: {e}")
                return

            # Create Operation entity
            operation = Operation(
                code=code,
                display=display,
                operation_type="aggregate",
                params=params,
            )

            # Add operation to dataset
            try:
                active_dataset.apply_operation(operation)
                self.notify(f"Applied: {display}")

                # Refresh the table to show aggregated data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar with all operations (executed + queued)
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

                # Show aggregation results in SummaryPanel if in eager mode
                if active_dataset.execution_mode == "eager":
                    self._show_aggregation_results(active_dataset, display)

            except Exception as e:
                self.kittiwake_app.notify_error(f"Aggregate operation failed: {e}")

        # Show aggregate sidebar with filtered numerical columns
        if self.aggregate_sidebar:
            self.aggregate_sidebar.update_columns(numerical_columns)
            self.aggregate_sidebar.callback = handle_aggregate_result
            self.aggregate_sidebar.show()

    def _show_aggregation_results(self, dataset, operation_display: str) -> None:
        """Show aggregation results in SummaryPanel.

        Args:
            dataset: Dataset containing aggregation results
            operation_display: Human-readable operation description
        """
        if not self.summary_panel:
            return

        # Get current frame (contains aggregated data)
        frame = dataset.current_frame or dataset.frame
        if frame is None:
            self.notify("No data to display", severity="warning")
            return

        # Collect lazy frame to get concrete DataFrame
        try:
            collected_frame = frame.collect()
        except Exception as e:
            self.notify(f"Failed to collect aggregation results: {e}", severity="error")
            return

        # Convert DataFrame to list of dictionaries
        try:
            data_dicts = collected_frame.to_dict(as_series=False)
        except Exception as e:
            self.notify(f"Failed to convert aggregation results: {e}", severity="error")
            return

        # Show results in SummaryPanel
        self.summary_panel.show_results(data_dicts, operation_display)

    def action_pivot(self) -> None:
        """Open PivotSidebar to build pivot table operation (P key)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to pivot", severity="warning")
            return

        # Get column names from the dataset
        if not active_dataset.schema:
            self.kittiwake_app.notify_error("Dataset schema not available")
            return

        columns = list(active_dataset.schema.keys())
        if not columns:
            self.notify("No columns available in dataset", severity="warning")
            return

        # Filter to only numerical columns for pivot values
        from ..services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in active_dataset.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        # Check if there are any numerical columns for values
        if not numerical_columns:
            self.notify(
                "Pivot requires at least one numerical column for values",
                severity="warning",
            )
            return

        # Setup pivot sidebar callback
        def handle_pivot_result(params: dict) -> None:
            """Handle pivot sidebar result."""
            # Import code generator
            from ..services.narwhals_ops import generate_pivot_code

            # Generate code and display string
            try:
                code, display = generate_pivot_code(params)
            except ValueError as e:
                self.kittiwake_app.notify_error(f"Invalid pivot parameters: {e}")
                return

            # Create Operation entity
            operation = Operation(
                code=code,
                display=display,
                operation_type="pivot",
                params=params,
            )

            # Add operation to dataset
            try:
                active_dataset.apply_operation(operation)
                self.notify(f"Applied: {display}")

                # Refresh the table to show pivoted data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar with all operations (executed + queued)
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

            except Exception as e:
                self.kittiwake_app.notify_error(f"Pivot operation failed: {e}")

        # Show pivot sidebar with all columns for index/columns, numerical for values
        if self.pivot_sidebar:
            self.pivot_sidebar.update_columns(columns, value_columns=numerical_columns)
            self.pivot_sidebar.callback = handle_pivot_result
            self.pivot_sidebar.show()

    def action_open_join_sidebar(self) -> None:
        """Open JoinSidebar to build join operation (Ctrl+J)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to join", severity="warning")
            return

        # Check if we have at least 2 datasets loaded
        if len(self.session.datasets) < 2:
            self.notify(
                "Need at least 2 datasets loaded to perform join", severity="warning"
            )
            return

        # Get column names from the active dataset
        if not active_dataset.schema:
            self.kittiwake_app.notify_error("Dataset schema not available")
            return

        left_columns = list(active_dataset.schema.keys())
        if not left_columns:
            self.notify("No columns available in dataset", severity="warning")
            return

        # Get list of other datasets (exclude active dataset)
        available_datasets = [
            (ds.name, ds.id)
            for ds in self.session.datasets
            if ds.id != active_dataset.id
        ]

        if not available_datasets:
            self.notify("No other datasets available for join", severity="warning")
            return

        # Show join sidebar
        if self.join_sidebar:
            # Convert UUID to string for JoinSidebar compatibility
            available_datasets_str = [
                (ds_name, str(ds_id)) for ds_name, ds_id in available_datasets
            ]

            self.join_sidebar.update_datasets(
                left_dataset_name=active_dataset.name,
                left_columns=left_columns,
                available_datasets=available_datasets_str,
            )

            # Update right columns for each available dataset
            for _ds_name, ds_id in available_datasets:
                # Find dataset by ID
                dataset = next(
                    (ds for ds in self.session.datasets if ds.id == ds_id), None
                )
                if dataset and dataset.schema:
                    self.join_sidebar.update_right_columns(
                        str(ds_id), list(dataset.schema.keys())
                    )

            self.join_sidebar.show()

    def on_join_sidebar_join_requested(
        self, message: JoinSidebar.JoinRequested
    ) -> None:
        """Handle join request from sidebar with error handling."""
        # Get active (left) dataset
        left_dataset = self.session.get_active_dataset()
        if not left_dataset:
            self.notify("No active dataset for join", severity="error")
            return

        # Find right dataset by ID
        right_dataset = next(
            (ds for ds in self.session.datasets if ds.id == message.right_dataset), None
        )

        if not right_dataset:
            self.notify(
                f"Right dataset not found: {message.right_dataset}", severity="error"
            )
            return

        # Validate join keys exist in both datasets
        if not left_dataset.schema or not right_dataset.schema:
            self.kittiwake_app.notify_error(
                "Dataset schema not available for join validation"
            )
            return

        # Check if left key exists
        if message.left_key not in left_dataset.schema:
            self.notify(
                f"Left join key '{message.left_key}' not found in {left_dataset.name}",
                severity="error",
            )
            return

        # Check if right key exists
        if message.right_key not in right_dataset.schema:
            self.notify(
                f"Right join key '{message.right_key}' not found in {right_dataset.name}",
                severity="error",
            )
            return

        # Get column types for validation
        left_key_type = left_dataset.schema.get(message.left_key, "")
        right_key_type = right_dataset.schema.get(message.right_key, "")

        # Type compatibility check using validation function
        if left_key_type and right_key_type:
            from ..services.narwhals_ops import validate_join_key_types

            validation = validate_join_key_types(
                left_key_type, right_key_type, message.left_key, message.right_key
            )

            if not validation.is_compatible:
                self.notify(
                    f"Join failed: {validation.error_message}",
                    severity="error",
                    timeout=10,
                )
                return

            if validation.needs_conversion:
                self.notify(
                    f"Auto-converting {message.left_key} ({left_key_type}) → {right_key_type} for join compatibility",
                    severity="information",
                    timeout=5,
                )

        # Generate join code
        try:
            from ..services.narwhals_ops import generate_join_code

            # Prepare params for code generation
            join_params = {
                "right_dataset_id": message.right_dataset,
                "left_key": message.left_key,
                "right_key": message.right_key,
                "how": message.join_type,
                "left_suffix": message.left_suffix,
                "right_suffix": message.right_suffix,
            }

            # Add type information for automatic conversion
            if left_key_type and right_key_type:
                join_params["left_key_type"] = left_key_type
                join_params["right_key_type"] = right_key_type

            code, display = generate_join_code(join_params)

        except ValueError as e:
            self.kittiwake_app.notify_error(f"Invalid join parameters: {e}")
            return

        # Create Operation entity
        operation = Operation(
            code=code,
            display=display,
            operation_type="join",
            params=join_params,
        )

        # Add operation to dataset (will queue or execute based on execution mode)
        try:
            # Store reference to right dataset in params for execution
            operation.params["_right_dataset_obj"] = right_dataset

            left_dataset.apply_operation(operation)
            self.notify(f"Applied: {display}")

            # Refresh the table to show joined data
            if (
                self.dataset_table_left
                and self.dataset_table_left.dataset == left_dataset
            ):
                self.dataset_table_left.load_dataset(left_dataset)
            if (
                self.split_pane_active
                and self.dataset_table_right
                and self.dataset_table_right.dataset == left_dataset
            ):
                self.dataset_table_right.load_dataset(left_dataset)

            # Refresh operations sidebar with all operations (executed + queued)
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(
                    self._get_all_operations(left_dataset)
                )

        except Exception as e:
            self.kittiwake_app.notify_error(f"Join operation failed: {e}")

    def action_toggle_summary_panel(self) -> None:
        """Toggle SummaryPanel visibility (Ctrl+R)."""
        if not self.summary_panel:
            return

        # Check if panel is currently visible by checking for visible class
        if "visible" in self.summary_panel.classes:
            # Hide panel
            self.summary_panel.action_dismiss()
        else:
            # Try to show panel with current data
            active_dataset = self.session.get_active_dataset()
            if not active_dataset:
                self.notify("No active dataset to show results", severity="warning")
                return

            # Show with current aggregation results
            last_operation = (
                active_dataset.executed_operations[-1]
                if active_dataset.executed_operations
                else None
            )
            if last_operation and last_operation.operation_type == "aggregate":
                self._show_aggregation_results(active_dataset, last_operation.display)
            else:
                self.notify(
                    "No aggregation results to display. Run an aggregation first.",
                    severity="information",
                )

    def action_save_analysis(self) -> None:
        """Save current analysis."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()

        if not active_dataset:
            self.notify("No dataset loaded", severity="warning")
            return

        # Check if there are operations to save
        all_operations = self._get_all_operations(active_dataset)
        if not all_operations:
            self.notify("No operations to save", severity="warning")
            return

        # Show save modal
        def on_save_modal_result(result: dict | None) -> None:
            """Handle save modal result."""
            if result is None:
                return

            # Prepare analysis data
            analysis_data = {
                "name": result["name"],
                "description": result.get("description"),
                "dataset_path": active_dataset.source,
                "operation_count": len(all_operations),
                "operations": [
                    {
                        "operation_type": op.operation_type,
                        "display": op.display,
                        "code": op.code,
                        "params": op.params,
                    }
                    for op in all_operations
                ],
            }

            # Save to database
            try:
                from ..services.persistence import SavedAnalysisRepository

                repo = SavedAnalysisRepository()
                analysis_id, versioned_name = repo.save(analysis_data)

                if versioned_name:
                    # Name was auto-versioned due to duplicate
                    self.notify(
                        f"Analysis saved as '{versioned_name}' (ID: {analysis_id}) - original name was duplicate",
                        severity="information",
                    )
                else:
                    self.notify(
                        f"Analysis '{result['name']}' saved successfully (ID: {analysis_id})",
                        severity="information",
                    )
            except Exception as e:
                self.kittiwake_app.notify_error(f"Failed to save analysis: {e}")

        self.app.push_screen(SaveAnalysisModal(), on_save_modal_result)

    def action_save_workflow(self) -> None:
        """Save current operations as a reusable workflow (Ctrl+Shift+S)."""
        # Get active dataset
        active_dataset = self.session.get_active_dataset()

        if not active_dataset:
            self.notify("No dataset loaded", severity="warning")
            return

        # Check if there are operations to save
        all_operations = self._get_all_operations(active_dataset)
        if not all_operations:
            self.notify("No operations to save as workflow", severity="warning")
            return

        # Show save workflow modal
        def on_save_workflow_modal_result(result: dict | None) -> None:
            """Handle save workflow modal result."""
            if result is None:
                return

            # Save workflow to database
            try:
                from ..services.workflow import WorkflowService

                workflow_service = WorkflowService()
                workflow_id, versioned_name, error = workflow_service.save_workflow(
                    name=result["name"],
                    description=result.get("description"),
                    operations=all_operations,
                    include_schema=result.get("include_schema", True),
                    dataset_schema=active_dataset.schema
                    if result.get("include_schema", True)
                    else None,
                )

                if error:
                    self.kittiwake_app.notify_error(f"Failed to save workflow: {error}")
                    return

                if versioned_name:
                    # Name was auto-versioned due to duplicate
                    self.notify(
                        f"Workflow saved as '{versioned_name}' (ID: {workflow_id}) - original name was duplicate",
                        severity="information",
                    )
                else:
                    self.notify(
                        f"Workflow '{result['name']}' saved successfully (ID: {workflow_id})",
                        severity="information",
                    )
            except Exception as e:
                self.kittiwake_app.notify_error(f"Failed to save workflow: {e}")

        self.app.push_screen(SaveWorkflowModal(), on_save_workflow_modal_result)

    def action_load_analysis(self) -> None:
        """Load a saved analysis (Ctrl+L)."""
        from ..screens.saved_analyses_list_screen import SavedAnalysesListScreen

        def on_analyses_screen_result(result: dict | None) -> None:
            """Handle saved analyses list screen result."""
            if result is None:
                return

            action = result.get("action")
            analysis = result.get("analysis")

            if action == "load" and analysis:
                # Load the analysis
                self._load_saved_analysis(analysis)
            elif action == "edit" and analysis:
                # Edit analysis metadata
                self._edit_analysis_metadata(analysis)

        self.app.push_screen(SavedAnalysesListScreen(), on_analyses_screen_result)

    def _load_saved_analysis(self, analysis: dict) -> None:
        """Load a saved analysis into the current session.

        Args:
            analysis: Analysis data with operations to replay

        """
        dataset_path = analysis.get("dataset_path")
        operations = analysis.get("operations", [])
        analysis_name = analysis.get("name")

        if not dataset_path:
            self.notify("Analysis has no dataset path", severity="error")
            return

        from pathlib import Path

        # Check if dataset file exists
        if not Path(dataset_path).exists():
            # Show PathUpdateModal to let user specify new location
            from ..widgets.modals import PathUpdateModal

            def on_path_update(new_path: str | None) -> None:
                """Handle path update modal result."""
                if new_path:
                    # Updated path provided, proceed with new path
                    analysis["dataset_path"] = new_path
                    self._load_saved_analysis(analysis)
                else:
                    # User cancelled, don't load
                    self.notify("Analysis loading cancelled", severity="information")

            self.app.push_screen(
                PathUpdateModal(
                    analysis_name=analysis_name, original_path=dataset_path
                ),
                on_path_update,
            )
            return

        # Load dataset asynchronously
        async def load_and_apply():
            """Load dataset and apply saved operations asynchronously."""
            try:
                self.notify(f"Loading dataset for '{analysis_name}'...")

                # Load dataset
                from ..services.data_loader import DataLoader

                loader = DataLoader()
                dataset = await loader.load_from_source(dataset_path)

                # Add to session
                self.session.add_dataset(dataset)

                # Update UI
                if self.dataset_tabs:
                    self.dataset_tabs.add_dataset_tab()
                if self.dataset_table_left:
                    self.dataset_table_left.load_dataset(dataset)

                self.notify(f"Loaded dataset: {dataset.name}")

                # Apply operations
                if operations:
                    self.notify(f"Applying {len(operations)} operations...")

                    from ..models.operations import Operation

                    for op_data in operations:
                        operation = Operation(
                            code=op_data.get("code", ""),
                            display=op_data.get("display", ""),
                            operation_type=op_data.get("operation_type", ""),
                            params=op_data.get("params", {}),
                        )

                        # Apply operation
                        dataset.apply_operation(operation)

                    # Refresh table and operations sidebar
                    if self.dataset_table_left:
                        self.dataset_table_left.load_dataset(dataset)
                    if self.operations_sidebar:
                        self.operations_sidebar.refresh_operations(
                            self._get_all_operations(dataset)
                        )

                    self.notify(
                        f"✓ Loaded analysis '{analysis_name}' with {len(operations)} operations"
                    )
                else:
                    self.notify(f"✓ Loaded analysis '{analysis_name}' (no operations)")

            except Exception as e:
                self.kittiwake_app.notify_error(f"Failed to load analysis: {e}")

        # Run async load
        self.run_worker(load_and_apply(), exclusive=False)

    def _edit_analysis_metadata(self, analysis: dict) -> None:
        """Edit analysis metadata (name and description).

        Args:
            analysis: Analysis data to edit
        """
        analysis_id = analysis.get("id")
        if not analysis_id:
            self.notify("Invalid analysis ID", severity="error")
            return

        # Show save modal pre-filled with current values
        def on_edit_modal_result(result: dict | None) -> None:
            """Handle edit modal result."""
            if result is None:
                return

            # Update analysis in database
            async def update_analysis():
                """Update analysis asynchronously."""
                try:
                    from ..services.persistence import SavedAnalysisRepository

                    repo = SavedAnalysisRepository()

                    # Load full analysis to preserve operations
                    full_analysis = repo.load_by_id(analysis_id)
                    if not full_analysis:
                        self.notify("Analysis not found", severity="error")
                        return

                    # Update metadata
                    full_analysis["name"] = result["name"]
                    full_analysis["description"] = result.get("description")

                    # Save to database
                    success = repo.update(analysis_id, full_analysis)

                    if success:
                        self.notify(
                            f"Updated analysis '{result['name']}'",
                            severity="information",
                        )
                    else:
                        self.notify("Failed to update analysis", severity="error")

                except Exception as e:
                    self.kittiwake_app.notify_error(f"Failed to update analysis: {e}")

            # Run async update
            self.run_worker(update_analysis(), exclusive=False)

        self.app.push_screen(
            SaveAnalysisModal(
                default_name=analysis.get("name", ""),
                default_description=analysis.get("description", ""),
            ),
            on_edit_modal_result,
        )

    def action_reload_dataset(self) -> None:
        """Reload dataset from source file and re-apply operations (Ctrl+R)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset to reload", severity="warning")
            return

        source_path = active_dataset.source
        if not source_path:
            self.notify("Dataset has no source path", severity="error")
            return

        # Preserve current operations
        all_operations = self._get_all_operations(active_dataset)
        dataset_name = active_dataset.name
        dataset_id = active_dataset.id
        execution_mode = active_dataset.execution_mode

        # Reload dataset asynchronously
        async def reload_and_reapply():
            """Reload dataset and reapply operations asynchronously."""
            try:
                self.notify(f"Reloading dataset '{dataset_name}'...")

                # Load fresh data from source
                from pathlib import Path

                from ..services.data_loader import DataLoader

                loader = DataLoader()

                # Check if source file exists
                if source_path.startswith(("http://", "https://")):
                    # Remote URL - just try to load
                    pass
                else:
                    # Local file - check existence
                    if not Path(source_path).exists():
                        self.kittiwake_app.notify_error(
                            f"Source file not found: {source_path}\n"
                            "The file may have been moved or deleted."
                        )
                        return

                # Load dataset
                new_dataset = await loader.load_from_source(source_path)

                # Preserve original ID and name
                new_dataset.id = dataset_id
                new_dataset.name = dataset_name
                new_dataset.execution_mode = execution_mode

                # Check schema compatibility if we have operations
                if all_operations:
                    # Check if all referenced columns still exist
                    old_schema = active_dataset.schema
                    new_schema = new_dataset.schema

                    missing_columns = set(old_schema.keys()) - set(new_schema.keys())
                    if missing_columns:
                        self.notify(
                            f"Warning: Schema changed - missing columns: {', '.join(missing_columns)}",
                            severity="warning",
                            timeout=8,
                        )

                # Replace dataset in session (keeping same position)
                dataset_index = self.session.datasets.index(active_dataset)
                self.session.datasets[dataset_index] = new_dataset

                # Re-apply operations
                if all_operations:
                    self.notify(f"Re-applying {len(all_operations)} operations...")

                    from ..models.operations import Operation

                    failed_ops = []
                    for op_data in all_operations:
                        # Recreate operation
                        if isinstance(op_data, Operation):
                            operation = op_data
                        else:
                            operation = Operation(
                                code=op_data.get("code", ""),
                                display=op_data.get("display", ""),
                                operation_type=op_data.get("operation_type", ""),
                                params=op_data.get("params", {}),
                            )

                        # Apply operation
                        try:
                            new_dataset.apply_operation(operation)
                        except Exception as e:
                            failed_ops.append((operation.display, str(e)))

                    if failed_ops:
                        error_msg = "\n".join(
                            [f"- {op}: {err}" for op, err in failed_ops]
                        )
                        self.notify(
                            f"Some operations failed:\n{error_msg}",
                            severity="warning",
                            timeout=10,
                        )

                # Refresh UI
                if self.dataset_table_left:
                    self.dataset_table_left.load_dataset(new_dataset)
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(new_dataset)
                    )

                if all_operations:
                    self.notify(
                        f"✓ Reloaded '{dataset_name}' with {len(all_operations)} operations"
                    )
                else:
                    self.notify(f"✓ Reloaded '{dataset_name}'")

            except FileNotFoundError:
                self.kittiwake_app.notify_error(
                    f"Source file not found: {source_path}\n"
                    "The file may have been moved or deleted."
                )
            except Exception as e:
                self.kittiwake_app.notify_error(f"Failed to reload dataset: {e}")

        # Run async reload
        self.run_worker(reload_and_reapply(), exclusive=False)

    def action_help(self) -> None:
        """Show help overlay."""
        self.app.push_screen(
            HelpOverlay(screen_name="main", keybindings=self.keybindings)
        )

    def action_next_dataset(self) -> None:
        """Switch to next dataset."""
        if self.dataset_tabs:
            if not self.dataset_tabs.next_tab():
                self.notify("No other datasets available")

    def action_prev_dataset(self) -> None:
        """Switch to previous dataset."""
        if self.dataset_tabs:
            if not self.dataset_tabs.previous_tab():
                self.notify("No other datasets available")

    def action_next_page(self) -> None:
        """Navigate to next page of data."""
        if self.dataset_table_left:
            if self.dataset_table_left.next_page():
                self.notify("Next page")

    def action_prev_page(self) -> None:
        """Navigate to previous page of data."""
        if self.dataset_table_left:
            if self.dataset_table_left.previous_page():
                self.notify("Previous page")

    def action_scroll_columns_left(self) -> None:
        """Scroll 5 columns to the left (Ctrl+Left)."""
        if self.dataset_table_left:
            if self.dataset_table_left.scroll_columns(-1):
                pass

    def action_scroll_columns_right(self) -> None:
        """Scroll 5 columns to the right (Ctrl+Right)."""
        if self.dataset_table_left:
            if self.dataset_table_left.scroll_columns(1):
                pass

    def action_close_dataset(self) -> None:
        """Close active dataset."""
        if self.dataset_tabs:
            self.dataset_tabs.close_tab()
            self.notify("Dataset closed")

    def action_quit(self) -> None:
        """Quit application."""
        self.app.exit()

    def action_execute_next(self) -> None:
        """Execute next queued operation (Ctrl+E)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return

        # Check if in eager mode
        if (
            hasattr(active_dataset, "execution_mode")
            and active_dataset.execution_mode == "eager"
        ):
            self.notify(
                "No queued operations (eager mode active)", severity="information"
            )
            return

        # Check if there are queued operations
        if (
            not hasattr(active_dataset, "queued_operations")
            or not active_dataset.queued_operations
        ):
            self.notify("No queued operations to execute", severity="information")
            return

        # Execute next operation
        try:
            success = active_dataset.execute_next_queued()
            if success:
                # Refresh table to show updated data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

                # Check if last executed operation was an aggregation
                if active_dataset.executed_operations:
                    last_operation = active_dataset.executed_operations[-1]
                    if last_operation.operation_type == "aggregate":
                        self._show_aggregation_results(
                            active_dataset, last_operation.display
                        )

                executed_count = len(active_dataset.executed_operations)
                queued_count = len(active_dataset.queued_operations)
                self.notify(
                    f"Executed operation (✓ {executed_count}, ⏳ {queued_count} remaining)"
                )
            else:
                self.notify("No queued operations to execute", severity="information")
        except Exception as e:
            self.kittiwake_app.notify_error(f"Operation execution failed: {e}")
            # Refresh sidebar to show failed state
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(
                    self._get_all_operations(active_dataset)
                )

    def action_execute_all(self) -> None:
        """Execute all queued operations (Ctrl+Shift+E)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return

        # Check if in eager mode
        if (
            hasattr(active_dataset, "execution_mode")
            and active_dataset.execution_mode == "eager"
        ):
            self.notify(
                "No queued operations (eager mode active)", severity="information"
            )
            return

        # Check if there are queued operations
        if (
            not hasattr(active_dataset, "queued_operations")
            or not active_dataset.queued_operations
        ):
            self.notify("No queued operations to execute", severity="information")
            return

        # Execute all operations
        total_queued = len(active_dataset.queued_operations)
        try:
            count = active_dataset.execute_all_queued()

            # Refresh table to show updated data
            if (
                self.dataset_table_left
                and self.dataset_table_left.dataset == active_dataset
            ):
                self.dataset_table_left.load_dataset(active_dataset)
            if (
                self.split_pane_active
                and self.dataset_table_right
                and self.dataset_table_right.dataset == active_dataset
            ):
                self.dataset_table_right.load_dataset(active_dataset)

            # Refresh operations sidebar
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(
                    self._get_all_operations(active_dataset)
                )

            # Check if last executed operation was an aggregation
            if active_dataset.executed_operations:
                last_operation = active_dataset.executed_operations[-1]
                if last_operation.operation_type == "aggregate":
                    self._show_aggregation_results(
                        active_dataset, last_operation.display
                    )

            if count == total_queued:
                self.notify(f"✓ Executed all {count} operations successfully")
            else:
                remaining = len(active_dataset.queued_operations)
                self.notify(
                    f"Executed {count} of {total_queued} operations ({remaining} failed/remaining)",
                    severity="warning",
                )
        except Exception as e:
            self.kittiwake_app.notify_error(f"Operation execution failed: {e}")
            # Refresh sidebar to show failed state
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(
                    self._get_all_operations(active_dataset)
                )

    def action_undo(self) -> None:
        """Undo last executed operation (Ctrl+Z)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return

        # Check if there are operations to undo
        has_executed = (
            hasattr(active_dataset, "executed_operations")
            and active_dataset.executed_operations
        )
        has_legacy = (
            hasattr(active_dataset, "operation_history")
            and active_dataset.operation_history
        )

        if not has_executed and not has_legacy:
            self.notify("No operations to undo", severity="information")
            return

        # Undo operation
        try:
            success = active_dataset.undo()
            if success:
                # Refresh table to show updated data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

                executed_count = (
                    len(active_dataset.executed_operations)
                    if has_executed
                    else len(active_dataset.operation_history)
                )
                redo_count = (
                    len(active_dataset.redo_stack)
                    if hasattr(active_dataset, "redo_stack")
                    else 0
                )
                self.notify(
                    f"Undone (✓ {executed_count} executed, ↶ {redo_count} can redo)"
                )
            else:
                self.notify("Failed to undo operation", severity="error")
        except Exception as e:
            self.kittiwake_app.notify_error(f"Undo failed: {e}")

    def action_redo(self) -> None:
        """Redo previously undone operation (Ctrl+Shift+Z)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return

        # Check if there are operations to redo
        if not hasattr(active_dataset, "redo_stack") or not active_dataset.redo_stack:
            self.notify("No operations to redo", severity="information")
            return

        # Redo operation
        try:
            success = active_dataset.redo()
            if success:
                # Refresh table to show updated data
                if (
                    self.dataset_table_left
                    and self.dataset_table_left.dataset == active_dataset
                ):
                    self.dataset_table_left.load_dataset(active_dataset)
                if (
                    self.split_pane_active
                    and self.dataset_table_right
                    and self.dataset_table_right.dataset == active_dataset
                ):
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

                executed_count = len(active_dataset.executed_operations)
                redo_count = len(active_dataset.redo_stack)
                self.notify(
                    f"Redone (✓ {executed_count} executed, ↶ {redo_count} can redo)"
                )
            else:
                self.notify("Failed to redo operation", severity="error")
        except Exception as e:
            self.kittiwake_app.notify_error(f"Redo failed: {e}")

    def action_toggle_execution_mode(self) -> None:
        """Toggle execution mode between lazy and eager (Ctrl+M)."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return

        current_mode = (
            active_dataset.execution_mode
            if hasattr(active_dataset, "execution_mode")
            else "lazy"
        )
        new_mode = "eager" if current_mode == "lazy" else "lazy"

        # Check if switching from lazy to eager with queued operations
        has_queued = (
            hasattr(active_dataset, "queued_operations")
            and len(active_dataset.queued_operations) > 0
        )

        if current_mode == "lazy" and new_mode == "eager" and has_queued:
            # Show modal to ask what to do with queued operations
            queued_count = len(active_dataset.queued_operations)

            def on_mode_switch_result(choice: str | None) -> None:
                """Handle mode switch modal result."""
                if choice is None:
                    # User cancelled
                    return

                if choice == "execute":
                    # Execute all queued operations
                    try:
                        count = active_dataset.execute_all_queued()
                        self.notify(
                            f"Executed {count} operations, switched to EAGER mode"
                        )

                        # Refresh table
                        if self.dataset_table_left:
                            self.dataset_table_left.load_dataset(active_dataset)
                    except Exception as e:
                        self.kittiwake_app.notify_error(
                            f"Failed to execute operations: {e}"
                        )
                        return

                elif choice == "clear":
                    # Clear queued operations
                    active_dataset.clear_queued()
                    self.notify("Cleared queued operations, switched to EAGER mode")

                # Switch mode
                active_dataset.execution_mode = new_mode

                # Update sidebar mode indicator
                if self.operations_sidebar:
                    self.operations_sidebar.execution_mode = new_mode
                    self.operations_sidebar.refresh_operations(
                        self._get_all_operations(active_dataset)
                    )

            self.app.push_screen(
                ModeSwitchPromptModal(queued_count=queued_count), on_mode_switch_result
            )
        else:
            # No queued operations or switching to lazy, just switch
            active_dataset.execution_mode = new_mode

            # Update sidebar mode indicator
            if self.operations_sidebar:
                self.operations_sidebar.execution_mode = new_mode
                self.operations_sidebar.refresh_operations(
                    self._get_all_operations(active_dataset)
                )

            mode_name = "EAGER" if new_mode == "eager" else "LAZY"
            self.notify(f"Switched to {mode_name} mode")

    def load_dataset(self, dataset) -> None:
        """Load a dataset into the view.

        Args:
            dataset: Dataset to load

        """
        # Add to session (respects 10-dataset limit)
        result = self.session.add_dataset(dataset)

        # Handle different result statuses
        if result == DatasetAddResult.ERROR_AT_LIMIT:
            self.notify(
                f"Cannot load {dataset.name}: Maximum of {self.session.max_datasets} datasets reached. "
                "Close a dataset (Ctrl+W) before loading more.",
                severity="error",
                timeout=5,
            )
            return

        # Update tabs
        if self.dataset_tabs:
            self.dataset_tabs.add_dataset_tab()

        # Load into table directly
        if self.dataset_table_left:
            self.dataset_table_left.load_dataset(dataset)

        # Show appropriate notification based on result
        if result == DatasetAddResult.WARNING_8_DATASETS:
            self.notify(
                f"Loaded: {dataset.name} | Approaching limit: 8/{self.session.max_datasets} datasets loaded",
                severity="warning",
                timeout=4,
            )
        elif result == DatasetAddResult.WARNING_9_DATASETS:
            self.notify(
                f"Loaded: {dataset.name} | Almost at limit: 9/{self.session.max_datasets} datasets. One slot remaining.",
                severity="warning",
                timeout=5,
            )
        else:
            self.notify(f"Loaded: {dataset.name}")

    # OperationsSidebar message handlers

    def on_operations_sidebar_operations_reordered(
        self, message: OperationsSidebar.OperationsReordered
    ) -> None:
        """Handle operations reordering from sidebar."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            return

        # Update dataset operation history
        active_dataset.operation_history = message.operations

        # Reapply all operations from scratch
        try:
            # Reset to original frame
            active_dataset.current_frame = active_dataset.original_frame

            # Reapply all operations in new order
            for op in active_dataset.operation_history:
                if active_dataset.current_frame is None:
                    raise ValueError("Current frame is None, cannot apply operation")
                active_dataset.current_frame = op.apply(active_dataset.current_frame)

            # Refresh table
            if (
                self.dataset_table_left
                and self.dataset_table_left.dataset == active_dataset
            ):
                self.dataset_table_left.load_dataset(active_dataset)

            self.notify("Operations reordered and reapplied")

        except Exception as e:
            self.kittiwake_app.notify_error(f"Failed to reapply operations: {e}")

    def on_operations_sidebar_operation_edit(
        self, message: OperationsSidebar.OperationEdit
    ) -> None:
        """Handle operation edit request from sidebar."""
        operation = message.operation

        # TODO: Reopen appropriate sidebar with operation params pre-filled
        # For now, just notify
        self.notify(
            f"Edit operation not yet implemented: {operation.display}",
            severity="information",
        )

    def on_operations_sidebar_operation_removed(
        self, message: OperationsSidebar.OperationRemoved
    ) -> None:
        """Handle operation removal from sidebar."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            return

        # Remove from dataset history (already removed from sidebar)
        try:
            active_dataset.operation_history.remove(message.operation)
        except ValueError:
            pass

        # Reapply all remaining operations
        try:
            # Reset to original frame
            active_dataset.current_frame = active_dataset.original_frame

            # Reapply all remaining operations
            for op in active_dataset.operation_history:
                if active_dataset.current_frame is None:
                    raise ValueError("Current frame is None, cannot apply operation")
                active_dataset.current_frame = op.apply(active_dataset.current_frame)

            # Refresh table
            if (
                self.dataset_table_left
                and self.dataset_table_left.dataset == active_dataset
            ):
                self.dataset_table_left.load_dataset(active_dataset)

            # Refresh operations sidebar
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(
                    active_dataset.operation_history
                )

            self.notify(f"Removed: {message.operation.display}")

        except Exception as e:
            self.kittiwake_app.notify_error(f"Failed to reapply operations: {e}")

    def on_operations_sidebar_operations_clear_all(
        self, message: OperationsSidebar.OperationsClearAll
    ) -> None:
        """Handle clear all operations request from sidebar."""
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            return

        # Clear all operations
        active_dataset.operation_history = []
        active_dataset.current_frame = active_dataset.original_frame

        # Refresh table
        if (
            self.dataset_table_left
            and self.dataset_table_left.dataset == active_dataset
        ):
            self.dataset_table_left.load_dataset(active_dataset)

        # Refresh operations sidebar (will auto-hide)
        if self.operations_sidebar:
            self.operations_sidebar.refresh_operations([])

        self.notify("All operations cleared")

    def on_dataset_table_quick_filter_requested(
        self, message: DatasetTable.QuickFilterRequested
    ) -> None:
        """Handle quick filter request from column header click.

        Args:
            message: QuickFilterRequested message with filter data

        """
        from ..services.operation_builder import OperationBuilder
        from ..utils.type_colors import map_operator_to_symbol

        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            return

        filter_data = message.filter_data

        # Map display operator to symbol (e.g., "equals (=)" -> "==")
        filter_data["operator"] = map_operator_to_symbol(filter_data["operator"])

        # Build operation using OperationBuilder
        try:
            code, display, params_dict = OperationBuilder.build_filter_operation(
                filter_data
            )

            # Create Operation entity
            operation = Operation(
                code=code,
                display=display,
                operation_type="filter",
                params=params_dict,
            )

            # Add operation to dataset
            active_dataset.apply_operation(operation)
            self.notify(f"Applied: {display}")

            # Refresh the table to show filtered data
            if (
                self.dataset_table_left
                and self.dataset_table_left.dataset == active_dataset
            ):
                self.dataset_table_left.load_dataset(active_dataset)
            if (
                self.split_pane_active
                and self.dataset_table_right
                and self.dataset_table_right.dataset == active_dataset
            ):
                self.dataset_table_right.load_dataset(active_dataset)

            # Refresh operations sidebar with all operations (executed + queued)
            self._refresh_operations_sidebar_if_focused(active_dataset)

        except Exception as e:
            self.kittiwake_app.notify_error(f"Quick filter failed: {e}")

    def on_operations_sidebar_mode_toggle_requested(
        self, message: OperationsSidebar.ModeToggleRequested
    ) -> None:
        """Handle mode toggle request from sidebar button."""
        # Delegate to action method
        self.action_toggle_execution_mode()
