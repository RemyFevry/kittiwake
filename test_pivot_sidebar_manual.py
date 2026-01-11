#!/usr/bin/env python3
"""Manual test for the refactored pivot sidebar with SelectionList."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Button, Static
from kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar
from kittiwake.models.dataset import Dataset
import polars as pl
import narwhals as nw


class TestPivotApp(App):
    """Test app for pivot sidebar."""

    CSS = """
    Screen {
        align: center middle;
    }
    
    #main {
        width: 80%;
        height: 80%;
        border: solid green;
        padding: 2;
    }
    
    #result {
        margin-top: 1;
        border: solid yellow;
        padding: 1;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Button("Open Pivot Sidebar", id="open_btn"),
            Static("Results will appear here", id="result"),
            id="main"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Create test dataset and sidebar."""
        # Create a simple test dataset
        df = pl.DataFrame({
            "category": ["A", "A", "B", "B", "A", "B"],
            "region": ["East", "West", "East", "West", "East", "West"],
            "product": ["X", "Y", "X", "Y", "X", "Y"],
            "sales": [100, 200, 150, 250, 120, 180],
            "quantity": [10, 20, 15, 25, 12, 18],
            "year": [2023, 2023, 2024, 2024, 2023, 2024]
        })
        
        # Create dataset with named parameters
        nw_frame = nw.from_native(df, eager_only=True).lazy()
        self.dataset = Dataset(
            name="test_data",
            source="/tmp/test.csv",
            backend="polars",
            frame=nw_frame,
            original_frame=nw_frame,
            schema={col: str(dtype) for col, dtype in df.schema.items()},
            row_count=len(df),
            is_active=True,
            is_lazy=True
        )
        
        # Create pivot sidebar
        self.pivot_sidebar = PivotSidebar(
            columns=list(self.dataset.schema.keys())
        )
        self.pivot_sidebar.callback = self.handle_pivot_result
        self.pivot_sidebar.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "open_btn":
            self.open_pivot_sidebar()

    def open_pivot_sidebar(self) -> None:
        """Open the pivot sidebar."""
        if not self.pivot_sidebar.is_mounted:
            self.mount(self.pivot_sidebar)
        
        self.pivot_sidebar.show()

    def handle_pivot_result(self, params: dict) -> None:
        """Handle pivot result."""
        result_widget = self.query_one("#result", Static)
        
        # Format the params nicely
        lines = ["Pivot Parameters Received:", ""]
        lines.append(f"Index: {params.get('index', [])}")
        lines.append(f"Columns: {params.get('columns', [])}")
        lines.append(f"Values: {params.get('values', [])}")
        
        result_widget.update("\n".join(lines))
        
        # Also print to console
        print("\n" + "="*60)
        print("PIVOT PARAMETERS RECEIVED:")
        print("="*60)
        import json
        print(json.dumps(params, indent=2))
        print("="*60 + "\n")


if __name__ == "__main__":
    app = TestPivotApp()
    app.run()
