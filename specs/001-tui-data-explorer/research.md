# Research: TUI Data Explorer Implementation

**Feature**: 001-tui-data-explorer  
**Date**: 2026-01-09  
**Status**: Complete - All unknowns resolved

## Executive Summary

This document consolidates research findings for implementing the TUI Data Explorer with lazy/eager execution modes. All 8 research tasks have been completed, resolving implementation patterns for:

1. Textual sidebar architecture (overlay vs push)
2. Execution mode toggle UI/UX
3. Operation state visualization (queued vs executed)
4. DuckDB async operations
5. Multi-choice modal prompts
6. Export template generation (Python/marimo/Jupyter)
7. Operation execution sequencing
8. Multi-dataset navigation with independent states

**Key Technologies Validated**:
- ✅ Textual 7.0+ for sidebar architecture and reactive state management
- ✅ Rich markup for icon + color coding in operations list
- ✅ DuckDB with thread-safe connection-per-worker pattern
- ✅ Jinja2 for code generation templates
- ✅ narwhals lazy evaluation for large datasets

---

## R1: Textual Sidebar Implementation Patterns

**Question**: How to implement overlay (left) vs push (right) sidebars in Textual?

### Key Findings

**Overlay Sidebar (Left - 30% width)**:
- Use `Container` with `layer="overlay"` CSS property
- Absolute positioning with `z-index` higher than data table
- Semi-transparent background via `background: $surface 90%`
- Keyboard shortcut (Ctrl+F/Ctrl+H) toggles visibility via `display: none`

**Push Sidebar (Right - 25% width)**:
- Use Grid layout: `grid-size: 2 1` with columns `3fr 1fr`
- Sidebar compressed data table to 75% width when visible
- Reactive width adjustment via `watch_show_operations_sidebar()`
- Auto-show on first operation, hide when empty

**Implementation Pattern**:
```python
# main_screen.tcss
#main-grid {
    grid-size: 1 1;  /* Initially full width */
}

#main-grid.with-right-sidebar {
    grid-size: 2 1;  /* Switch to 2-column when sidebar visible */
    grid-columns: 3fr 1fr;  /* 75% data, 25% sidebar */
}

#filter-sidebar {
    layer: overlay;
    dock: left;
    width: 30%;
    background: $surface 90%;
    display: none;  /* Hidden by default */
}
```

**Simultaneous Sidebars**:
- Both can be visible: left overlays (30%), right pushes data to 75%
- Effective data viewing area: 45% width (75% - 30% overlay)
- Terminal minimum width check: 80 columns enforced via SC-010

**Reference**: See detailed sidebar architecture in existing code:
- `src/kittiwake/widgets/sidebars/filter_sidebar.py` (overlay implementation)
- `src/kittiwake/widgets/sidebars/operations_sidebar.py` (push implementation)

---

## R2: Execution Mode Toggle UI Patterns

**Question**: How to display and toggle lazy/eager execution mode in right sidebar header?

### Key Findings

**UI Pattern**:
```
┌─────────────────────────────┐
│ Operations  [⚡ LAZY ▼]     │  ← Header with mode toggle button
├─────────────────────────────┤
│ ⏸ Filter: age > 25         │
│ ⏸ Select: Name, Age        │
│ ✓ Sort: Age desc           │
└─────────────────────────────┘
```

**Textual Implementation**:
```python
class OperationsSidebar(Static):
    execution_mode: reactive[str] = reactive("lazy")  # "lazy" | "eager"
    
    def compose(self) -> ComposeResult:
        with Horizontal(id="sidebar-header"):
            yield Static("Operations", id="title")
            yield Button(
                self._format_mode_label(),
                id="mode-toggle-btn",
                variant="warning"  # Yellow for lazy
            )
    
    def _format_mode_label(self) -> str:
        icons = {"lazy": "⚡", "eager": "▶"}
        return f"{icons[self.execution_mode]} {self.execution_mode.upper()}"
    
    def watch_execution_mode(self, old_mode: str, new_mode: str) -> None:
        """React to mode changes - update button styling."""
        button = self.query_one("#mode-toggle-btn", Button)
        button.label = self._format_mode_label()
        button.variant = "success" if new_mode == "eager" else "warning"
        
        # Show notification
        self.app.notify(
            f"Execution mode: {new_mode.upper()}",
            severity="information",
            timeout=2
        )
```

**Keyboard Shortcut (Ctrl+M)**:
```python
# In main_screen.py
BINDINGS = [
    Binding("ctrl+m", "toggle_execution_mode", "Toggle Mode", show=True),
]

def action_toggle_execution_mode(self) -> None:
    """Toggle lazy/eager mode with queued operations check."""
    dataset = self.session.active_dataset
    sidebar = self.query_one("#operations-sidebar", OperationsSidebar)
    
    # Check if switching from lazy to eager with queued operations
    if sidebar.execution_mode == "lazy" and len(dataset.queued_operations) > 0:
        # Show prompt modal (see R5)
        self.push_screen(ModeSwitchPromptModal(dataset), self._handle_mode_switch_choice)
    else:
        # Switch immediately
        sidebar.execution_mode = "eager" if sidebar.execution_mode == "lazy" else "lazy"
```

**Visual Feedback**:
- Color coding: Yellow (warning variant) for lazy, green (success variant) for eager
- Icon prefix: ⚡ (lightning) for lazy, ▶ (play) for eager
- Button animation: Brief accent color flash on mode change
- Toast notification: "Execution mode: LAZY" appears for 2 seconds

---

## R3: Operation State Visualization

**Question**: How to implement icon + color coding for queued vs executed operations in Textual ListView?

### Key Findings

**Rich Markup Pattern**:
```python
# Queued operation (yellow)
"[yellow]⏸ Filter: age > 25[/yellow]"

# Executed operation (green)
"[green]✓ Filter: age > 25[/green]"

# Failed operation (red)
"[red]✗ Filter: age > 25[/red]"
```

**ListView Implementation**:
```python
def refresh_operations(self, operations: list[Operation]) -> None:
    """Update operations list with state visualization."""
    operations_list = self.query_one("#operations_list", ListView)
    operations_list.clear()
    
    for idx, op in enumerate(operations):
        # Choose icon and color based on state
        if op.state == "executed":
            icon, color = "✓", "green"
        elif op.state == "failed":
            icon, color = "✗", "red"
        else:  # queued
            icon, color = "⏸", "yellow"
        
        # Create Rich markup
        display_text = f"[{color}]{icon} {idx + 1}. {op.display}[/{color}]"
        
        operations_list.append(
            ListItem(Static(display_text), id=f"op_{op.id}")
        )
```

**Unicode Symbol Support**:
- ⏸ (U+23F8) - Pause Button - universal support in modern terminals
- ✓ (U+2713) - Check Mark - widely supported
- ✗ (U+2717) - Ballot X - widely supported

**Accessibility**:
- Icons provide non-color fallback for colorblind users
- Pause (waiting) vs checkmark (done) vs X (failed) are universally understood
- Color enhances but doesn't replace semantic meaning

**CSS Enhancements**:
```css
/* operations_sidebar.tcss */
#operations_list {
    border: solid $primary;
    height: 1fr;
}

#operations_list > ListItem:hover,
#operations_list > ListItem.-highlighted {
    background: $boost;
}

#operations_list > ListItem.-selected {
    background: $accent;
}
```

---

## R4: DuckDB Async Operations in Textual

**Question**: How to perform DuckDB operations without blocking Textual UI thread?

### Key Findings

**Critical**: DuckDB is **NOT async-aware** - requires thread workers, not coroutines.

**Thread-Safe Pattern**:
```python
# Connection-per-thread strategy (REQUIRED)
import threading
import duckdb

class DuckDBManager:
    _connections: dict[int, duckdb.DuckDBPyConnection] = {}
    _write_lock = threading.Lock()
    
    @classmethod
    def get_connection(cls) -> duckdb.DuckDBPyConnection:
        """Get thread-local connection to DuckDB."""
        thread_id = threading.get_ident()
        if thread_id not in cls._connections:
            cls._connections[thread_id] = duckdb.connect(
                database="~/.kittiwake/analyses.db",
                read_only=False
            )
        return cls._connections[thread_id]
```

**Textual Worker Pattern**:
```python
# In app.py
@work(thread=True, exit_on_error=False)
async def save_analysis_async(self, analysis: SavedAnalysis) -> None:
    """Save analysis to DuckDB in background thread."""
    try:
        conn = DuckDBManager.get_connection()
        
        with DuckDBManager._write_lock:  # Serialize writes
            conn.execute("""
                INSERT INTO saved_analyses (name, description, operations, ...)
                VALUES (?, ?, ?, ...)
            """, [analysis.name, analysis.description, ...])
        
        # Update UI from worker thread
        self.call_from_thread(
            self.notify,
            f"Saved: {analysis.name}",
            severity="information"
        )
    except duckdb.Error as e:
        self.call_from_thread(
            self.notify_error,
            f"Failed to save analysis: {e}"
        )
```

**Key Rules**:
1. **One connection per thread** - DuckDB connections are NOT thread-safe
2. **Serialize writes** - Use `threading.Lock()` for INSERT/UPDATE/DELETE
3. **Concurrent reads OK** - Multiple threads can SELECT simultaneously
4. **Use `call_from_thread()`** - All UI updates from workers must use this
5. **Never share cursors** - Each thread needs its own connection
6. **Set `exit_on_error=False`** - Prevent worker exceptions from crashing app

**Progress Feedback**:
```python
# For long queries (>500ms)
def action_load_saved_analyses(self) -> None:
    """Load saved analyses with progress feedback."""
    # Show loading indicator
    self.query_one("#analyses_list").loading = True
    
    # Run in background
    self.run_worker(self.load_analyses_worker)

@work(thread=True)
async def load_analyses_worker(self) -> list[SavedAnalysis]:
    analyses = fetch_from_duckdb()
    
    # Update UI
    self.call_from_thread(self._update_analyses_list, analyses)
    self.call_from_thread(
        lambda: setattr(self.query_one("#analyses_list"), "loading", False)
    )
```

**Reference**: Full implementation details in `research-duckdb-async-textual.md`

---

## R5: Modal Prompt for Mode Switch

**Question**: Best pattern for multi-choice modal prompts in Textual?

### Key Findings

**ModalScreen Pattern**:
```python
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Horizontal, Vertical

class ModeSwitchPromptModal(ModalScreen[str]):
    """Prompt when switching lazy→eager with queued operations."""
    
    BINDINGS = [
        Binding("1,e", "choice_execute", "Execute All", show=True),
        Binding("2,c", "choice_clear", "Clear All", show=True),
        Binding("3,escape", "choice_cancel", "Cancel", show=True),
    ]
    
    def __init__(self, dataset: Dataset):
        super().__init__()
        self.dataset = dataset
    
    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Static(
                f"You have {len(self.dataset.queued_operations)} queued operations.\n"
                "Choose action:",
                id="modal-message"
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Execute All (1/E)", id="btn-execute", variant="primary")
                yield Button("Clear All (2/C)", id="btn-clear", variant="warning")
                yield Button("Cancel (3/Esc)", id="btn-cancel")
    
    def action_choice_execute(self) -> None:
        """Execute all queued operations and switch to eager mode."""
        self.dismiss("execute")
    
    def action_choice_clear(self) -> None:
        """Clear queued operations and switch to eager mode."""
        self.dismiss("clear")
    
    def action_choice_cancel(self) -> None:
        """Stay in lazy mode."""
        self.dismiss("cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-execute":
            self.action_choice_execute()
        elif event.button.id == "btn-clear":
            self.action_choice_clear()
        elif event.button.id == "btn-cancel":
            self.action_choice_cancel()
```

**Usage in main_screen.py**:
```python
def action_toggle_execution_mode(self) -> None:
    dataset = self.session.active_dataset
    sidebar = self.query_one("#operations-sidebar", OperationsSidebar)
    
    if sidebar.execution_mode == "lazy" and len(dataset.queued_operations) > 0:
        # Show modal and wait for result
        self.push_screen(
            ModeSwitchPromptModal(dataset),
            self._handle_mode_switch_choice
        )
    else:
        # Switch immediately
        sidebar.execution_mode = "eager" if sidebar.execution_mode == "lazy" else "lazy"

def _handle_mode_switch_choice(self, choice: str) -> None:
    """Handle user's modal choice."""
    dataset = self.session.active_dataset
    sidebar = self.query_one("#operations-sidebar", OperationsSidebar)
    
    if choice == "execute":
        # Execute all queued operations
        self.action_execute_all()
        sidebar.execution_mode = "eager"
    elif choice == "clear":
        # Clear queued operations
        dataset.queued_operations.clear()
        sidebar.execution_mode = "eager"
        sidebar.refresh_operations()
    # elif choice == "cancel": do nothing
```

**Keyboard Shortcuts**:
- Dual binding: `"1,e"` means both `1` key and `e` key trigger same action
- Mnemonic: E=Execute, C=Clear, Esc=Cancel
- Numbers: 1/2/3 for quick selection without thinking
- Escape: Always dismisses modal (Textual default behavior)

**Result Passing**:
- `ModalScreen[str]` generic parameter defines return type
- `dismiss("execute")` passes string back to caller
- Caller receives result via callback function

---

## R6: Export Template Generation

**Question**: What templating approach for generating Python/marimo/Jupyter notebooks?

### Key Findings

**Templating Approach**: **Jinja2** for all three formats

**Existing Templates** (already in `contracts/`):
1. `export-python.jinja2` - Standalone Python script
2. `export-marimo.jinja2` - marimo reactive notebook
3. `export-jupyter.jinja2` - Jupyter notebook JSON

**Template Context Variables**:
```python
context = {
    "analysis_name": "Titanic Analysis",
    "analysis_description": "Filter and analyze passenger data",
    "generated_at": "2026-01-09T10:30:00Z",
    "kittiwake_version": "0.1.0",
    "dataset_path": "/Users/data/titanic.csv",
    "operation_count": 3,
    "operations": [
        {
            "display": "Filter: Age > 30",
            "code": "df = df.filter(nw.col('Age') > 30)"
        },
        ...
    ],
    "backend_dependencies": ["polars>=0.20.0"]  # marimo-specific
}
```

**Python Script Template Structure**:
```python
#!/usr/bin/env python3
"""{{ analysis_name }}"""

import narwhals as nw

def main():
    df = nw.scan_csv(r"{{ dataset_path }}")
    
    {% for operation in operations %}
    # {{ operation.display }}
    {{ operation.code }}
    {% endfor %}
    
    return df.collect()
```

**marimo Notebook Template Structure**:
```python
# /// script
# requires-python = ">=3.13"
# dependencies = ["narwhals>=2.15.0", "marimo>=0.18.4"]
# ///

import marimo

app = marimo.App()

@app.cell
def __():
    import narwhals as nw
    return nw,

{% for operation in operations %}
@app.cell
def __({% if loop.first %}df{% else %}df_{{ loop.index - 1 }}{% endif %}, nw):
    # {{ operation.display }}
    df_{{ loop.index }} = {{ operation.code }}
    return df_{{ loop.index }},
{% endfor %}
```

**Jupyter Notebook Template Structure**:
```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "source": ["# {{ analysis_name }}"]
    },
    {
      "cell_type": "code",
      "source": ["import narwhals as nw"]
    },
    {% for operation in operations %}
    {
      "cell_type": "code",
      "source": ["{{ operation.code }}"]
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "metadata": {...},
  "nbformat": 4
}
```

**Code Generation Pattern**:
```python
from jinja2 import Environment, FileSystemLoader

def export_analysis(analysis: SavedAnalysis, format: str) -> str:
    env = Environment(loader=FileSystemLoader('contracts/'))
    template = env.get_template(f'export-{format}.jinja2')
    
    context = {
        'operations': [
            {'display': op.display, 'code': op.to_code()}
            for op in analysis.operations
        ],
        ...
    }
    
    return template.render(**context)
```

**Operation Code Serialization**:
```python
# In Operation model
def to_code(self) -> str:
    """Generate Python code for this operation."""
    if self.operation_type == "filter":
        return f"df = df.filter(nw.col('{self.params['column']}') {self.params['operator']} {self.params['value']})"
    elif self.operation_type == "select":
        cols = ", ".join(f"'{c}'" for c in self.params['columns'])
        return f"df = df.select([{cols}])"
    # ... other operation types
```

**Security Considerations**:
- Use raw strings `r"..."` for file paths (Windows safety)
- Escape quotes in JSON strings for Jupyter format
- Validate column names against dataset schema
- No `eval()` or `exec()` - all code generation is templated

**Reference**: Detailed template specifications in `research-code-generation-security.md`

---

## R7: Operation Execution Sequencing

**Question**: How to execute queued operations one-by-one with error handling?

### Key Findings

**ExecutionManager Service Class**:
```python
@dataclass
class ExecutionResult:
    success: bool
    operation: Operation
    error_message: str | None = None
    execution_time_ms: float = 0.0

class ExecutionManager:
    """Manages operation execution in lazy/eager modes."""
    
    def execute_next(self, dataset: Dataset) -> ExecutionResult:
        """Execute next queued operation with error handling."""
        if not dataset.queued_operations:
            return ExecutionResult(success=False, error_message="No queued operations")
        
        operation = dataset.queued_operations[0]  # FIFO
        start_time = time.time()
        
        try:
            # Apply operation to dataset
            dataset.current_frame = eval(
                operation.code,
                {"df": dataset.current_frame, "nw": narwhals}
            )
            
            # Mark as executed
            operation.state = "executed"
            dataset.queued_operations.pop(0)
            dataset.executed_operations.append(operation)
            
            return ExecutionResult(
                success=True,
                operation=operation,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        except Exception as e:
            # Mark as failed but keep in queue
            operation.state = "failed"
            operation.error_message = str(e)
            
            return ExecutionResult(
                success=False,
                operation=operation,
                error_message=self._friendly_error(operation, e)
            )
    
    def execute_all(
        self,
        dataset: Dataset,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> list[ExecutionResult]:
        """Execute all queued operations with stop-on-error."""
        results = []
        total = len(dataset.queued_operations)
        
        for idx in range(total):
            if progress_callback:
                progress_callback(idx + 1, total)
            
            result = self.execute_next(dataset)
            results.append(result)
            
            if not result.success:
                # Stop on first error
                break
        
        return results
    
    def _friendly_error(self, operation: Operation, error: Exception) -> str:
        """Generate user-friendly error message."""
        if "column" in str(error).lower():
            return f"Column error in '{operation.display}': {error}\n" \
                   "The column may have been removed by a previous operation."
        elif "type" in str(error).lower():
            return f"Type mismatch in '{operation.display}': {error}\n" \
                   "Check that the operation is compatible with the data types."
        else:
            return f"Error executing '{operation.display}': {error}"
```

**State Management**:
```python
@dataclass
class Dataset:
    execution_mode: str = "lazy"  # "lazy" | "eager"
    queued_operations: list[Operation] = field(default_factory=list)
    executed_operations: list[Operation] = field(default_factory=list)
    
    def apply_operation(self, operation: Operation) -> None:
        """Apply operation based on execution mode."""
        if self.execution_mode == "eager":
            # Execute immediately
            ExecutionManager().execute_next(self)
        else:
            # Queue for later execution
            operation.state = "queued"
            self.queued_operations.append(operation)
```

**Integration with Textual UI**:
```python
# In main_screen.py
BINDINGS = [
    Binding("ctrl+e", "execute_next", "Execute Next", show=True),
    Binding("ctrl+shift+e", "execute_all", "Execute All", show=True),
]

@work(thread=True, exit_on_error=False)
async def execute_operations_worker(self, execute_all: bool = False) -> None:
    """Execute operations in background thread."""
    dataset = self.session.active_dataset
    manager = ExecutionManager()
    
    if execute_all:
        results = manager.execute_all(dataset, progress_callback=self._update_progress)
        
        # Summary notification
        succeeded = sum(1 for r in results if r.success)
        total = len(results)
        self.call_from_thread(
            self.notify,
            f"Executed {succeeded}/{total} operations",
            severity="information" if succeeded == total else "warning"
        )
    else:
        result = manager.execute_next(dataset)
        
        if result.success:
            self.call_from_thread(
                self.notify,
                f"✓ {result.operation.display} ({result.execution_time_ms:.0f}ms)",
                severity="information"
            )
        else:
            self.call_from_thread(
                self.notify_error,
                result.error_message
            )
    
    # Refresh UI
    self.call_from_thread(self._refresh_operations_sidebar)
    self.call_from_thread(self._refresh_data_table)

def action_execute_next(self) -> None:
    """Execute next queued operation (Ctrl+E)."""
    dataset = self.session.active_dataset
    
    if not dataset.queued_operations:
        self.notify("No queued operations", severity="information")
        return
    
    self.run_worker(self.execute_operations_worker(execute_all=False))

def action_execute_all(self) -> None:
    """Execute all queued operations (Ctrl+Shift+E)."""
    dataset = self.session.active_dataset
    
    if not dataset.queued_operations:
        self.notify("No queued operations", severity="information")
        return
    
    self.run_worker(self.execute_operations_worker(execute_all=True))
```

**Error Handling Strategy**:
- **Stop-on-failure**: Execution stops at first error
- **Preserve queue**: Failed operation stays in `queued_operations` with `state="failed"`
- **Error context**: Friendly messages suggest likely causes
- **User control**: User can fix/remove failed operation and continue

**Visual Feedback**:
- Queued: `[yellow]⏸ Operation[/yellow]`
- Executed: `[green]✓ Operation[/green]`
- Failed: `[red]✗ Operation[/red]`

**Reference**: Full implementation details in `research-operation-execution-sequencing.md`

---

## R8: Multi-Dataset Navigation with Independent States

**Question**: How to manage 10 datasets with independent operation histories?

### Key Findings

**DatasetSession API** (already implemented):
```python
@dataclass
class DatasetSession:
    """Manages collection of loaded datasets."""
    MAX_DATASETS = 10
    
    datasets: dict[UUID, Dataset] = field(default_factory=dict)
    active_dataset_id: UUID | None = None
    split_pane_config: dict[str, Any] | None = None
    
    def add_dataset(self, dataset: Dataset) -> bool:
        """Add dataset to session (max 10)."""
        if len(self.datasets) >= self.MAX_DATASETS:
            return False  # Reject addition
        
        # Auto-rename if name conflicts
        original_name = dataset.name
        counter = 1
        while any(d.name == dataset.name for d in self.datasets.values()):
            dataset.name = f"{original_name}_{counter}"
            counter += 1
        
        self.datasets[dataset.id] = dataset
        if self.active_dataset_id is None:
            self.active_dataset_id = dataset.id
        
        return True
    
    def switch_to_dataset(self, dataset_id: UUID) -> None:
        """Switch active dataset (preserves state implicitly)."""
        if dataset_id in self.datasets:
            self.active_dataset_id = dataset_id
    
    @property
    def active_dataset(self) -> Dataset | None:
        """Get currently active dataset."""
        if self.active_dataset_id:
            return self.datasets.get(self.active_dataset_id)
        return None
```

**State Preservation**:
- **Automatic**: Each `Dataset` holds its own state (queued_operations, executed_operations, current_frame)
- **No explicit save/restore**: Switching datasets just updates `active_dataset_id` pointer
- **Independent histories**: Operations on Dataset A don't affect Dataset B

**UI Widget: Tabs (Recommended)**:
```python
# In main_screen.py
def compose(self) -> ComposeResult:
    yield DatasetTabs(id="dataset_tabs")  # Shows all loaded datasets
    yield DataTable(id="data_table")
    # ... sidebars

# In dataset_tabs.py
class DatasetTabs(Tabs):
    """Tab widget for dataset switching."""
    
    def __init__(self, session: DatasetSession):
        super().__init__()
        self.session = session
    
    def refresh_tabs(self) -> None:
        """Update tabs to reflect loaded datasets."""
        self.clear()
        for dataset in self.session.datasets.values():
            # Show operation counts in tab label
            queued = len(dataset.queued_operations)
            executed = len(dataset.executed_operations)
            label = f"{dataset.name} ({queued}⏸/{executed}✓)"
            self.add_tab(Tab(label, id=str(dataset.id)))
    
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab switch."""
        dataset_id = UUID(event.tab.id)
        self.session.switch_to_dataset(dataset_id)
        # Trigger UI refresh
        self.post_message(DatasetSwitched(dataset_id))
```

**Memory Management**:
```python
def add_dataset(self, dataset: Dataset) -> tuple[bool, str]:
    """Add dataset with proactive warnings."""
    count = len(self.datasets)
    
    if count >= self.MAX_DATASETS:
        return False, f"Limit reached ({count}/{self.MAX_DATASETS}). Close a dataset (Ctrl+W) first."
    
    # Proactive warnings
    if count == 8:
        warning = f"Approaching limit ({count + 1}/10). Close unused datasets."
    elif count == 9:
        warning = f"Almost at limit ({count + 1}/10). One slot remaining."
    else:
        warning = None
    
    self.datasets[dataset.id] = dataset
    return True, warning
```

**CLI Bulk Load Handling**:
```python
# In cli.py
def load_command(paths: list[str]) -> None:
    """Load datasets from CLI arguments."""
    session = DatasetSession()
    
    loaded = []
    skipped = []
    
    for path in paths[:session.MAX_DATASETS]:  # Cap at 10
        dataset = load_dataset(path)
        success, msg = session.add_dataset(dataset)
        if success:
            loaded.append(path)
        else:
            skipped.append(path)
    
    # Warn about excess files
    if len(paths) > session.MAX_DATASETS:
        excess = paths[session.MAX_DATASETS:]
        logger.warning(f"Skipped {len(excess)} files (10-dataset limit): {excess}")
```

**Keyboard Shortcuts**:
- `Tab` / `Shift+Tab`: Navigate between dataset tabs
- `Ctrl+W`: Close active dataset (free up slot)
- `Ctrl+1` to `Ctrl+9`: Jump to specific dataset tab

**Required Modifications for Lazy/Eager Mode**:
- Replace single `operation_history` list with dual `queued_operations` + `executed_operations`
- Add `execution_mode` field to Dataset
- Update tab labels to show operation counts: `sales.csv (3⏸/5✓)`

**Reference**: Full implementation details in `research-multi-dataset-navigation.md`

---

## Implementation Recommendations

### Phase 1: Core Infrastructure (P0)
1. **Update Dataset model**:
   - Add `execution_mode: str = "lazy"`
   - Split `operation_history` → `queued_operations` + `executed_operations`
   - Add `Operation.state` field: "queued" | "executed" | "failed"

2. **Create ExecutionManager service**:
   - Implement `execute_next()` and `execute_all()` methods
   - Add error handling with friendly messages
   - Integrate with Textual workers for non-blocking execution

3. **Update OperationsSidebar**:
   - Add mode toggle button in header (⚡ LAZY / ▶ EAGER)
   - Update `refresh_operations()` to use icon + color coding
   - Wire up Ctrl+M keyboard shortcut

### Phase 2: Execution Controls (P1)
4. **Add execution keybindings**:
   - Ctrl+E: Execute next queued operation
   - Ctrl+Shift+E: Execute all queued operations
   - Both as no-op in eager mode with informational message

5. **Create ModeSwitchPromptModal**:
   - 3-button modal (Execute All / Clear All / Cancel)
   - Keyboard shortcuts (1/E, 2/C, 3/Esc)
   - Show when switching lazy→eager with queued operations

6. **Update Dataset.apply_operation()**:
   - Check `execution_mode` before executing
   - If lazy: queue operation with state="queued"
   - If eager: execute immediately with ExecutionManager

### Phase 3: Export & Persistence (P2)
7. **DuckDB async integration**:
   - Implement `DuckDBManager` with connection-per-thread
   - Add `@work(thread=True)` wrappers for all DB operations
   - Use `call_from_thread()` for UI updates

8. **Export template rendering**:
   - Load Jinja2 templates from `contracts/` directory
   - Implement `Operation.to_code()` method for code generation
   - Add export actions to main screen (Ctrl+X)

### Phase 4: Polish & Testing (P3)
9. **Memory warnings**:
   - Show warnings at 8/9 datasets loaded
   - Reject 11th dataset with clear message
   - Handle CLI bulk load (cap at 10, warn about skipped files)

10. **Update DatasetTabs**:
    - Show operation counts in tab labels: `data.csv (3⏸/5✓)`
    - Highlight active tab
    - Support Ctrl+W to close tabs

---

## Technology Decisions

| Technology | Decision | Rationale |
|------------|----------|-----------|
| **Sidebar architecture** | Textual Container + Grid layout | Native Textual support, reactive, performant |
| **Operation visualization** | Rich markup (icon + color) | Accessible, terminal-native, no dependencies |
| **DuckDB async** | Thread workers with connection-per-thread | Required by DuckDB thread model |
| **Modal prompts** | ModalScreen with dual keybindings (1/E, 2/C) | Textual native, keyboard-first |
| **Export templates** | Jinja2 | Industry standard, maintainable, secure |
| **Execution model** | Stop-on-error with queue preservation | Safe, debuggable, user-friendly |
| **Dataset navigation** | Tabs widget | Space-efficient, intuitive, fits 10-dataset limit |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Terminal compatibility** | Unicode symbols don't render | Use widely-supported symbols (⏸✓✗), test on macOS/Linux/Windows |
| **DuckDB thread contention** | Write operations block | Use write lock, keep writes fast (<50ms target) |
| **Operation execution errors** | Cascade failures in chain | Stop-on-error, friendly messages, preserve queue for fixes |
| **Memory with 10 datasets** | OOM with large files | Use narwhals lazy evaluation, proactive warnings at 8+ datasets |
| **Jinja2 code injection** | Malicious template content | All templates shipped with package, no user-provided templates |

---

## Testing Strategy

### Unit Tests
- `test_execution_manager.py`: Execute next/all, error handling, state transitions
- `test_dataset_session.py`: Add/remove datasets, 10-dataset limit, state switching
- `test_operation_serialization.py`: Operation.to_code() for all 13 operation types
- `test_export_templates.py`: Render templates, validate output syntax

### Integration Tests
- `test_lazy_eager_mode_switching.py`: Mode toggle with queued operations
- `test_duckdb_persistence.py`: Save/load analyses, concurrent access
- `test_multi_dataset_navigation.py`: Switch datasets, preserve independent states

### E2E Tests (Textual pilot)
- `test_keyboard_shortcuts.py`: Ctrl+E, Ctrl+Shift+E, Ctrl+M
- `test_operations_sidebar.py`: Visual feedback, icon + color rendering
- `test_mode_switch_prompt.py`: Modal interaction, result passing

---

## Success Metrics

All research tasks resolved:
- ✅ R1: Sidebar architecture pattern documented
- ✅ R2: Mode toggle UI/UX pattern documented
- ✅ R3: Operation visualization pattern documented
- ✅ R4: DuckDB async pattern documented
- ✅ R5: Modal prompt pattern documented
- ✅ R6: Export templates documented
- ✅ R7: Execution sequencing pattern documented
- ✅ R8: Multi-dataset navigation pattern documented

**No remaining unknowns.** Ready to proceed to Phase 1: Design & Contracts.

---

## References

- **Textual Documentation**: https://textual.textualize.io/
- **Rich Markup**: https://rich.readthedocs.io/en/stable/markup.html
- **DuckDB Python API**: https://duckdb.org/docs/api/python/overview
- **Jinja2 Templates**: https://jinja.palletsprojects.com/
- **narwhals API**: https://narwhals-dev.github.io/narwhals/
- **marimo Notebook Format**: https://docs.marimo.io/

**Detailed Research Files**:
- `research-duckdb-async-textual.md` - DuckDB thread safety patterns
- `research-operation-execution-sequencing.md` - ExecutionManager implementation
- `research-multi-dataset-navigation.md` - DatasetSession patterns
- `research-code-generation-security.md` - Template security considerations
