"""Operations sidebar showing operations history (right sidebar, push)."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, ListItem, ListView, Static


class OperationsSidebar(Vertical):
    """Right sidebar showing operations history (push, 25% width).

    Features:
    - ListView showing all applied operations
    - Keyboard actions:
        - Ctrl+Up/Down: Move operation up/down in sequence
        - Enter: Edit selected operation
        - Delete: Remove selected operation
    - Auto-shows when first operation is applied
    - Auto-hides when all operations are removed

    Usage:
        sidebar.refresh_operations(dataset.operation_history)
    """

    show_sidebar = reactive(False)

    BINDINGS = [
        Binding("ctrl+up", "move_up", "Move Up"),
        Binding("ctrl+down", "move_down", "Move Down"),
        Binding("enter", "edit_operation", "Edit"),
        Binding("delete", "remove_operation", "Remove"),
        Binding("ctrl+c", "clear_all", "Clear All"),
    ]

    def __init__(self, **kwargs):
        """Initialize operations sidebar."""
        super().__init__(id="operations_sidebar", classes="sidebar hidden", **kwargs)
        self.operations: list = []

    def watch_show_sidebar(self, show: bool) -> None:
        """React to visibility changes."""
        if show:
            self.remove_class("hidden")
            self.add_class("visible")
        else:
            self.add_class("hidden")
            self.remove_class("visible")

    def compose(self) -> ComposeResult:
        """Create operations sidebar content."""
        yield Label("Applied Operations", classes="sidebar-title")
        yield ListView(id="operations_list")
        yield Static("", id="operations_status", classes="sidebar-status")

    def refresh_operations(self, operations: list) -> None:
        """Update operations list.

        Args:
            operations: List of Operation objects
        """
        self.operations = operations
        operations_list = self.query_one("#operations_list", ListView)
        operations_list.clear()

        for idx, op in enumerate(operations):
            # Display format: "1. Filter: age > 25"
            display_text = f"{idx + 1}. {op.display}"
            operations_list.append(
                ListItem(
                    Static(display_text),
                    id=f"op_{op.id}",
                )
            )

        # Update status
        status = self.query_one("#operations_status", Static)
        if operations:
            status.update(f"{len(operations)} operation{'s' if len(operations) > 1 else ''} applied")
        else:
            status.update("No operations applied")

        # Auto-show/hide based on operations
        self.show_sidebar = len(operations) > 0

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

        if operations_list.index is None or operations_list.index >= len(self.operations) - 1:
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

    # Custom messages for operation events
    class OperationsReordered(Message):
        """Message sent when operations are reordered."""

        def __init__(self, operations: list):
            super().__init__()
            self.operations = operations

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
