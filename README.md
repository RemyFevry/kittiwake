# Kittiwake TUI Data Explorer

A terminal-based interactive data exploration tool built with Textual and Narwhals.

## Features (MVP - Phase 3 Complete)

- ✅ Load datasets from local files (CSV, Parquet, JSON, Excel)
- ✅ Load datasets from remote URLs (HTTP/HTTPS)
- ✅ View data in paginated tables (500-1000 rows per page)
- ✅ Switch between multiple datasets (up to 10)
- ✅ Keyboard-first navigation
- ✅ Lazy loading for large datasets
- ✅ Backend-agnostic (Polars, Pandas, PyArrow via Narwhals)

## Installation

```bash
# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

## Usage

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

**Note**: Use the `load` subcommand to pre-load datasets: `kw load <files>`. Bare `kw` launches an empty workspace.

## Keyboard Shortcuts

### Navigation
- **Arrow Keys** - Navigate table cells
- **Page Up/Down** - Navigate table pages
- **Tab** - Switch to next dataset
- **Shift+Tab** - Switch to previous dataset

### Actions
- **f** - Filter rows (coming in Phase 4)
- **a** - Aggregate/Group by (coming in Phase 5)
- **Ctrl+W** - Close current dataset
- **Ctrl+S** - Save analysis (coming in Phase 6)
- **?** - Show help overlay
- **q** - Quit application

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

### Completed (Phase 1-3)
- ✅ Project setup and infrastructure
- ✅ Core data models and services
- ✅ Dataset loading (local and remote)
- ✅ TUI with pagination and tabs
- ✅ Multi-dataset support (up to 10)
- ✅ Keyboard navigation
- ✅ Error handling and user feedback

### Pending (Optional MVP Tasks)
- ⏸️ Split pane mode (T021)
- ⏸️ Loading indicators for >500ms operations (T023)

### Next Phase (Phase 4)
- 🔜 Filter and search functionality
- 🔜 Column-specific filters
- 🔜 Text search across all columns

### Future Phases
- Phase 5: Aggregation and summarization
- Phase 6: Pivot tables
- Phase 7: Dataset joins and merges
- Phase 8: Column operations (select, drop, rename, transform)
- Phase 9: Saved analyses and export (marimo, Python, Jupyter)

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

# Test with sample data
uv run kw load tests/e2e/Titanic-Dataset.csv

# Test empty workspace
uv run kw
```

## License

[To be determined]

## Contributing

This project follows a specification-driven development approach. See `/specs/001-tui-data-explorer/` for detailed specifications.

## Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Amazing TUI framework
- [Narwhals](https://github.com/narwhals-dev/narwhals) - DataFrame interoperability layer
