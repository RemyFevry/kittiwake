"""Main Textual application for Kittiwake TUI data explorer."""

import time
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer
from textual.reactive import reactive

from .screens.main_screen import MainScreen
from .utils.keybindings import KeybindingsRegistry
from .services.data_loader import DataLoader
from .models.dataset import Dataset
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
    }
    
    #main_container {
        height: 1fr;
    }
    
    #dataset_tabs {
        height: auto;
        background: $panel;
        padding: 1;
    }
    
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
    
    Footer {
        background: $panel;
    }
    
    .loading-indicator {
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
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

    def on_mount(self) -> None:
        """Handle app mount event."""
        # Push MainScreen to make it active
        self.push_screen(self.main_screen)
        
        # Load initial datasets if provided via CLI
        if self.initial_load_paths:
            self.call_after_refresh(self._load_initial_datasets)

    def _load_initial_datasets(self) -> None:
        """Load datasets from CLI arguments."""
        for path in self.initial_load_paths:
            self.run_worker(self.load_dataset_async(path), exclusive=False)

    async def load_dataset_async(self, path: str) -> None:
        """Load dataset asynchronously with progress tracking.

        Args:
            path: File path or URL to load
        """
        # Track start time for 500ms threshold
        start_time = time.time()
        
        # Show immediate notification
        self.notify(f"Loading {Path(path).name}...")

        try:
            # Load dataset using DataLoader
            dataset = await self.data_loader.load_from_source(path)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Show completion notification with timing if >500ms
            if elapsed_time > 0.5:
                self.notify(
                    f"Loaded {Path(path).name} ({elapsed_time:.1f}s)", 
                    timeout=3
                )
            else:
                self.notify(f"Loaded {Path(path).name}", timeout=2)

            # Update UI in main thread
            self._on_dataset_loaded(dataset)

        except FileNotFoundError as e:
            self.notify(f"File not found: {Path(path).name}", severity="error")
        except TimeoutError as e:
            self.notify(f"Network timeout loading {Path(path).name}: {e}", severity="error")
        except ValueError as e:
            # Handles unsupported formats and HTTP errors
            self.notify(f"Error loading {Path(path).name}: {e}", severity="error")
        except Exception as e:
            # Catch-all for unexpected errors
            self.notify(f"Unexpected error loading {Path(path).name}: {type(e).__name__}: {e}", severity="error")

    def _on_dataset_loaded(self, dataset: Dataset) -> None:
        """Handle dataset loaded (runs in main thread).

        Args:
            dataset: Loaded dataset
        """
        try:
            self.main_screen.load_dataset(dataset)
        except Exception as e:
            self.notify(f"Error displaying dataset: {e}", severity="error")

    async def action_quit(self) -> None:
        """Quit application."""
        self.exit()

    def action_help(self) -> None:
        """Show help overlay."""
        self.main_screen.action_help()
