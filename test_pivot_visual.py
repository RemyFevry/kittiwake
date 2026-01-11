#!/usr/bin/env python3
"""Visual test for pivot sidebar - automatically opens the sidebar."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Static
from kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar


class TestPivotVisualApp(App):
    """Test app that automatically opens pivot sidebar."""

    CSS = """
    Screen {
        align: center middle;
    }
    
    #main {
        width: 100%;
        height: 100%;
        background: $surface;
    }
    
    #info {
        width: 50%;
        height: auto;
        border: solid green;
        padding: 2;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(
                "Pivot Sidebar Visual Test\n\n"
                "The sidebar should be visible on the left.\n"
                "Check:\n"
                "- Index SelectionList (height 8)\n"
                "- Columns SelectionList (height 8)\n"
                "- Value sections container (min-height 10)\n"
                "- Default Value #1 section with aggregations\n\n"
                "Press Ctrl+C or 'q' to quit",
                id="info"
            ),
            id="main"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Mount and show sidebar immediately."""
        # Create test columns
        test_columns = ["category", "region", "product", "sales", "quantity", "year"]
        
        # Create and mount sidebar
        self.pivot_sidebar = PivotSidebar(columns=test_columns)
        self.pivot_sidebar.callback = self.handle_pivot
        
        # Mount it
        self.mount(self.pivot_sidebar)
        
        # Show it (remove 'hidden' class)
        self.pivot_sidebar.show()

    def handle_pivot(self, params: dict) -> None:
        """Handle pivot parameters."""
        import json
        self.notify(f"Pivot params: {json.dumps(params, indent=2)}")
        print("\n" + "="*60)
        print("PIVOT PARAMETERS:")
        print(json.dumps(params, indent=2))
        print("="*60)


if __name__ == "__main__":
    app = TestPivotVisualApp()
    app.run()
