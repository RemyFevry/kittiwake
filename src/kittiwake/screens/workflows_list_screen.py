"""Screen for managing saved workflows."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from ..services.persistence import WorkflowRepository


class WorkflowsListScreen(Screen):
    """Screen for listing and managing saved workflows."""

    BINDINGS = [
        Binding("l", "load_workflow", "Load"),
        Binding("e", "edit_workflow", "Edit"),
        Binding("d", "delete_workflow", "Delete"),
        Binding("escape", "dismiss", "Back"),
    ]

    def __init__(self, repository: WorkflowRepository | None = None, **kwargs):
        """Initialize workflows list screen.

        Args:
            repository: WorkflowRepository instance (created if None)

        """
        super().__init__(**kwargs)
        self.repository = repository or WorkflowRepository()
        self.workflows: list[dict] = []
        self.selected_workflow_id: int | None = None

    def compose(self) -> ComposeResult:
        """Create workflows list screen layout."""
        yield Header()

        with Container(id="workflows_container"):
            yield Label("Saved Workflows", id="workflows_title")

            with Vertical(id="workflows_list"):
                table = DataTable(id="workflows_table")
                table.cursor_type = "row"
                table.zebra_stripes = True
                yield table

            with Horizontal(id="workflows_buttons"):
                yield Button("Load (L)", variant="primary", id="load_btn")
                yield Button("Edit (E)", variant="default", id="edit_btn")
                yield Button("Delete (D)", variant="error", id="delete_btn")
                yield Button("Back (Esc)", variant="default", id="back_btn")

        yield Footer()

    def on_mount(self) -> None:
        """Setup table columns and load workflows."""
        table = self.query_one("#workflows_table", DataTable)

        # Add columns
        table.add_columns("ID", "Name", "Description", "Ops", "Created", "Modified")

        # Load workflows
        self._refresh_workflows()

    def _refresh_workflows(self) -> None:
        """Refresh workflows list from database."""
        table = self.query_one("#workflows_table", DataTable)
        table.clear()

        try:
            self.workflows = self.repository.list_all()

            if not self.workflows:
                table.add_row("", "No workflows saved", "", "", "", "")
                return

            for workflow in self.workflows:
                table.add_row(
                    str(workflow["id"]),
                    workflow["name"],
                    workflow.get("description", "")[:50] or "",
                    str(workflow["operation_count"]),
                    str(workflow["created_at"])[:19],
                    str(workflow["modified_at"])[:19],
                )
        except Exception as e:
            self.notify(f"Error loading workflows: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection.

        Args:
            event: Row selected event

        """
        if not self.workflows:
            return

        # Get selected workflow ID from row
        row_key = event.row_key
        table = self.query_one("#workflows_table", DataTable)
        row_data = table.get_row(row_key)

        try:
            self.selected_workflow_id = int(row_data[0])
        except (ValueError, IndexError):
            self.selected_workflow_id = None

    def action_load_workflow(self) -> None:
        """Load selected workflow and dismiss screen."""
        if self.selected_workflow_id is None:
            self.notify("Please select a workflow", severity="warning")
            return

        try:
            workflow_data = self.repository.load_by_id(self.selected_workflow_id)
            if workflow_data is None:
                self.notify("Workflow not found", severity="error")
                return

            # Return workflow data to caller
            self.dismiss({"action": "load", "workflow": workflow_data})

        except Exception as e:
            self.notify(f"Error loading workflow: {e}", severity="error")

    def action_edit_workflow(self) -> None:
        """Edit selected workflow."""
        if self.selected_workflow_id is None:
            self.notify("Please select a workflow", severity="warning")
            return

        try:
            workflow_data = self.repository.load_by_id(self.selected_workflow_id)
            if workflow_data is None:
                self.notify("Workflow not found", severity="error")
                return

            # Return edit action to caller
            self.dismiss({"action": "edit", "workflow": workflow_data})

        except Exception as e:
            self.notify(f"Error loading workflow: {e}", severity="error")

    def action_delete_workflow(self) -> None:
        """Delete selected workflow after confirmation."""
        if self.selected_workflow_id is None:
            self.notify("Please select a workflow", severity="warning")
            return

        # TODO: Add confirmation modal
        try:
            success = self.repository.delete(self.selected_workflow_id)
            if success:
                self.notify("Workflow deleted", severity="information")
                self._refresh_workflows()
                self.selected_workflow_id = None
            else:
                self.notify("Failed to delete workflow", severity="error")

        except Exception as e:
            self.notify(f"Error deleting workflow: {e}", severity="error")

    def action_dismiss(self) -> None:
        """Dismiss screen without action."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event

        """
        if event.button.id == "load_btn":
            self.action_load_workflow()
        elif event.button.id == "edit_btn":
            self.action_edit_workflow()
        elif event.button.id == "delete_btn":
            self.action_delete_workflow()
        elif event.button.id == "back_btn":
            self.action_dismiss()


# CSS for workflows list screen
WORKFLOWS_LIST_SCREEN_CSS = """
WorkflowsListScreen {
    align: center top;
}

#workflows_container {
    width: 90%;
    height: 90%;
    background: $surface;
    border: thick $primary;
    margin: 2;
    padding: 1;
}

#workflows_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#workflows_list {
    height: 1fr;
    margin-bottom: 1;
}

#workflows_table {
    width: 100%;
    height: 100%;
}

#workflows_buttons {
    width: 100%;
    height: auto;
    align: center middle;
}

#workflows_buttons Button {
    margin: 0 1;
}
"""
