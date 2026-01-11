"""Loading modal with progress indicator for long-running data operations."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ProgressBar, Static


class LoadingModal(ModalScreen[bool]):
    """Modal that displays loading progress with cancellation option.

    Features:
    - Progress bar showing 0-100% completion
    - Status message (e.g., "Reading file...", "Analyzing schema...")
    - File info display (size, estimated rows)
    - Esc key to cancel operation
    - Returns True if cancelled, False if completed normally

    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    LoadingModal {
        align: center middle;
    }
    
    #loading_dialog {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $accent;
        padding: 1 2;
    }
    
    #loading_title {
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }
    
    #loading_file_info {
        text-align: center;
        color: $text-muted;
        padding: 0 1;
        margin-bottom: 1;
    }
    
    #loading_progress {
        width: 100%;
        margin: 1 0;
    }
    
    #loading_status {
        text-align: center;
        padding: 1;
        height: 3;
    }
    
    #loading_hint {
        text-align: center;
        color: $text-muted;
        padding: 1;
        margin-top: 1;
    }
    """

    def __init__(
        self, filename: str, file_size: int = 0, estimated_rows: int = 0, **kwargs
    ):
        """Initialize loading modal.

        Args:
            filename: Name of file being loaded
            file_size: File size in bytes (0 if unknown)
            estimated_rows: Estimated number of rows (0 if unknown)
        """
        super().__init__(**kwargs)
        self.filename = filename
        self.file_size = file_size
        self.estimated_rows = estimated_rows
        self._cancelled = False

    def compose(self) -> ComposeResult:
        """Create loading modal content."""
        with Container(id="loading_dialog"):
            yield Static("Loading Data", id="loading_title")

            # File info
            file_info_parts = [f"File: {self.filename}"]
            if self.file_size > 0:
                size_mb = self.file_size / (1024 * 1024)
                file_info_parts.append(f"Size: {size_mb:.1f} MB")
            if self.estimated_rows > 0:
                rows_str = (
                    f"{self.estimated_rows:,}"
                    if self.estimated_rows < 1_000_000
                    else f"{self.estimated_rows / 1_000_000:.1f}M"
                )
                file_info_parts.append(f"Est. rows: {rows_str}")

            yield Label(" | ".join(file_info_parts), id="loading_file_info")

            with Vertical():
                yield ProgressBar(total=100, show_eta=False, id="loading_progress")
                yield Label("Initializing...", id="loading_status")

            yield Static("Press Esc to cancel", id="loading_hint")

    def update_progress(self, value: float, message: str = "") -> None:
        """Update progress bar and status message.

        Args:
            value: Progress value between 0.0 and 1.0
            message: Status message to display
        """
        if self._cancelled:
            return

        # Update progress bar (0-100)
        progress_bar = self.query_one("#loading_progress", ProgressBar)
        progress_bar.update(progress=int(value * 100))

        # Update status message
        if message:
            status_label = self.query_one("#loading_status", Label)
            status_label.update(message)

    def action_cancel(self) -> None:
        """Cancel the loading operation."""
        self._cancelled = True
        self.dismiss(True)  # Return True to indicate cancellation

    @property
    def cancelled(self) -> bool:
        """Check if loading was cancelled."""
        return self._cancelled
