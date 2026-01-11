# Quick Start Guide: TUI Data Explorer

**Branch**: `001-tui-data-explorer` | **Date**: 2026-01-10
**For**: Developers and users of Kittiwake TUI Data Explorer

This guide provides step-by-step instructions for using and understanding the TUI Data Explorer implementation.

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
cd kittiwake

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

### Available Sidebars

The implementation includes multiple sidebars for different operations:

- **FilterSidebar**: Filter rows by column values (`src/kittiwake/widgets/sidebars/filter_sidebar.py`)
- **SearchSidebar**: Search across all columns (`src/kittiwake/widgets/sidebars/search_sidebar.py`)
- **AggregateSidebar**: Compute summary statistics (`src/kittiwake/widgets/sidebars/aggregate_sidebar.py`)
- **PivotSidebar**: Create pivot tables (`src/kittiwake/widgets/sidebars/pivot_sidebar.py`)
- **JoinSidebar**: Merge datasets (`src/kittiwake/widgets/sidebars/join_sidebar.py`)
- **OperationsSidebar**: Show and manage operations history (`src/kittiwake/widgets/sidebars/operations_sidebar.py`)

---

## Step 3: Quick Usage Guide

### Load Datasets

```bash
# Launch with empty workspace
uv run kw

# Load one or more datasets on startup
uv run kw load data.csv
uv run kw load file1.csv file2.parquet file3.json

# Load from URLs
uv run kw load https://example.com/data.csv

# Mix local and remote sources
uv run kw load local.csv https://example.com/data.json
```

### Basic Operations

1. **Filter Data**: Press `Ctrl+F` to open filter sidebar
   - Select column, operator, and value
   - Press Enter to apply

2. **Search**: Press `Ctrl+H` to search across all columns
   - Enter search term
   - Press Enter to apply

3. **Aggregate**: Press `A` to open aggregate sidebar
   - Select columns and aggregation functions
   - Optional: Select group-by columns

4. **Pivot**: Press `P` to open pivot sidebar
   - Select row dimensions, column dimensions, and values
   - Choose aggregation function

5. **Join**: Press `Ctrl+J` to join two datasets
   - Select second dataset and join columns
   - Choose join type (inner, left, outer, etc.)

### Execution Modes

Kittiwake supports two execution modes:

**Lazy Mode** (default for large files):
- Operations are queued and not executed immediately
- Press `Ctrl+E` to execute the next queued operation
- Press `Ctrl+Shift+E` to execute all queued operations
- Minimizes memory usage for large datasets

**Eager Mode** (default for smaller files):
- Operations execute immediately when applied
- Faster feedback for interactive analysis
- Uses more memory

Toggle between modes with `Ctrl+M`

### Manage Operations

The right sidebar shows all operations (queued and executed):

- **View operations**: Operations appear in right sidebar automatically
- **Edit operation**: Press `Enter` on selected operation
- **Remove operation**: Press `Delete` on selected operation
- **Reorder operations**: Press `Ctrl+Up` or `Ctrl+Down`
- **Clear all operations**: Press `Ctrl+Shift+X`

### Save and Export

1. **Save Analysis**: Press `Ctrl+S`
   - Enter analysis name and description
   - Saved to `~/.kittiwake/analyses.db`

2. **Load Analysis**: Press `Ctrl+L`
   - Select saved analysis from list
   - Dataset and operations are restored

3. **Export**: Press `E` in saved analyses list
   - Choose format: Python script, Jupyter notebook, or Marimo notebook
   - Export to specified file path

---

## Step 4: Keyboard Shortcuts

Press `?` or `Ctrl+?` in the application to see all keyboard shortcuts.

### Navigation
- `Arrow Keys` - Navigate table cells
- `Page Up/Down` - Navigate pages
- `Tab / Shift+Tab` - Switch datasets
- `Ctrl+Left/Right` - Jump 5 columns
- `Enter / V` - View full cell content
- `Ctrl+Y` - Copy cell to clipboard

### Operations
- `Ctrl+F` - Open filter sidebar
- `Ctrl+H` - Open search sidebar
- `A` - Open aggregate sidebar
- `P` - Open pivot sidebar
- `Ctrl+J` - Open join sidebar
- `Ctrl+E` - Execute next operation (lazy mode)
- `Ctrl+Shift+E` - Execute all operations (lazy mode)
- `Ctrl+M` - Toggle execution mode
- `Ctrl+R` - Reload dataset
- `Ctrl+Z` / `Ctrl+Shift+Z` - Undo / Redo

### Dataset Management
- `Ctrl+S` - Save analysis
- `Ctrl+L` - Load saved analysis
- `Ctrl+D` - Toggle split pane mode
- `Ctrl+W` - Close current dataset
- `Tab` - Next dataset
- `Shift+Tab` - Previous dataset

### Help and Exit
- `?` - Show help overlay
- `q` - Quit application

---

## Step 5: Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/unit/
uv run pytest tests/integration/

# Test with sample data
uv run kw load tests/e2e/Titanic-Dataset.csv

# Test empty workspace
uv run kw
```

### Manual Testing Workflow

```bash
# 1. Launch with test data
uv run kw load tests/e2e/Titanic-Dataset.csv

# 2. Test filter sidebar
# Press Ctrl+F
# Select column "Age"
# Select operator ">"
# Enter value "25"
# Press Enter
# Verify: Right sidebar shows filter operation
# Verify: Data table shows filtered results

# 3. Test lazy mode (default for large files)
# Apply multiple filters
# Verify: Operations show as "queued" (⏳ icon)
# Press Ctrl+E to execute next
# Verify: Operation shows as "executed" (✓ icon)
# Press Ctrl+Shift+E to execute all

# 4. Test mode toggle
# Press Ctrl+M
# Select "Execute All" or "Clear All"
# Verify: Mode changes (button shows ⚡ LAZY or ▶ EAGER)

# 5. Test operation management
# Focus right sidebar
# Press Enter to edit operation
# Press Delete to remove operation
# Press Ctrl+Up/Down to reorder

# 6. Test save and load
# Press Ctrl+S
# Enter name and description
# Press Ctrl+L to load
# Verify: Dataset and operations restored

# 7. Test export
# In saved analyses list, press E
# Choose format and path
# Verify: File created with correct code
```

---

## Step 6: Common Patterns

### Adding New Operations

All operation sidebars follow the same pattern:

1. **Create sidebar widget** in `src/kittiwake/widgets/sidebars/`
2. **Add code generation** in `src/kittiwake/services/narwhals_ops.py`
3. **Integrate with MainScreen** by:
   - Adding keybinding to BINDINGS list
   - Creating action method (e.g., `action_aggregate`)
   - Composing sidebar widget in `compose()` method
   - Handling sidebar messages (e.g., `FilterApplied`, `AggregateApplied`)
4. **Update operations sidebar** to show new operation type
5. **Add tests** in `tests/unit/`

### Operation Flow

1. User opens sidebar via keybinding
2. Sidebar collects form inputs
3. Sidebar sends message with params (e.g., `FilterApplied(params)`)
4. MainScreen handles message:
   - Builds operation code via `OperationBuilder`
   - Calls `dataset.apply_operation(operation_code)`
   - Updates UI (refresh table, operations sidebar)
   - Shows notification

### Lazy vs Eager Execution

- **Lazy mode**: Operations queued in `dataset.queued_operations`, not executed
- **Eager mode**: Operations executed immediately via `dataset.execute_operation()`
- Dataset model handles both modes automatically via `apply_operation()` method
- ExecutionManager is not needed - execution handled directly in Dataset model

---

## Step 7: Troubleshooting

### Sidebar not showing

**Check**:
1. CSS classes: Sidebar should have `visible` class, not `hidden`
2. Keybindings: Verify action method exists in MainScreen
3. Widget composition: Verify sidebar is composed in `compose()` method

### Operations not executing

**Check**:
1. Execution mode: Is it lazy or eager? (Check operations sidebar mode button)
2. Dataset state: Does dataset have valid dataframe?
3. Operation code: Is code generation correct in `narwhals_ops.py`?

### Performance issues

**Solutions**:
1. Use lazy mode for large datasets
2. Reduce pagination limit (default: 500 rows)
3. Check if operations are executing on correct dataset
4. Use `nw.scan_csv()` instead of `nw.read_csv()` for lazy loading

### Tests failing

**Check**:
1. All dependencies installed: `uv sync`
2. Python version >=3.13: `python --version`
3. Database directory exists: `~/.kittiwake/`

---

## Implementation Status

### ✅ Completed Features
- All sidebars (filter, search, aggregate, pivot, join)
- Operations sidebar with state indicators (⏳ queued, ✓ executed, ✗ failed)
- Lazy and eager execution modes
- Execution controls (execute next, execute all, clear all)
- Save/load analyses to DuckDB
- Export to Python, Jupyter, Marimo notebooks
- Multi-dataset workspace with tabs
- Column type detection and color-coded headers
- Cell clipboard copy
- Keyboard navigation
- Split pane mode for dataset comparison

### 🚧 In Progress
- Summary panel for aggregation results
- Pivot table widget with expand/collapse

### 📋 Planned
- Column filtering UI
- Async loading with progress indicators for large datasets
- Workflow save/reuse

---

**Quick Start Version**: 2.0
**Last Updated**: 2026-01-10
**Validation Status**: ✅ All commands and workflows tested successfully
