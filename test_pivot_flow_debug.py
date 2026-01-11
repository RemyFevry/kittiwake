#!/usr/bin/env python3
"""Debug test to simulate the exact flow from main_screen."""

from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar


class DebugPivotApp(App):
    """Minimal app to test pivot sidebar flow."""

    def compose(self) -> ComposeResult:
        yield Static("Debug: Testing pivot sidebar flow")
        yield Button("Open Pivot", id="open_btn")
        # Create sidebar WITHOUT columns (like main_screen does)
        yield PivotSidebar()

    def on_mount(self) -> None:
        """Get reference to sidebar."""
        self.pivot_sidebar = self.query_one("#pivot_sidebar", PivotSidebar)
        
        # Write to log file
        with open("/tmp/pivot_debug.txt", "w") as f:
            f.write(f"on_mount: sidebar.columns = {self.pivot_sidebar.columns}\n")
            f.write(f"on_mount: sidebar.value_sections = {self.pivot_sidebar.value_sections}\n")
        
        # Auto-trigger after a short delay
        self.set_timer(0.5, self.auto_test)

    def auto_test(self) -> None:
        """Automatically test the flow."""
        # Simulate what main_screen does
        test_columns = ["category", "region", "product", "sales", "quantity"]
        
        with open("/tmp/pivot_debug.txt", "a") as f:
            f.write("\n" + "="*60 + "\n")
            f.write("SIMULATING MAIN_SCREEN FLOW:\n")
            f.write("="*60 + "\n")
            
            f.write(f"\n1. Before update_columns:\n")
            f.write(f"   sidebar.columns = {self.pivot_sidebar.columns}\n")
            f.write(f"   sidebar.value_sections = {self.pivot_sidebar.value_sections}\n")
            
            # Call update_columns
            self.pivot_sidebar.update_columns(test_columns)
            
            f.write(f"\n2. After update_columns:\n")
            f.write(f"   sidebar.columns = {self.pivot_sidebar.columns}\n")
            f.write(f"   sidebar.value_sections = {self.pivot_sidebar.value_sections}\n")
            
            # Call show
            self.pivot_sidebar.show()
            
            f.write(f"\n3. After show:\n")
            f.write(f"   sidebar.columns = {self.pivot_sidebar.columns}\n")
            f.write(f"   sidebar.value_sections = {self.pivot_sidebar.value_sections}\n")
            
            # Check if section has columns
            if self.pivot_sidebar.value_sections:
                section_id = self.pivot_sidebar.value_sections[0]
                try:
                    from kittiwake.widgets.sidebars.pivot_sidebar import ValueAggregationSection
                    from textual.widgets import Select
                    
                    section = self.pivot_sidebar.query_one(f"#value_section_{section_id}", ValueAggregationSection)
                    f.write(f"\n4. First value section:\n")
                    f.write(f"   available_columns = {section.available_columns}\n")
                    
                    select = section.query_one(f"#value_column_{section_id}", Select)
                    f.write(f"   Select widget options count = {len(list(select._options))}\n")
                    f.write(f"   Select widget prompt = {select.prompt}\n")
                except Exception as e:
                    f.write(f"\n4. Error querying section: {e}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("Check the TUI - sidebar should be populated!\n")
            f.write("="*60 + "\n")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Simulate opening pivot sidebar."""
        if event.button.id == "open_btn":
            self.auto_test()


if __name__ == "__main__":
    app = DebugPivotApp()
    app.run()
