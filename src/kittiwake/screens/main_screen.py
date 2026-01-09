"""Main screen for data exploration."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..models.dataset_session import DatasetSession
from ..models.operations import Operation
from ..utils.keybindings import KeybindingsRegistry
from ..widgets import DatasetTable, DatasetTabs, HelpOverlay
from ..widgets.sidebars import FilterSidebar, OperationsSidebar, SearchSidebar


class MainScreen(Screen):
    """Main data exploration screen with tabs and paginated table."""

    # Reactive variable for split pane mode
    split_pane_active = reactive(False)

    BINDINGS = [
        Binding("a", "aggregate", "Aggregate"),
        Binding("?", "help", "Help"),
        Binding("ctrl+s", "save_analysis", "Save"),
        Binding("ctrl+p", "toggle_split_pane", "Split Pane"),
        Binding("ctrl+f", "filter_data", "Filter"),
        Binding("ctrl+slash", "search_data", "Search"),
        Binding("tab", "next_dataset", "Next Dataset"),
        Binding("shift+tab", "prev_dataset", "Prev Dataset"),
        Binding("page_down", "next_page", "Next Page", show=False),
        Binding("page_up", "prev_page", "Prev Page", show=False),
        Binding("ctrl+w", "close_dataset", "Close"),
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
        self.operations_sidebar: OperationsSidebar | None = None

    def compose(self) -> ComposeResult:
        """Compose screen UI with sidebar architecture."""
        yield Header()

        # Left sidebars (overlay layer) - initially hidden
        yield FilterSidebar()
        yield SearchSidebar()

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

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        self.dataset_tabs = self.query_one("#dataset_tabs", DatasetTabs)
        self.dataset_table_left = self.query_one("#dataset_table_left", DatasetTable)
        self.dataset_table_right = self.query_one("#dataset_table_right", DatasetTable)
        self.filter_sidebar = self.query_one("#filter_sidebar", FilterSidebar)
        self.search_sidebar = self.query_one("#search_sidebar", SearchSidebar)
        self.operations_sidebar = self.query_one("#operations_sidebar", OperationsSidebar)

        # Load active dataset if one exists
        active_dataset = self.session.get_active_dataset()
        if active_dataset:
            self.dataset_table_left.load_dataset(active_dataset)
            # Refresh operations sidebar
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(active_dataset.operation_history)

    def watch_split_pane_active(self, active: bool) -> None:
        """React to split pane mode changes."""
        if self.dataset_table_right:
            if active:
                self.dataset_table_right.remove_class("hidden")
            else:
                self.dataset_table_right.add_class("hidden")

    def on_dataset_tabs_tab_changed(self, message: DatasetTabs.TabChanged) -> None:
        """Handle tab change - update table view."""
        active_dataset = self.session.get_active_dataset()

        # Always update left pane with active dataset
        if active_dataset and self.dataset_table_left:
            self.dataset_table_left.load_dataset(active_dataset)

    def on_dataset_tabs_tab_closed(self, message: DatasetTabs.TabClosed) -> None:
        """Handle tab close - update table view or show empty state."""
        active_dataset = self.session.get_active_dataset()
        if active_dataset and self.dataset_table_left:
            self.dataset_table_left.load_dataset(active_dataset)
        else:
            # No datasets left - show empty state
            if self.dataset_table_left:
                self.dataset_table_left.dataset = None
                self.dataset_table_left._update_status("No dataset loaded")
            # Disable split pane if no datasets
            if self.split_pane_active:
                self.action_toggle_split_pane()

    def action_toggle_split_pane(self) -> None:
        """Toggle split pane mode for side-by-side dataset comparison."""
        # Check if we have at least 2 datasets
        if len(self.session.datasets) < 2 and not self.split_pane_active:
            self.notify("Need at least 2 datasets for split pane mode", severity="warning")
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
            self.notify(
                f"Cannot enable split pane: {e}",
                severity="error"
            )
            return

        # Load datasets into both panes
        if self.dataset_table_left and self.dataset_table_right:
            self.dataset_table_left.load_dataset(dataset_1)
            self.dataset_table_right.load_dataset(dataset_2)

        self.split_pane_active = True
        self.notify("Split pane enabled (Ctrl+P to toggle)")

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
            self.notify("Dataset schema not available", severity="error")
            return

        columns = list(active_dataset.schema.keys())
        if not columns:
            self.notify("No columns available in dataset", severity="warning")
            return

        # Setup filter sidebar callback
        def handle_filter_result(params: dict) -> None:
            """Handle filter sidebar result."""
            # Build operation code using FilterModal helper for now
            # TODO: Move this logic to a service/builder class
            from ..widgets.modals.filter_modal import FilterModal
            modal = FilterModal(columns=columns)
            code, display, params_dict = modal._build_filter_operation(params)

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
                if self.dataset_table_left and self.dataset_table_left.dataset == active_dataset:
                    self.dataset_table_left.load_dataset(active_dataset)
                if self.split_pane_active and self.dataset_table_right and self.dataset_table_right.dataset == active_dataset:
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(active_dataset.operation_history)

            except Exception as e:
                self.notify(f"Filter operation failed: {e}", severity="error")

        # Show filter sidebar
        if self.filter_sidebar:
            self.filter_sidebar.update_columns(columns)
            self.filter_sidebar.callback = handle_filter_result
            self.filter_sidebar.show()

    def action_search_data(self) -> None:
        """Open SearchSidebar for full-text search (Ctrl+/)."""
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

            # Build operation using SearchModal helper with schema for smart type handling
            # TODO: Move this logic to a service/builder class
            from ..widgets.modals.search_modal import SearchModal
            modal = SearchModal()
            code, display, params_dict = modal._build_search_operation(
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
                if self.dataset_table_left and self.dataset_table_left.dataset == active_dataset:
                    self.dataset_table_left.load_dataset(active_dataset)
                if self.split_pane_active and self.dataset_table_right and self.dataset_table_right.dataset == active_dataset:
                    self.dataset_table_right.load_dataset(active_dataset)

                # Refresh operations sidebar
                if self.operations_sidebar:
                    self.operations_sidebar.refresh_operations(active_dataset.operation_history)

            except Exception as e:
                self.notify(f"Search operation failed: {e}", severity="error")

        # Show search sidebar
        if self.search_sidebar:
            self.search_sidebar.callback = handle_search_result
            self.search_sidebar.show()

    def action_aggregate(self) -> None:
        """Open aggregate modal."""
        # TODO: Implement aggregate modal
        self.notify("Aggregate modal not yet implemented")

    def action_save_analysis(self) -> None:
        """Save current analysis."""
        # TODO: Implement save analysis
        self.notify("Save analysis not yet implemented")

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

    def action_close_dataset(self) -> None:
        """Close active dataset."""
        if self.dataset_tabs:
            self.dataset_tabs.close_tab()
            self.notify("Dataset closed")

    def action_quit(self) -> None:
        """Quit application."""
        self.app.exit()

    def load_dataset(self, dataset) -> None:
        """Load a dataset into the view.

        Args:
            dataset: Dataset to load
        """
        # Add to session (respects 10-dataset limit)
        if not self.session.add_dataset(dataset):
            self.notify(
                f"Cannot load {dataset.name}: Maximum of {self.session.max_datasets} datasets reached. "
                "Close a dataset (Ctrl+W) before loading more.",
                severity="warning",
                timeout=5
            )
            return

        # Update tabs
        if self.dataset_tabs:
            self.dataset_tabs.add_dataset_tab()

        # Load into table directly
        if self.dataset_table_left:
            self.dataset_table_left.load_dataset(dataset)

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
                active_dataset.current_frame = op.apply(active_dataset.current_frame)

            # Refresh table
            if self.dataset_table_left and self.dataset_table_left.dataset == active_dataset:
                self.dataset_table_left.load_dataset(active_dataset)

            self.notify("Operations reordered and reapplied")

        except Exception as e:
            self.notify(f"Failed to reapply operations: {e}", severity="error")

    def on_operations_sidebar_operation_edit(
        self, message: OperationsSidebar.OperationEdit
    ) -> None:
        """Handle operation edit request from sidebar."""
        operation = message.operation

        # TODO: Reopen appropriate sidebar with operation params pre-filled
        # For now, just notify
        self.notify(f"Edit operation not yet implemented: {operation.display}", severity="information")

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
                active_dataset.current_frame = op.apply(active_dataset.current_frame)

            # Refresh table
            if self.dataset_table_left and self.dataset_table_left.dataset == active_dataset:
                self.dataset_table_left.load_dataset(active_dataset)

            # Refresh operations sidebar
            if self.operations_sidebar:
                self.operations_sidebar.refresh_operations(active_dataset.operation_history)

            self.notify(f"Removed: {message.operation.display}")

        except Exception as e:
            self.notify(f"Failed to reapply operations: {e}", severity="error")

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
        if self.dataset_table_left and self.dataset_table_left.dataset == active_dataset:
            self.dataset_table_left.load_dataset(active_dataset)

        # Refresh operations sidebar (will auto-hide)
        if self.operations_sidebar:
            self.operations_sidebar.refresh_operations([])

        self.notify("All operations cleared")

