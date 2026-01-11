"""Dataset tabs widget for switching between multiple datasets."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label

from ..models.dataset_session import DatasetSession


class DatasetTabs(Container):
    """Tab bar for switching between loaded datasets.

    Features:
    - Display up to 10 dataset tabs
    - Highlight active dataset
    - Click or keyboard navigation (Tab/Shift+Tab)
    - Close button for each tab (Ctrl+W)
    - Shows dataset name with truncation if needed
    """

    DEFAULT_CSS = """
    DatasetTabs {
        height: auto;
        background: $panel;
        padding: 1;
    }

    DatasetTabs Horizontal {
        height: auto;
        width: 1fr;
    }

    DatasetTabs Label {
        padding: 0 1;
        width: auto;
    }

    DatasetTabs Button {
        margin: 0 1;
    }
    """

    active_index = reactive(0)

    class TabChanged(Message):
        """Message sent when active tab changes."""

        def __init__(self, index: int):
            super().__init__()
            self.index = index

    class TabClosed(Message):
        """Message sent when a tab is closed."""

        def __init__(self, index: int):
            super().__init__()
            self.index = index

    def __init__(self, session: DatasetSession | None = None, **kwargs):
        """Initialize dataset tabs.

        Args:
            session: DatasetSession managing datasets

        """
        super().__init__(**kwargs)
        self.session = session
        self.tab_buttons: list[Button] = []
        self._rebuilding = False

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal(id="tabs_container"):
            yield Label("Datasets:", id="tabs_label")

    def on_mount(self) -> None:
        """Initialize tabs when mounted."""
        if self.session:
            self._rebuild_tabs()

    def set_session(self, session: DatasetSession) -> None:
        """Set or update the session.

        Args:
            session: DatasetSession to use

        """
        self.session = session
        self._rebuild_tabs()

    def _rebuild_tabs(self) -> None:
        """Rebuild tab buttons from current session."""
        if not self.session or self._rebuilding:
            return

        # Prevent concurrent rebuilds
        self._rebuilding = True

        try:
            container = self.query_one("#tabs_container")
            datasets = self.session.datasets
            num_datasets = len(datasets)
            num_existing = len(self.tab_buttons)

            # Remove excess buttons (if we have more buttons than datasets)
            while num_existing > num_datasets:
                try:
                    last_btn = self.tab_buttons.pop()
                    last_btn.remove()
                except Exception:
                    pass
                num_existing -= 1

            # Add new buttons (if we have fewer buttons than datasets)
            for i in range(num_existing, num_datasets):
                dataset = datasets[i]
                name = dataset.name
                if len(name) > 20:
                    name = name[:17] + "..."

                btn = Button(
                    name,
                    id=f"tab_{i}",
                    variant="primary" if i == self.active_index else "default",
                    classes="dataset-tab",
                )
                self.tab_buttons.append(btn)
                container.mount(btn)

            # Update labels and variants of existing buttons
            for i in range(num_datasets):
                dataset = datasets[i]
                btn = self.tab_buttons[i]
                name = dataset.name
                if len(name) > 20:
                    name = name[:17] + "..."

                # Add operation counts to label
                queued_count = len(dataset.queued_operations)
                executed_count = len(dataset.executed_operations)
                if queued_count > 0 or executed_count > 0:
                    ops_label = f" ({queued_count}⏸/{executed_count}✓)"
                    # Ensure total label doesn't exceed reasonable length
                    if len(name) + len(ops_label) <= 20:
                        name = name + ops_label
                    elif len(ops_label) > 0:
                        # Truncate name more to fit operation counts
                        name = name[: 20 - len(ops_label) - 3] + "..." + ops_label

                btn.label = name
                btn.variant = "primary" if i == self.active_index else "default"
        finally:
            # Always release the lock
            self._rebuilding = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab button click."""
        button = event.button

        # Get tab index from button id
        if button.id and button.id.startswith("tab_"):
            try:
                index = int(button.id.split("_")[1])
                self.switch_to(index)
            except (IndexError, ValueError):
                pass

    def switch_to(self, index: int) -> None:
        """Switch to tab at given index.

        Args:
            index: Tab index (0-based)

        """
        if not self.session or index < 0 or index >= len(self.session.datasets):
            return

        # Update active index
        old_index = self.active_index
        self.active_index = index

        # Update button styles
        if 0 <= old_index < len(self.tab_buttons):
            self.tab_buttons[old_index].variant = "default"
        if 0 <= index < len(self.tab_buttons):
            self.tab_buttons[index].variant = "primary"

        # Update session active dataset using UUID
        dataset = self.session.datasets[index]
        self.session.set_active_dataset(dataset.id)

        # Post message
        self.post_message(self.TabChanged(index))

    def next_tab(self) -> bool:
        """Switch to next tab (wraps around).

        Returns:
            True if tab changed, False if only one tab

        """
        if not self.session or len(self.session.datasets) <= 1:
            return False

        next_idx = (self.active_index + 1) % len(self.session.datasets)
        self.switch_to(next_idx)
        return True

    def previous_tab(self) -> bool:
        """Switch to previous tab (wraps around).

        Returns:
            True if tab changed, False if only one tab

        """
        if not self.session or len(self.session.datasets) <= 1:
            return False

        prev_idx = (self.active_index - 1) % len(self.session.datasets)
        self.switch_to(prev_idx)
        return True

    def close_tab(self, index: int | None = None) -> None:
        """Close tab at given index (or active tab if None).

        Args:
            index: Tab index to close, or None for active tab

        """
        if index is None:
            index = self.active_index

        if not self.session or index < 0 or index >= len(self.session.datasets):
            return

        # Post message first
        self.post_message(self.TabClosed(index))

        # Remove from session using UUID
        dataset = self.session.datasets[index]
        self.session.remove_dataset(dataset.id)

        # Adjust active index if needed
        if index < self.active_index:
            self.active_index -= 1
        elif index == self.active_index and self.active_index >= len(
            self.session.datasets
        ):
            self.active_index = max(0, len(self.session.datasets) - 1)

        # Rebuild tabs
        self._rebuild_tabs()

        # Notify of new active tab
        if self.session.datasets:
            self.post_message(self.TabChanged(self.active_index))

    def add_dataset_tab(self) -> None:
        """Add a new dataset tab (triggers rebuild)."""
        self._rebuild_tabs()

        # Switch to new tab
        if self.session and self.session.datasets:
            self.switch_to(len(self.session.datasets) - 1)
