# Kittiwake TUI Data Explorer

A powerful terminal-based interactive data exploration tool that brings the speed and flexibility of command-line workflows to data analysis. Built with Textual and Narwhals, Kittiwake provides a keyboard-first interface for exploring, filtering, transforming, and exporting datasets.

## Overview

Kittiwake is designed for data analysts and engineers who prefer terminal-based workflows. It combines the interactivity of GUI tools with the efficiency of CLI operations, supporting lazy evaluation for large datasets and backend-agnostic dataframe operations.

**Key Highlights**:
- 🚀 **Lazy & Eager Execution Modes**: Choose between lazy evaluation for massive datasets or eager loading for interactive analysis
- 📊 **Multi-Dataset Workspace**: Work with up to 10 datasets simultaneously with tab-based navigation
- 🔍 **Interactive Operations**: Filter, search, aggregate, and transform data with keyboard-driven sidebars
- 💾 **Save & Export**: Save analysis history and export to Python, Jupyter, or Marimo notebooks
- 🎯 **Backend Agnostic**: Automatically uses Polars, Pandas, or PyArrow through Narwhals

## Features

- ✅ **Data Loading**
  - Local files (CSV, Parquet, JSON, Excel)
  - Remote URLs (HTTP/HTTPS)
  - Lazy loading with `scan_csv()` / `scan_parquet()` for large datasets
  - Automatic backend detection (Polars → Pandas → PyArrow)

- ✅ **Interactive Exploration**
  - Paginated table view (500-1000 rows per page)
  - Multi-dataset tabs (up to 10 datasets)
  - Column type detection with color-coded headers
  - Keyboard-first navigation

- ✅ **Data Operations**
  - Filter rows with multiple operators (=, ≠, >, <, ≥, ≤, contains)
  - Search across all columns or specific columns
  - Operation history with edit/remove/reorder capabilities
  - Sidebar-based operation configuration

- ✅ **Save & Export**
  - Save analysis history to DuckDB
  - Export operation sequences to:
    - Python scripts (.py)
    - Jupyter notebooks (.ipynb)
    - Marimo notebooks (.py)
  - Reload saved analyses

## Quick Start

For detailed implementation guides and architecture details, see the [Quick Start Guide](specs/001-tui-data-explorer/quickstart.md).

### Installation

**Prerequisites**: Python >=3.13

```bash
# Clone the repository
git clone https://github.com/yourusername/kittiwake.git
cd kittiwake

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Basic Usage

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

**Tip**: Use `kw load <files>` to pre-load datasets. Running `kw` alone launches an empty workspace where you can load datasets interactively.

### Lazy vs Eager Execution

Kittiwake supports two execution modes optimized for different workflows:

**Lazy Mode** (Default for large files):
```bash
# Automatically uses scan_csv() for files > 100MB
uv run kw load large_dataset.csv
# Data is streamed on-demand, minimal memory usage
```

**Eager Mode** (Default for smaller files):
```bash
# Fully loads data into memory for interactive operations
uv run kw load small_dataset.csv
# Faster operations, full dataset in memory
```

The mode is automatically selected based on file size, but you can manually control it through the UI with `Ctrl+M` (mode switch).

### Keyboard Shortcuts

Press `?` or `Ctrl+?` in the application to see all keyboard shortcuts. Key bindings include:

**Navigation**:
- `Arrow Keys` - Navigate table cells
- `Page Up/Down` - Navigate pages
- `Tab / Shift+Tab` - Switch datasets

**Operations**:
- `Ctrl+F` - Open filter sidebar
- `Ctrl+S` - Save analysis
- `Ctrl+E` - Export to notebook
- `Ctrl+?` - Show help overlay
- `q` - Quit application

For the complete list of shortcuts and detailed usage examples, see the [Quick Start Guide](specs/001-tui-data-explorer/quickstart.md).

## Architecture

```
src/kittiwake/
├── models/          # Data models (Dataset, DatasetSession, Operation)
├── widgets/         # Textual UI widgets (DatasetTable, DatasetTabs, HelpOverlay)
├── screens/         # Application screens (MainScreen)
├── services/        # Business logic (DataLoader, NarwhalsOps, Persistence)
└── utils/          # Utilities (keybindings, async helpers)
```

## Development Status

### ✅ Completed Features
- Project setup and infrastructure
- Core data models and services
- Dataset loading (local and remote)
- TUI with pagination and dataset tabs
- Multi-dataset workspace (up to 10 datasets)
- Keyboard navigation and help overlay
- Filter and search operations
- Operations history sidebar with edit/remove/reorder
- Save analysis to DuckDB
- Export to Python, Jupyter, and Marimo notebooks
- Column type detection and color-coded display
- Lazy and eager execution mode switching
- Error handling and user feedback

### 🚧 In Progress
- Aggregation and group-by operations
- Pivot table functionality

### 📋 Planned Features
- Dataset joins and merges
- Advanced column operations (rename, transform, derive)
- Custom operation templates
- Query history and replay
- Performance profiling

For detailed implementation status, see the [feature specification](specs/001-tui-data-explorer/spec.md) and [task list](specs/001-tui-data-explorer/tasks.md).

## Technical Details

### Dependencies
- **Textual** (>=7.0.1) - Terminal UI framework
- **Narwhals** (>=2.15.0) - Backend-agnostic DataFrame library
- **Typer** (>=0.9.0) - CLI framework
- **DuckDB** (>=0.10.0) - Persistence layer
- **httpx** (>=0.27.0) - Async HTTP client
- **nbformat** (>=5.10.0) - Jupyter notebook format
- **Jinja2** (>=3.1.0) - Template engine for export

### Backend Detection
Kittiwake automatically detects and uses the best available backend:
1. **Polars** (preferred) - Fastest performance
2. **Pandas** - Fallback if Polars unavailable
3. **PyArrow** - Fallback if neither available

### Performance
- Lazy loading with `scan_csv()` / `scan_parquet()`
- Pagination: 500-1000 rows per page
- Async data loading to prevent UI blocking
- Memory-efficient schema inspection with `collect_schema()`

## Testing

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

# Test lazy/eager workflow
uv run pytest tests/integration/test_lazy_eager_workflow.py
```

## License

[To be determined]

## Contributing

This project follows a specification-driven development approach. All features are designed and documented before implementation:

1. **Feature Specifications**: See `/specs/001-tui-data-explorer/spec.md` for detailed feature requirements
2. **Implementation Plan**: See `/specs/001-tui-data-explorer/plan.md` for architecture and design decisions
3. **Task Tracking**: See `/specs/001-tui-data-explorer/tasks.md` for implementation progress
4. **Quick Start Guide**: See `/specs/001-tui-data-explorer/quickstart.md` for developer onboarding

Before contributing:
- Review the [constitution](/.specify/memory/constitution.md) for project principles
- Check the [task list](specs/001-tui-data-explorer/tasks.md) for available work
- Run `uv run pytest` to ensure tests pass
- Follow the existing code style (enforced by `ruff`)

### Development Commands

```bash
# Code formatting and linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/

# Run development version
uv run python -m kittiwake.cli load data.csv
```

## Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Amazing TUI framework
- [Narwhals](https://github.com/narwhals-dev/narwhals) - DataFrame interoperability layer
