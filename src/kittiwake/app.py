"""Main Textual application for Kittiwake TUI data explorer."""

import asyncio
import time
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive

from .models.dataset import Dataset
from .screens.main_screen import MainScreen
from .services.data_loader import DataLoader
from .utils.keybindings import KeybindingsRegistry
from .widgets import HELP_OVERLAY_CSS


class KittiwakeApp(App):
    """Main Kittiwake application."""

    # Reactive variable to track loading state
    loading = reactive(False)
    loading_message = reactive("")

    CSS = (
        """
    Screen {
        background: $surface;
        layers: base overlay;
    }

    /* Main container and content area */
    #main_container {
        height: 1fr;
    }

    #content_area {
        height: 1fr;
    }

    #dataset_tabs {
        height: auto;
        background: $panel;
        padding: 1;
    }

    /* Data tables */
    DatasetTable {
        height: 1fr;
    }

    #dataset_table_left {
        height: 1fr;
    }

    #dataset_table_right {
        height: 1fr;
    }

    #dataset_table_right.hidden {
        display: none;
    }

    DatasetTable DataTable {
        height: 1fr;
    }

    DatasetTable Label {
        height: auto;
        padding: 0 1;
    }

    /* Left sidebars (overlay layer) */
    .sidebar {
        height: 100%;
        background: $panel-darken-1;
        border-right: solid $accent;
        opacity: 95%;
        padding: 1;
    }

    #filter_sidebar, #search_sidebar, #aggregate_sidebar, #pivot_sidebar, #join_sidebar {
        layer: overlay;
        dock: left;
        width: 30%;
        display: none;
    }

    #filter_sidebar.visible, #search_sidebar.visible, #aggregate_sidebar.visible, #pivot_sidebar.visible, #join_sidebar.visible {
        display: block;
    }

    #filter_sidebar.hidden, #search_sidebar.hidden, #aggregate_sidebar.hidden, #pivot_sidebar.hidden, #join_sidebar.hidden {
        display: none;
    }

    /* Sidebar styling */
    .sidebar-title {
        text-style: bold;
        padding: 1;
        background: $accent;
        color: $text;
        margin-bottom: 1;
    }

    .form-group {
        padding: 1 0;
        margin: 1 0;
    }

    .form-label {
        margin-bottom: 0;
        text-style: bold;
        color: $text;
    }

    .button-row {
        padding: 1 0;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    .button-row Button {
        margin: 0 1;
    }

    /* Value section styling for pivot sidebar */
    #value_sections_container {
        height: auto;
        min-height: 10;
    }

    .value-section-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        padding: 1 0;
        margin-top: 1;
    }

    .value-section {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
        background: $panel-darken-2;
        height: auto;
        max-height: 30;
        overflow-y: auto;
    }

    .value-section Label {
        margin: 1 0;
    }

    .value-section Select {
        margin: 0 0 1 0;
    }

    .value-section Checkbox {
        margin: 0 0 0 1;
    }

    .value-section Button {
        width: 100%;
        margin-top: 1;
    }

    #add_value_button {
        width: 100%;
        margin: 1 0;
    }

    /* Right sidebar (operations history - push layout, always visible) */
    #operations_sidebar {
        width: 25%;
        height: 100%;
        background: $panel-darken-1;
        border-left: solid $accent;
        padding: 1;
    }

    .sidebar-status {
        text-align: center;
        color: $text-muted;
        padding: 1;
        text-style: italic;
    }

    .dataset-label {
        color: $text-muted;
        text-style: italic;
        padding: 0 1;
        margin-bottom: 1;
        background: $panel-darken-2;
        text-align: center;
    }

    .mode-toggle-button {
        width: 100%;
        margin: 1 0;
    }

    #operations_list {
        height: 1fr;
    }

    /* Footer */
    Footer {
        background: $panel;
    }

    .loading-indicator {
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
    }

    /* Column type colors - using Textual semantic variables */
    DataTable .column-type-numeric {
        color: $primary;
        text-style: bold;
    }

    DataTable .column-type-text {
        color: $success;
        text-style: bold;
    }

    DataTable .column-type-date {
        color: $warning;
        text-style: bold;
    }

    DataTable .column-type-boolean {
        color: $accent;
        text-style: bold;
    }

    DataTable .column-type-unknown {
        color: $text-muted;
        text-style: bold;
    }
    """
        + HELP_OVERLAY_CSS
    )

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self, session, **kwargs):
        """Initialize app with dataset session."""
        super().__init__(**kwargs)
        self.session = session
        self.initial_load_paths = []
        self.keybindings = KeybindingsRegistry()
        self.data_loader = DataLoader()
        self._loading_start_time = None

        # Install MainScreen
        self.main_screen = MainScreen(self.session, self.keybindings)

    def notify_error(
        self, message: str, title: str = "Error", copy_to_clipboard: bool = True
    ) -> None:
        """Show error notification and optionally copy to clipboard.

        Args:
            message: The error message to display
            title: Title for the notification
            copy_to_clipboard: Whether to automatically copy to clipboard (default: True)

        """
        if copy_to_clipboard:
            try:
                self.copy_to_clipboard(message)
                # Add visual indicator that it was copied
                display_message = f"{message}\n\n[dim italic]✓ Copied to clipboard (click to dismiss)[/dim italic]"
            except Exception:
                # Clipboard not available (e.g., macOS Terminal)
                display_message = (
                    f"{message}\n\n[dim italic](click to dismiss)[/dim italic]"
                )
        else:
            display_message = (
                f"{message}\n\n[dim italic](click to dismiss)[/dim italic]"
            )

        self.notify(
            display_message, severity="error", timeout=30, title=title, markup=True
        )

    def on_mount(self) -> None:
        """Handle app mount event."""
        # Push MainScreen to make it active
        self.push_screen(self.main_screen)

        # Load initial datasets if provided via CLI
        if self.initial_load_paths:
            self.call_after_refresh(self._load_initial_datasets)

    def _load_initial_datasets(self) -> None:
        """Load datasets from CLI arguments with limit enforcement."""
        max_load = self.session.max_datasets
        total_paths = len(self.initial_load_paths)

        # Warn if more files than limit
        if total_paths > max_load:
            self.notify(
                f"Warning: {total_paths} files provided, but maximum is {max_load}. "
                f"Only loading first {max_load} files.",
                severity="warning",
                timeout=6,
            )
            paths_to_load = self.initial_load_paths[:max_load]
            skipped_count = total_paths - max_load
            skipped_files = self.initial_load_paths[max_load:]
            # Show skipped file names
            self.notify(
                f"Skipped {skipped_count} files: {', '.join([Path(p).name for p in skipped_files])}",
                severity="information",
                timeout=5,
            )
        else:
            paths_to_load = self.initial_load_paths

        for path in paths_to_load:
            self.run_worker(self.load_dataset_async(path), exclusive=False)

    async def load_dataset_async(self, path: str) -> None:
        """Load dataset asynchronously with progress tracking.

        Args:
            path: File path or URL to load

        """
        # Track start time for 500ms threshold
        start_time = time.time()

        # Check if this is a large file
        file_size, estimated_rows, is_large = self.data_loader.get_file_info(path)

        loading_modal = None

        # Show loading modal for large files
        if is_large:
            from .widgets.modals import LoadingModal

            loading_modal = LoadingModal(
                filename=Path(path).name,
                file_size=file_size,
                estimated_rows=estimated_rows,
            )

            # Show modal and get the future
            self.push_screen(loading_modal)

            # Give the modal a moment to render
            await asyncio.sleep(0.05)
        else:
            # Show immediate notification for small files
            self.notify(f"Loading {Path(path).name}...")

        try:
            # Progress callback to update modal
            def progress_callback(value: float, message: str):
                if loading_modal and not loading_modal.cancelled:
                    loading_modal.update_progress(value, message)

            # Cancellation checker function
            def is_cancelled() -> bool:
                return loading_modal.cancelled if loading_modal else False

            # Load dataset with progress tracking and cancellation support
            if is_large:
                dataset = await self.data_loader.load_from_source(
                    path, progress_callback=progress_callback, is_cancelled=is_cancelled
                )
            else:
                dataset = await self.data_loader.load_from_source(path)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time

            # Dismiss loading modal if shown
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()

            # Show completion notification with timing if >500ms
            if elapsed_time > 0.5:
                self.notify(
                    f"Loaded {Path(path).name} ({elapsed_time:.1f}s)", timeout=3
                )
            else:
                self.notify(f"Loaded {Path(path).name}", timeout=2)

            # Update UI in main thread
            self._on_dataset_loaded(dataset)

        except asyncio.CancelledError:
            # User cancelled the loading operation
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()
            self.notify(
                f"Cancelled loading {Path(path).name}", severity="warning", timeout=3
            )
        except FileNotFoundError:
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()
            self.notify_error(
                f"File not found: {Path(path).name}",
                title="Load Failed",
            )
        except TimeoutError as e:
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()
            self.notify_error(
                f"Network timeout loading {Path(path).name}: {e}",
                title="Load Failed",
            )
        except ValueError as e:
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()
            # Handles unsupported formats and HTTP errors
            self.notify_error(
                f"Error loading {Path(path).name}: {e}",
                title="Load Failed",
            )
        except Exception as e:
            if loading_modal and loading_modal in self.screen_stack:
                self.pop_screen()
            # Catch-all for unexpected errors
            self.notify_error(
                f"Unexpected error loading {Path(path).name}: {type(e).__name__}: {e}",
                title="Load Failed",
            )

    def _on_dataset_loaded(self, dataset: Dataset) -> None:
        """Handle dataset loaded (runs in main thread).

        Args:
            dataset: Loaded dataset

        """
        try:
            self.main_screen.load_dataset(dataset)
        except Exception as e:
            self.notify_error(
                f"Error displaying dataset: {e}",
                title="Display Error",
            )

    async def action_quit(self) -> None:
        """Quit application."""
        self.exit()

    def action_help(self) -> None:
        """Show help overlay."""
        self.main_screen.action_help()
