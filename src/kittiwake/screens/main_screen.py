"""Main screen for data exploration."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive

from ..models.dataset_session import DatasetSession
from ..utils.keybindings import KeybindingsRegistry
from ..widgets import DatasetTable, DatasetTabs, HelpOverlay


class MainScreen(Screen):
    """Main data exploration screen with tabs and paginated table."""

    # Reactive variable for split pane mode
    split_pane_active = reactive(False)

    BINDINGS = [
        Binding("f", "filter", "Filter"),
        Binding("a", "aggregate", "Aggregate"),
        Binding("?", "help", "Help"),
        Binding("ctrl+s", "save_analysis", "Save"),
        Binding("ctrl+p", "toggle_split_pane", "Split Pane"),
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

    def compose(self) -> ComposeResult:
        """Compose screen UI."""
        yield Header()

        with Vertical(id="main_container"):
            yield DatasetTabs(session=self.session, id="dataset_tabs")
            
            # Single table view (default)
            yield DatasetTable(id="dataset_table_left")
            
            # Second table for split pane (initially hidden)
            yield DatasetTable(id="dataset_table_right", classes="hidden")

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        self.dataset_tabs = self.query_one("#dataset_tabs", DatasetTabs)
        self.dataset_table_left = self.query_one("#dataset_table_left", DatasetTable)
        self.dataset_table_right = self.query_one("#dataset_table_right", DatasetTable)

        # Load active dataset if one exists
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
            self.notify(f"Cannot enable split pane: {e}", severity="error")
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

    def action_filter(self) -> None:
        """Open filter modal."""
        # TODO: Implement filter modal
        self.notify("Filter modal not yet implemented")

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
