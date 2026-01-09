"""Saved analyses list screen for managing saved analyses."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ..services.persistence import SavedAnalysisRepository
from ..widgets.modals.export_modal import ExportModal

if TYPE_CHECKING:
    from ..app import KittiwakeApp


class SavedAnalysesListScreen(Screen):
    """Screen for listing and managing saved analyses.

    Features:
    - DataTable showing all saved analyses
    - Columns: name, description, created_at, modified_at, operation_count
    - Keyboard actions:
        - Enter: Load analysis
        - E: Update (edit) analysis
        - Delete: Delete analysis with confirmation
        - X: Export analysis
    - Returns to main screen with selected analysis or None
    """

    BINDINGS = [
        Binding("enter", "load_analysis", "Load", priority=True),
        Binding("e", "edit_analysis", "Edit"),
        Binding("delete", "delete_analysis", "Delete"),
        Binding("x", "export_analysis", "Export"),
        Binding("escape", "cancel", "Cancel"),
        Binding("q", "cancel", "Back"),
    ]

    CSS = """
    SavedAnalysesListScreen {
        align: center middle;
    }

    #analyses_container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #analyses_title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        margin-bottom: 1;
        padding: 1;
    }

    #analyses_table {
        width: 100%;
        height: 1fr;
    }

    #analyses_status {
        margin-top: 1;
        text-align: center;
        color: $text-muted;
    }
    """

    def __init__(self, **kwargs):
        """Initialize saved analyses list screen."""
        super().__init__(**kwargs)
        self.repository = SavedAnalysisRepository()
        self.analyses_data: list[dict[str, Any]] = []
        self.selected_row_key: int | None = None

    @property
    def kittiwake_app(self) -> "KittiwakeApp":
        """Return the app instance with proper typing."""
        from ..app import KittiwakeApp  # noqa: F401
        return self.app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose screen UI."""
        yield Header()

        with Container(id="analyses_container"):
            yield Static("Saved Analyses", id="analyses_title")

            # Create data table with columns
            table = DataTable(id="analyses_table", cursor_type="row")
            table.add_column("ID", width=6)
            table.add_column("Name", width=25)
            table.add_column("Description", width=35)
            table.add_column("Created", width=20)
            table.add_column("Modified", width=20)
            table.add_column("Ops", width=6)
            yield table

            yield Static("", id="analyses_status")

        yield Footer()

    def on_mount(self) -> None:
        """Load analyses when screen mounts."""
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Refresh the analyses table with latest data."""
        table = self.query_one("#analyses_table", DataTable)
        status = self.query_one("#analyses_status", Static)

        # Clear existing rows
        table.clear()

        try:
            # Fetch analyses from database
            self.analyses_data = self.repository.list_all()

            if not self.analyses_data:
                status.update("No saved analyses found. Press ESC to return.")
                return

            # Populate table
            for analysis in self.analyses_data:
                # Format dates
                created_at = self._format_datetime(analysis.get("created_at"))
                modified_at = self._format_datetime(analysis.get("modified_at"))

                # Truncate description
                description = analysis.get("description") or ""
                if len(description) > 32:
                    description = description[:29] + "..."

                table.add_row(
                    str(analysis["id"]),
                    analysis["name"],
                    description,
                    created_at,
                    modified_at,
                    str(analysis["operation_count"]),
                    key=str(analysis["id"]),
                )

            status.update(
                f"Showing {len(self.analyses_data)} saved analyses. "
                "Press Enter to load, E to edit, X to export, Delete to remove."
            )

        except Exception as e:
            status.update(f"Error loading analyses: {e}")
            self.kittiwake_app.notify_error(f"Failed to load analyses: {e}")

    def _format_datetime(self, dt: Any) -> str:
        """Format datetime for display."""
        if dt is None:
            return "N/A"

        try:
            if isinstance(dt, str):
                # Parse ISO format
                dt = datetime.fromisoformat(dt)

            # Format as: "2026-01-09 14:30"
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(dt)

    def _get_selected_analysis(self) -> dict[str, Any] | None:
        """Get currently selected analysis data."""
        table = self.query_one("#analyses_table", DataTable)

        cursor_row = table.cursor_row
        if cursor_row is None or cursor_row < 0 or cursor_row >= len(self.analyses_data):
            return None

        # Return analysis at cursor position
        return self.analyses_data[cursor_row]

    def action_load_analysis(self) -> None:
        """Load selected analysis and return to main screen."""
        analysis = self._get_selected_analysis()

        if not analysis:
            self.notify("No analysis selected", severity="warning")
            return

        try:
            # Load full analysis data with operations
            analysis_id = analysis["id"]
            full_analysis = self.repository.load_by_id(analysis_id)

            if not full_analysis:
                self.notify(
                    f"Analysis {analysis_id} not found", severity="error"
                )
                return

            # Dismiss screen with loaded analysis
            self.dismiss({"action": "load", "analysis": full_analysis})

        except Exception as e:
            self.kittiwake_app.notify_error(f"Failed to load analysis: {e}")

    def action_edit_analysis(self) -> None:
        """Edit selected analysis metadata (name/description)."""
        analysis = self._get_selected_analysis()

        if not analysis:
            self.notify("No analysis selected", severity="warning")
            return

        # Return to main screen with edit action
        self.dismiss({"action": "edit", "analysis": analysis})

    def action_delete_analysis(self) -> None:
        """Delete selected analysis with confirmation."""
        analysis = self._get_selected_analysis()

        if not analysis:
            self.notify("No analysis selected", severity="warning")
            return

        analysis_name = analysis["name"]
        analysis_id = analysis["id"]

        # Show confirmation (for now, just delete - confirmation modal TBD)
        try:
            deleted = self.repository.delete(analysis_id)

            if deleted:
                self.notify(f"Deleted analysis: {analysis_name}", severity="information")
                self._refresh_table()
            else:
                self.notify(
                    f"Failed to delete analysis: {analysis_name}",
                    severity="error"
                )

        except Exception as e:
            self.kittiwake_app.notify_error(f"Error deleting analysis: {e}")

    def action_export_analysis(self) -> None:
        """Export selected analysis to code."""
        analysis = self._get_selected_analysis()

        if not analysis:
            self.notify("No analysis selected", severity="warning")
            return

        # Load full analysis data with operations
        try:
            repo = SavedAnalysisRepository()
            full_analysis = repo.load_by_id(analysis["id"])
            
            if not full_analysis:
                self.notify("Failed to load analysis data", severity="error")
                return
        except Exception as e:
            self.kittiwake_app.notify_error(f"Error loading analysis: {e}")
            return

        # Show export modal
        def on_export_modal_result(result: dict | None) -> None:
            """Handle export modal result."""
            if result is None:
                return
            
            export_format = result["format"]
            output_path = result["path"]
            
            # Perform export
            try:
                from ..services.export import ExportService
                from pathlib import Path
                
                export_service = ExportService()
                
                # Call appropriate export method
                if export_format == "python":
                    output_file = export_service.export_to_python(full_analysis, output_path)
                elif export_format == "marimo":
                    output_file = export_service.export_to_marimo(full_analysis, output_path)
                elif export_format == "jupyter":
                    output_file = export_service.export_to_jupyter(full_analysis, output_path)
                else:
                    self.notify(f"Unknown export format: {export_format}", severity="error")
                    return
                
                self.notify(f"Exported to {output_file}", severity="information")
            except Exception as e:
                self.kittiwake_app.notify_error(f"Export failed: {e}")
        
        self.app.push_screen(
            ExportModal(analysis_name=analysis["name"]),
            on_export_modal_result
        )

    def action_cancel(self) -> None:
        """Cancel and return to main screen without action."""
        self.dismiss(None)
