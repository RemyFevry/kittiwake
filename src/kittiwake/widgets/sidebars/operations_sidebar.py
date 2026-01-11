"""Operations sidebar showing operations history (right sidebar, push)."""

from typing import cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, ListItem, ListView, Static
from textual.widgets._button import ButtonVariant


class OperationsSidebar(Vertical):
    """Right sidebar showing operations (both queued and executed, push, 25% width).

    Features:
    - ListView showing all operations with state indicators:
        - ⏳ for queued operations
        - ✓ for executed operations
        - ✗ for failed operations
    - Keyboard actions:
        - Ctrl+Up/Down: Move operation up/down in sequence
        - Enter: Edit selected operation
        - Delete: Remove selected operation
        - Ctrl+Shift+X: Clear all operations
    - Auto-shows when first operation is applied
    - Auto-hides when all operations are removed

    Usage:
        all_operations = dataset.executed_operations + dataset.queued_operations
        sidebar.refresh_operations(all_operations)
    """

    show_sidebar = reactive(True)  # Always visible
    execution_mode = reactive("lazy")
    current_dataset_name: reactive[str | None] = reactive(
        None
    )  # Track which dataset's operations are shown

    BINDINGS = [
        Binding("ctrl+up", "move_up", "Move Up"),
        Binding("ctrl+down", "move_down", "Move Down"),
        Binding("enter", "edit_operation", "Edit"),
        Binding("delete", "remove_operation", "Remove"),
        Binding(
            "ctrl+shift+x", "clear_all", "Clear All"
        ),  # Changed from ctrl+c to avoid conflict with copy on French Mac
        Binding("ctrl+m", "toggle_mode", "Toggle Mode"),
    ]

    def __init__(self, execution_mode: str = "lazy", **kwargs):
        """Initialize operations sidebar.

        Args:
            execution_mode: Initial execution mode ("lazy" or "eager")

        """
        super().__init__(id="operations_sidebar", classes="sidebar visible", **kwargs)
        self.execution_mode = execution_mode
        self.current_dataset_name = None
        self.operations: list = []
        self._refresh_counter = 0  # Counter to ensure unique IDs across refreshes
        self.show_sidebar = True  # Always show sidebar

    def watch_show_sidebar(self, show: bool) -> None:
        """React to visibility changes."""
        if show:
            self.remove_class("hidden")
            self.add_class("visible")
        else:
            self.add_class("hidden")
            self.remove_class("visible")

    def watch_execution_mode(self, mode: str) -> None:
        """React to execution mode changes."""
        # Update button if mounted
        try:
            button = self.query_one("#mode_toggle_button", Button)
            button.label = self._get_mode_button_label()
            button.variant = self._get_mode_button_variant()
        except Exception:
            # Button not mounted yet
            pass

    def watch_current_dataset_name(self, dataset_name: str | None) -> None:
        """React to dataset name changes - update label.

        Args:
            dataset_name: Name of the dataset whose operations are displayed
        """
        try:
            label = self.query_one("#dataset_name_label", Label)
            if dataset_name:
                label.update(f"Dataset: {dataset_name}")
                label.display = True
            else:
                label.update("")
                label.display = False
        except Exception:
            # Label not mounted yet
            pass

    def _get_mode_button_label(self) -> str:
        """Get button label based on current mode."""
        if self.execution_mode == "lazy":
            return "⚡ LAZY"
        else:
            return "▶ EAGER"

    def _get_mode_button_variant(self) -> ButtonVariant:
        """Get button variant (color) based on current mode."""
        if self.execution_mode == "lazy":
            return "warning"  # Yellow for lazy
        else:
            return "success"  # Green for eager

    def compose(self) -> ComposeResult:
        """Create operations sidebar content."""
        yield Label("Operations", classes="sidebar-title")

        # Dataset name label
        yield Label("", id="dataset_name_label", classes="dataset-label")

        # Mode toggle button
        yield Button(
            self._get_mode_button_label(),
            id="mode_toggle_button",
            variant=cast(ButtonVariant, self._get_mode_button_variant()),
            classes="mode-toggle-button",
        )

        yield ListView(id="operations_list")
        yield Static("", id="operations_status", classes="sidebar-status")

    def refresh_operations(self, operations: list) -> None:
        """Update operations list.

        Args:
            operations: List of Operation objects (both queued and executed)

        """
        self.operations = operations
        self._refresh_counter += 1  # Increment counter for unique IDs
        operations_list = self.query_one("#operations_list", ListView)

        # Remove all existing items by querying and removing them
        # This is more reliable than clear() which might be async
        for child in list(operations_list.children):
            child.remove()

        for idx, op in enumerate(operations):
            # Determine operation state styling
            state_indicator = ""
            if hasattr(op, "state"):
                if op.state == "queued":
                    state_indicator = "⏳ "  # Hourglass for queued
                elif op.state == "executed":
                    state_indicator = "✓ "  # Checkmark for executed
                elif op.state == "failed":
                    state_indicator = "✗ "  # X mark for failed

            # Display format: "⏳ 1. Filter: age > 25" or "✓ 1. Filter: age > 25"
            display_text = f"{state_indicator}{idx + 1}. {op.display}"

            # Use refresh counter + index to ensure unique IDs across multiple refreshes
            operations_list.append(
                ListItem(
                    Static(display_text),
                    id=f"op_item_{self._refresh_counter}_{idx}",
                )
            )

        # Update status
        status = self.query_one("#operations_status", Static)
        if operations:
            queued_count = sum(
                1 for op in operations if hasattr(op, "state") and op.state == "queued"
            )
            executed_count = sum(
                1
                for op in operations
                if hasattr(op, "state") and op.state == "executed"
            )
            failed_count = sum(
                1 for op in operations if hasattr(op, "state") and op.state == "failed"
            )

            status_parts = []
            if executed_count > 0:
                status_parts.append(f"{executed_count} executed")
            if queued_count > 0:
                status_parts.append(f"{queued_count} queued")
            if failed_count > 0:
                status_parts.append(f"{failed_count} failed")

            status.update(", ".join(status_parts))
        else:
            status.update("No operations")

        # Always show sidebar (user requested it to be always visible)
        self.show_sidebar = True

    def action_move_up(self) -> None:
        """Move selected operation up in sequence."""
        operations_list = self.query_one("#operations_list", ListView)

        if operations_list.index is None or operations_list.index <= 0:
            self.app.notify("Cannot move up further", severity="warning")
            return

        idx = operations_list.index

        # Swap operations
        self.operations[idx], self.operations[idx - 1] = (
            self.operations[idx - 1],
            self.operations[idx],
        )

        # Post message to trigger reapply
        self.post_message(self.OperationsReordered(self.operations))

        # Refresh UI and maintain selection
        self.refresh_operations(self.operations)
        operations_list.index = idx - 1

    def action_move_down(self) -> None:
        """Move selected operation down in sequence."""
        operations_list = self.query_one("#operations_list", ListView)

        if (
            operations_list.index is None
            or operations_list.index >= len(self.operations) - 1
        ):
            self.app.notify("Cannot move down further", severity="warning")
            return

        idx = operations_list.index

        # Swap operations
        self.operations[idx], self.operations[idx + 1] = (
            self.operations[idx + 1],
            self.operations[idx],
        )

        # Post message to trigger reapply
        self.post_message(self.OperationsReordered(self.operations))

        # Refresh UI and maintain selection
        self.refresh_operations(self.operations)
        operations_list.index = idx + 1

    def action_edit_operation(self) -> None:
        """Edit selected operation."""
        operations_list = self.query_one("#operations_list", ListView)

        if operations_list.index is None:
            self.app.notify("No operation selected", severity="warning")
            return

        op = self.operations[operations_list.index]
        self.post_message(self.OperationEdit(op))

    def action_remove_operation(self) -> None:
        """Remove selected operation."""
        operations_list = self.query_one("#operations_list", ListView)

        if operations_list.index is None:
            self.app.notify("No operation selected", severity="warning")
            return

        op = self.operations.pop(operations_list.index)
        self.post_message(self.OperationRemoved(op))

        # Refresh UI
        self.refresh_operations(self.operations)

    def action_clear_all(self) -> None:
        """Clear all operations."""
        if not self.operations:
            self.app.notify("No operations to clear", severity="information")
            return

        # Post message to clear all
        self.post_message(self.OperationsClearAll())

        # Clear local state
        self.operations = []
        self.refresh_operations(self.operations)

    def action_toggle_mode(self) -> None:
        """Toggle execution mode between lazy and eager."""
        # Toggle mode
        new_mode = "eager" if self.execution_mode == "lazy" else "lazy"

        # Post message to notify parent (MainScreen will handle mode switch logic)
        self.post_message(self.ModeToggleRequested(new_mode))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "mode_toggle_button":
            self.action_toggle_mode()

    # Custom messages for operation events
    class OperationsReordered(Message):
        """Message sent when operations are reordered."""

        def __init__(self, operations: list):
            super().__init__()
            self.operations = operations

    class ModeToggleRequested(Message):
        """Message sent when mode toggle is requested."""

        def __init__(self, requested_mode: str):
            super().__init__()
            self.requested_mode = requested_mode

    class OperationEdit(Message):
        """Message sent when an operation should be edited."""

        def __init__(self, operation):
            super().__init__()
            self.operation = operation

    class OperationRemoved(Message):
        """Message sent when an operation is removed."""

        def __init__(self, operation):
            super().__init__()
            self.operation = operation

    class OperationsClearAll(Message):
        """Message sent when all operations should be cleared."""

        pass
