"""Summary panel widget for displaying aggregation results."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Label, Static


class SummaryPanel(Container):
    """Panel for displaying aggregation results with export functionality.

    Features:
    - Display aggregation results in a DataTable
    - Export results to CSV or JSON
    - Show/hide with keybinding
    - Keyboard navigable (Tab, Enter, Esc)

    Usage:
        panel.show_results(aggregation_data, operation_display)
        panel.hide()
    """

    DEFAULT_CSS = """
    SummaryPanel {
        height: 1fr;
        dock: top;
        display: none;
        layer: overlay;
        background: $surface;
        padding: 1;
    }

    SummaryPanel.visible {
        display: block;
    }

    SummaryPanel.hidden {
        display: none;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }

    .operation-desc {
        padding: 0 1;
        text-style: italic;
        color: $text-muted;
    }

    .results-container {
        height: 1fr;
        padding: 1;
    }

    .button-row {
        height: auto;
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
        Binding("ctrl+s", "export", "Export", priority=True),
    ]

    def __init__(self, **kwargs):
        """Initialize summary panel."""
        super().__init__(id="summary_panel", classes="summary-panel hidden", **kwargs)
        self.aggregation_data: list[dict[str, Any]] | None = None
        self.operation_display: str = ""
        self.callback: Callable[[str], None] | None = None

    def compose(self) -> ComposeResult:
        """Create summary panel content."""
        with VerticalScroll():
            yield Label("Aggregation Results", classes="panel-title")
            yield Static("", id="operation_description", classes="operation-desc")

            # Results table
            with Container(classes="results-container"):
                yield DataTable(
                    id="results_table", zebra_stripes=True, cursor_type="row"
                )

            # Action buttons
            with Horizontal(classes="button-row"):
                yield Button("Export CSV", variant="primary", id="export_csv_button")
                yield Button("Export JSON", variant="default", id="export_json_button")
                yield Button("Close", variant="default", id="close_button")

    def on_mount(self) -> None:
        """Configure table on mount."""
        table = self.query_one("#results_table", DataTable)
        table.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "export_csv_button":
            self._export_to_csv()
        elif event.button.id == "export_json_button":
            self._export_to_json()
        elif event.button.id == "close_button":
            self.action_dismiss()

    def show_results(self, data: list[dict[str, Any]], operation_display: str) -> None:
        """Show aggregation results in the panel.

        Args:
            data: List of dictionaries with aggregation results
            operation_display: Human-readable operation description
        """
        self.aggregation_data = data
        self.operation_display = operation_display

        # Update description
        desc_widget = self.query_one("#operation_description", Static)
        desc_widget.update(operation_display)

        # Populate table
        table = self.query_one("#results_table", DataTable)
        table.clear(columns=True)

        if not data or len(data) == 0:
            # No results
            table.add_column("Result")
            table.add_row("No results")
        else:
            # Add columns from first row
            first_row = data[0]
            for col_name in first_row.keys():
                table.add_column(str(col_name))

            # Add rows
            for row_data in data:
                row_values = []
                for col_name in first_row.keys():
                    value = row_data.get(col_name, "")
                    # Format value for display
                    if value is None:
                        row_values.append("null")
                    elif isinstance(value, (int, float)):
                        row_values.append(str(value))
                    else:
                        row_values.append(str(value))
                table.add_row(*row_values)

        # Show panel
        self.remove_class("hidden")
        self.add_class("visible")
        self.focus()

    def action_dismiss(self) -> None:
        """Hide the panel and return focus to main table."""
        self.add_class("hidden")
        self.remove_class("visible")

        # Try to focus data table
        try:
            data_table = self.app.query_one("#dataset_table_left")
            data_table.focus()
        except Exception:
            pass

    def action_export(self) -> None:
        """Show export options (triggered by Ctrl+S)."""
        # For now, just export to CSV as default
        self._export_to_csv()

    def _export_to_csv(self) -> None:
        """Export aggregation results to CSV file."""
        if not self.aggregation_data:
            self.app.notify("No data to export", severity="warning")
            return

        try:
            # Generate filename from operation display
            safe_name = "".join(
                c if c.isalnum() or c in (" ", "_", "-") else "_"
                for c in self.operation_display
            )
            safe_name = safe_name.replace(" ", "_").lower()
            filename = f"aggregation_{safe_name}.csv"

            # Get export directory (use current directory)
            export_path = Path.cwd() / filename

            # Write CSV
            import csv

            with open(export_path, "w", newline="", encoding="utf-8") as f:
                if self.aggregation_data:
                    writer = csv.DictWriter(
                        f, fieldnames=self.aggregation_data[0].keys()
                    )
                    writer.writeheader()
                    writer.writerows(self.aggregation_data)

            self.app.notify(f"Exported to {export_path}", severity="information")

        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")

    def _export_to_json(self) -> None:
        """Export aggregation results to JSON file."""
        if not self.aggregation_data:
            self.app.notify("No data to export", severity="warning")
            return

        try:
            # Generate filename from operation display
            safe_name = "".join(
                c if c.isalnum() or c in (" ", "_", "-") else "_"
                for c in self.operation_display
            )
            safe_name = safe_name.replace(" ", "_").lower()
            filename = f"aggregation_{safe_name}.json"

            # Get export directory (use current directory)
            export_path = Path.cwd() / filename

            # Write JSON
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "operation": self.operation_display,
                        "results": self.aggregation_data,
                        "row_count": len(self.aggregation_data),
                    },
                    f,
                    indent=2,
                    default=str,
                )

            self.app.notify(f"Exported to {export_path}", severity="information")

        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")
