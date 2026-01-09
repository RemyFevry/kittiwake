# Quick Start Guide: TUI Data Explorer

**Branch**: `001-tui-data-explorer` | **Date**: 2026-01-09  
**For**: Developers implementing the sidebar-based UI architecture

This guide provides step-by-step instructions for building the core features with practical code examples.

---

## Prerequisites

- Python >=3.13
- uv package manager
- Basic familiarity with Textual framework
- Understanding of narwhals dataframe API

---

## Step 1: Project Setup

### Initialize Environment

```bash
# Navigate to project root
cd /Users/larky/Code/kittiwake

# Install dependencies
uv sync

# Verify installation
uv run kw --help
```

### Verify Dependencies

```bash
# Check Python version
python --version  # Should be >=3.13

# Check installed packages
uv pip list | grep -E "(textual|narwhals|duckdb)"
```

---

## Step 2: Understand the Architecture

### Layout Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Header                                                      │
├──────────┬─────────────────────────────────────┬────────────┤
│          │                                     │            │
│  Left    │         Data Table                  │   Right    │
│ Sidebar  │     (75% when right shown,         │  Sidebar   │
│  (30%,   │      100% when right hidden)       │  (25%,     │
│ overlay) │                                     │   push)    │
│          │                                     │            │
│ [Filter  │  ┌───┬──────┬─────┬─────┐         │ Operations │
│  Form]   │  │Row│ Name │ Age │City │         │  History   │
│          │  ├───┼──────┼─────┼─────┤         │            │
│          │  │ 1 │ Alice│  25 │ NYC │         │ 1. Filter  │
│          │  │ 2 │ Bob  │  30 │  SF │         │ 2. Sort    │
│          │  └───┴──────┴─────┴─────┘         │            │
├──────────┴─────────────────────────────────────┴────────────┤
│ Footer (shortcuts, status)                                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Left Sidebar** (overlay, 30%): Operation configuration forms
2. **Right Sidebar** (push, 25%): Operations history with edit/remove/reorder
3. **Data Table** (center): Main dataset view with pagination
4. **Header/Footer**: Navigation and status information

---

## Step 3: Implement Left Sidebar (Filter Example)

### Create Filter Sidebar Widget

**File**: `src/kittiwake/widgets/sidebars/left_sidebar.py`

```python
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Container, Horizontal
from textual.widgets import Label, Select, Input, Button
from textual.binding import Binding

class FilterSidebar(VerticalScroll):
    """Left sidebar for filter configuration (overlay, 30% width)."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]
    
    def __init__(self, columns: list[str]):
        super().__init__(id="filter_sidebar", classes="hidden")
        self.columns = columns
        self.callback = None
    
    def compose(self) -> ComposeResult:
        yield Label("Filter Configuration", classes="sidebar-title")
        
        with Container(classes="form-group"):
            yield Label("Column")
            yield Select(
                options=[(col, col) for col in self.columns],
                prompt="Select column...",
                id="column_select"
            )
        
        with Container(classes="form-group"):
            yield Label("Operator")
            yield Select(
                options=[
                    ("Equals (=)", "=="),
                    ("Not Equals (≠)", "!="),
                    ("Greater Than (>)", ">"),
                    ("Less Than (<)", "<"),
                    ("Greater or Equal (≥)", ">="),
                    ("Less or Equal (≤)", "<="),
                    ("Contains", "contains"),
                ],
                prompt="Select operator...",
                id="operator_select"
            )
        
        with Container(classes="form-group"):
            yield Label("Value")
            yield Input(placeholder="Enter value", id="value_input")
        
        with Horizontal(classes="button-row"):
            yield Button("Apply", variant="primary", id="apply_btn")
            yield Button("Cancel", id="cancel_btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "apply_btn":
            self._apply_filter()
        elif event.button.id == "cancel_btn":
            self.action_dismiss()
    
    def _apply_filter(self) -> None:
        """Collect form values and trigger callback."""
        column_select = self.query_one("#column_select", Select)
        operator_select = self.query_one("#operator_select", Select)
        value_input = self.query_one("#value_input", Input)
        
        if column_select.value == Select.BLANK:
            self.app.notify("Please select a column", severity="warning")
            return
        if operator_select.value == Select.BLANK:
            self.app.notify("Please select an operator", severity="warning")
            return
        if not value_input.value:
            self.app.notify("Please enter a value", severity="warning")
            return
        
        # Build filter params
        params = {
            "column": column_select.value,
            "operator": operator_select.value,
            "value": value_input.value
        }
        
        # Trigger callback with params
        if self.callback:
            self.callback(params)
        
        # Dismiss sidebar
        self.action_dismiss()
    
    def action_dismiss(self) -> None:
        """Hide the sidebar."""
        self.remove_class("visible")
        self.add_class("hidden")
        self.app.query_one("#data_table").focus()
```

### Add CSS Styling

**File**: `src/kittiwake/app.py` (in CSS property)

```python
CSS = """
Screen {
    layers: base overlay;
}

#filter_sidebar {
    layer: overlay;
    dock: left;
    width: 30%;
    height: 100%;
    background: $panel-darken-1;
    opacity: 90%;
    border-right: solid $accent;
    display: none;
}

#filter_sidebar.visible {
    display: block;
}

#filter_sidebar.hidden {
    display: none;
}

.form-group {
    padding: 1;
    margin: 1 0;
}

.sidebar-title {
    text-style: bold;
    padding: 1;
    background: $accent;
    color: $text;
}

.button-row {
    padding: 1;
    height: auto;
}
"""
```

### Integrate with Main Screen

**File**: `src/kittiwake/screens/main_screen.py`

```python
from textual.screen import Screen
from textual.binding import Binding
from .widgets.sidebars.left_sidebar import FilterSidebar

class MainScreen(Screen):
    BINDINGS = [
        Binding("ctrl+f", "open_filter_sidebar", "Filter"),
        Binding("escape", "focus_main", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Left sidebar (initially hidden)
        yield FilterSidebar(columns=self.get_active_columns())
        
        # Main content
        with Horizontal(id="main_content"):
            yield DatasetTable(id="data_table")
            yield OperationsSidebar(id="operations_sidebar")
        
        yield Footer()
    
    def action_open_filter_sidebar(self) -> None:
        """Show filter sidebar."""
        sidebar = self.query_one("#filter_sidebar", FilterSidebar)
        
        # Update columns for current dataset
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            self.notify("No active dataset", severity="warning")
            return
        
        sidebar.columns = list(active_dataset.schema.keys())
        sidebar.callback = self._handle_filter_result
        
        # Show sidebar
        sidebar.remove_class("hidden")
        sidebar.add_class("visible")
        sidebar.focus()
    
    def _handle_filter_result(self, params: dict) -> None:
        """Process filter params and apply operation."""
        from .services.narwhals_ops import OperationBuilder
        
        active_dataset = self.session.get_active_dataset()
        if not active_dataset:
            return
        
        try:
            # Build operation
            op_func = OperationBuilder.build_filter(
                column=params["column"],
                operator=params["operator"],
                value=params["value"],
                schema=active_dataset.schema
            )
            
            # Apply to dataset
            active_dataset.df = op_func(active_dataset.df)
            
            # Create Operation entity
            operation = Operation(
                id=str(uuid.uuid4()),
                code=OperationBuilder.to_code_string(op_func, {
                    "operation_type": "filter",
                    **params
                }),
                display=f"Filter: {params['column']} {params['operator']} {params['value']}",
                operation_type="filter",
                params=params,
                created_at=datetime.now()
            )
            
            # Add to dataset history
            active_dataset.operations.append(operation)
            
            # Refresh table
            self.query_one("#data_table").reload()
            
            # Show right sidebar (auto-appear on first operation)
            operations_sidebar = self.query_one("#operations_sidebar")
            if not active_dataset.operations:
                operations_sidebar.visible = True
            
            self.notify(f"Applied: {operation.display}", severity="success")
            
        except Exception as e:
            self.notify(f"Failed to apply filter: {e}", severity="error")
```

---

## Step 4: Implement Right Sidebar (Operations History)

### Create Operations Sidebar Widget

**File**: `src/kittiwake/widgets/sidebars/right_sidebar.py`

```python
from textual.containers import Vertical
from textual.widgets import Label, ListView, ListItem, Static
from textual.reactive import reactive
from textual.binding import Binding

class OperationsSidebar(Vertical):
    """Right sidebar showing operations history (push, 25% width)."""
    
    visible = reactive(False)
    
    BINDINGS = [
        Binding("ctrl+up", "move_up", "Move Up"),
        Binding("ctrl+down", "move_down", "Move Down"),
        Binding("enter", "edit_operation", "Edit"),
        Binding("delete", "remove_operation", "Remove"),
    ]
    
    def __init__(self):
        super().__init__(id="operations_sidebar", classes="hidden")
        self.operations = []
    
    def watch_visible(self, visible: bool) -> None:
        """React to visibility changes."""
        if visible:
            self.remove_class("hidden")
            self.add_class("visible")
        else:
            self.add_class("hidden")
            self.remove_class("visible")
    
    def compose(self) -> ComposeResult:
        yield Label("Applied Operations", classes="sidebar-title")
        yield ListView(id="operations_list")
    
    def refresh_operations(self, operations: list) -> None:
        """Update operations list."""
        self.operations = operations
        operations_list = self.query_one("#operations_list", ListView)
        operations_list.clear()
        
        for idx, op in enumerate(operations):
            operations_list.append(ListItem(
                Static(f"{idx + 1}. {op.display}"),
                id=f"op_{op.id}"
            ))
        
        # Auto-show if operations exist
        self.visible = len(operations) > 0
    
    def action_move_up(self) -> None:
        """Move selected operation up in sequence."""
        operations_list = self.query_one("#operations_list", ListView)
        if operations_list.index > 0:
            # Swap operations
            idx = operations_list.index
            self.operations[idx], self.operations[idx - 1] = \
                self.operations[idx - 1], self.operations[idx]
            
            # Trigger reapply
            self.post_message(self.OperationsReordered(self.operations))
            
            # Refresh UI
            self.refresh_operations(self.operations)
            operations_list.index = idx - 1
    
    def action_move_down(self) -> None:
        """Move selected operation down in sequence."""
        operations_list = self.query_one("#operations_list", ListView)
        if operations_list.index < len(self.operations) - 1:
            idx = operations_list.index
            self.operations[idx], self.operations[idx + 1] = \
                self.operations[idx + 1], self.operations[idx]
            
            self.post_message(self.OperationsReordered(self.operations))
            self.refresh_operations(self.operations)
            operations_list.index = idx + 1
    
    def action_edit_operation(self) -> None:
        """Edit selected operation."""
        operations_list = self.query_one("#operations_list", ListView)
        if operations_list.index is not None:
            op = self.operations[operations_list.index]
            self.post_message(self.OperationEdit(op))
    
    def action_remove_operation(self) -> None:
        """Remove selected operation."""
        operations_list = self.query_one("#operations_list", ListView)
        if operations_list.index is not None:
            op = self.operations.pop(operations_list.index)
            self.post_message(self.OperationRemoved(op))
            self.refresh_operations(self.operations)
    
    # Custom messages
    class OperationsReordered(Message):
        def __init__(self, operations: list):
            super().__init__()
            self.operations = operations
    
    class OperationEdit(Message):
        def __init__(self, operation):
            super().__init__()
            self.operation = operation
    
    class OperationRemoved(Message):
        def __init__(self, operation):
            super().__init__()
            self.operation = operation
```

### Add CSS for Right Sidebar

```python
#operations_sidebar {
    width: 0;
    height: 100%;
    transition: width 100ms;
    background: $panel-darken-1;
    border-left: solid $accent;
}

#operations_sidebar.visible {
    width: 25%;
}

#operations_list {
    height: 1fr;
}
```

---

## Step 5: Test the Implementation

### Manual Testing

```bash
# Run the application
uv run kw load tests/e2e/Titanic-Dataset.csv

# Test filter sidebar
1. Press Ctrl+F
2. Select column "Age"
3. Select operator ">"
4. Enter value "25"
5. Click Apply
6. Verify: Right sidebar appears with "Filter: Age > 25"
7. Verify: Data table shows filtered results

# Test operation reordering
1. Apply second filter (Ctrl+F)
2. Focus right sidebar
3. Press Ctrl+Up/Down to reorder
4. Verify: Data table updates with reordered operations
```

### Unit Tests

**File**: `tests/unit/test_filter_sidebar.py`

```python
import pytest
from textual.widgets import Select, Input
from kittiwake.widgets.sidebars.left_sidebar import FilterSidebar

@pytest.mark.asyncio
async def test_filter_sidebar_apply():
    """Test filter sidebar collects form values."""
    sidebar = FilterSidebar(columns=["age", "name"])
    
    async with sidebar.app.run_test() as pilot:
        # Fill form
        column_select = sidebar.query_one("#column_select", Select)
        column_select.value = "age"
        
        operator_select = sidebar.query_one("#operator_select", Select)
        operator_select.value = ">"
        
        value_input = sidebar.query_one("#value_input", Input)
        value_input.value = "25"
        
        # Track callback
        result = None
        def callback(params):
            nonlocal result
            result = params
        
        sidebar.callback = callback
        
        # Click apply
        apply_btn = sidebar.query_one("#apply_btn")
        await pilot.click(apply_btn)
        
        # Verify
        assert result == {
            "column": "age",
            "operator": ">",
            "value": "25"
        }
```

---

## Step 6: Next Features to Implement

### Priority Order

1. **Search sidebar** (similar to filter)
2. **Aggregate sidebar** (multiple inputs)
3. **Dataset switcher tabs** (top of screen)
4. **Save analysis dialog** (modal or sidebar)
5. **Export notebook dialog**

### Common Patterns

- All operation sidebars follow same structure: form → params → builder → operation
- Right sidebar automatically shows on first operation
- All operations support edit (reopen sidebar with pre-filled params)
- All keyboard shortcuts defined in main screen BINDINGS

---

## Troubleshooting

### Sidebar not showing

**Check**:
1. CSS classes: Should be `visible` not `hidden`
2. Layer configuration: `Screen { layers: base overlay; }`
3. Dock setting: `dock: left` for left sidebar

### Operations not reapplying

**Check**:
1. Dataset.operations list is updated
2. OperationBuilder.build_operation is called
3. Dataset.df is reassigned (not mutated)

### Performance issues

**Solutions**:
1. Use `.head(100)` for UI preview
2. Lazy evaluation: `nw.scan_csv()` instead of `nw.read_csv()`
3. Cache operation results

---

**Quick Start Version**: 1.0  
**Last Updated**: 2026-01-09  
**Next**: Implement remaining sidebars and export functionality
