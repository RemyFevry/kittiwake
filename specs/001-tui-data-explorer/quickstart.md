# Quickstart: TUI Data Explorer Development

**Feature**: 001-tui-data-explorer  
**Date**: 2026-01-07  
**Purpose**: Fast onboarding guide for developers working on kittiwake

---

## Prerequisites

- **Python** >=3.13
- **uv** package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- Modern terminal emulator (iTerm2, Windows Terminal, Alacritty, etc.)

---

## Setup

```bash
# Clone repository
git clone <repository-url>
cd kittiwake

# Switch to feature branch
git checkout 001-tui-data-explorer

# Install dependencies with uv
uv sync

# Install optional backend dependencies (recommended)
uv pip install polars pandas pyarrow

# Verify installation
uv run kw --help
```

---

## Running the Application

```bash
# Launch empty workspace
uv run kw

# Load datasets from CLI
uv run kw load data/sample.csv

# Load multiple datasets
uv run kw load data/sales.csv data/customers.parquet

# Load remote dataset
uv run kw load https://example.com/data.csv
```

---

## Development Workflow

### Project Structure

```text
src/kittiwake/
├── cli.py              # Entry point & Typer CLI
├── app.py              # Main Textual App
├── models/             # Domain entities
├── widgets/            # Reusable UI components
├── screens/            # Full-screen layouts
├── services/           # Business logic
└── utils/              # Helpers

tests/
├── contract/           # API stability tests
├── integration/        # Multi-component tests
└── unit/               # Isolated component tests
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test suite
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/contract

# With coverage
uv run pytest --cov=kittiwake --cov-report=html

# Watch mode (install pytest-watch)
uv run ptw
```

---

## Key Architecture Patterns

### 1. Loading Data (Async Pattern)

```python
# In services/data_loader.py
import narwhals as nw
import httpx
from pathlib import Path

class DataLoader:
    async def load(self, source: str) -> nw.LazyFrame:
        """Load dataset from file or URL."""
        if source.startswith(("http://", "https://")):
            # Download remote file first
            local_path = await self._download(source)
            source = str(local_path)
        
        # Load with narwhals (lazy evaluation)
        if source.endswith('.csv'):
            return nw.scan_csv(source)
        elif source.endswith('.parquet'):
            return nw.scan_parquet(source)
        elif source.endswith('.json'):
            return nw.scan_json(source)
        else:
            raise ValueError(f"Unsupported format: {source}")
    
    async def _download(self, url: str) -> Path:
        """Download file to cache directory."""
        cache_dir = Path.home() / ".kittiwake" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / url.split("/")[-1]
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as response:
                with dest.open("wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        return dest
```

### 2. Running Operations (Worker Pattern)

```python
# In screens/main_screen.py
from textual.screen import Screen
from textual.worker import work
import narwhals as nw

class MainScreen(Screen):
    @work(exclusive=True, thread=True)
    async def apply_filter(self, dataset_id: str, column: str, operator: str, value):
        """Run filter operation in worker thread (doesn't block UI)."""
        dataset = self.app.session.get_dataset(dataset_id)
        
        # Build narwhals expression
        if operator == '>':
            filtered = dataset.frame.filter(nw.col(column) > value)
        elif operator == '==':
            filtered = dataset.frame.filter(nw.col(column) == value)
        # ... more operators
        
        # Materialize result (CPU-intensive, runs in worker)
        result = filtered.collect()
        
        return result
    
    def on_worker_state_changed(self, event):
        """Handle worker completion."""
        if event.worker.name == "apply_filter" and event.worker.is_finished:
            result = event.worker.result
            self.update_table(result)
```

### 3. Keyboard Shortcuts (Bindings Pattern)

```python
# In screens/main_screen.py
from textual.screen import Screen

class MainScreen(Screen):
    BINDINGS = [
        ("f", "filter", "Filter"),
        ("a", "aggregate", "Aggregate"),
        ("ctrl+s", "save_analysis", "Save"),
        ("?", "help", "Help"),
    ]
    
    def action_filter(self):
        """Show filter modal when 'f' is pressed."""
        self.app.push_screen(FilterModal())
    
    def action_aggregate(self):
        """Show aggregation menu when 'a' is pressed."""
        self.app.push_screen(AggregationModal())
    
    def action_save_analysis(self):
        """Save current analysis when Ctrl+S is pressed."""
        self.app.push_screen(SaveAnalysisModal())
    
    def action_help(self):
        """Show help overlay when '?' is pressed."""
        self.app.push_screen(HelpOverlay())
```

### 4. DuckDB Persistence (Repository Pattern)

```python
# In services/persistence.py
import duckdb
from pathlib import Path
from threading import Lock
from models.saved_analysis import SavedAnalysis

class SavedAnalysisRepository:
    _write_lock = Lock()
    
    @staticmethod
    def _get_connection():
        db_path = Path.home() / ".kittiwake" / "analyses.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL")  # Enable concurrent reads
        return conn
    
    def save(self, analysis: SavedAnalysis) -> int:
        """Insert or update saved analysis."""
        with self._write_lock:  # Serialize writes
            conn = self._get_connection()
            if analysis.id is None:
                # INSERT
                result = conn.execute("""
                    INSERT INTO saved_analyses 
                    (name, description, operation_count, dataset_path, operations)
                    VALUES (?, ?, ?, ?, ?)
                    RETURNING id
                """, (
                    analysis.name,
                    analysis.description,
                    analysis.operation_count,
                    analysis.dataset_path,
                    analysis.operations_json()
                )).fetchone()
                analysis.id = result[0]
            else:
                # UPDATE
                conn.execute("""
                    UPDATE saved_analyses
                    SET name=?, description=?, operation_count=?, 
                        dataset_path=?, operations=?, modified_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    analysis.name,
                    analysis.description,
                    analysis.operation_count,
                    analysis.dataset_path,
                    analysis.operations_json(),
                    analysis.id
                ))
            conn.close()
        return analysis.id
    
    def list_all(self) -> list[SavedAnalysis]:
        """List all saved analyses (concurrent reads OK)."""
        conn = self._get_connection()
        results = conn.execute("""
            SELECT id, name, description, created_at, modified_at, 
                   operation_count, dataset_path, operations
            FROM saved_analyses
            ORDER BY modified_at DESC
        """).fetchall()
        conn.close()
        return [SavedAnalysis.from_row(row) for row in results]
```

### 5. Export Code Generation (Template Pattern)

```python
# In services/export_service.py
from jinja2 import Environment, FileSystemLoader
import nbformat
from datetime import datetime

class ExportService:
    def __init__(self):
        template_dir = Path(__file__).parent.parent.parent / "specs" / "001-tui-data-explorer" / "contracts"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def export_marimo(self, analysis: SavedAnalysis, output_path: Path):
        """Generate marimo notebook (.py file)."""
        template = self.jinja_env.get_template("export-marimo.jinja2")
        code = template.render(
            analysis_name=analysis.name,
            analysis_description=analysis.description,
            generated_at=datetime.now().isoformat(),
            dataset_path=analysis.dataset_path,
            operation_count=analysis.operation_count,
            operations=analysis.operations,
            kittiwake_version="0.1.0"
        )
        output_path.write_text(code)
    
    def export_python(self, analysis: SavedAnalysis, output_path: Path):
        """Generate standalone Python script."""
        template = self.jinja_env.get_template("export-python.jinja2")
        code = template.render(
            analysis_name=analysis.name,
            analysis_description=analysis.description,
            generated_at=datetime.now().isoformat(),
            dataset_path=analysis.dataset_path,
            operation_count=analysis.operation_count,
            operations=analysis.operations,
            kittiwake_version="0.1.0"
        )
        output_path.write_text(code)
    
    def export_jupyter(self, analysis: SavedAnalysis, output_path: Path):
        """Generate Jupyter notebook (.ipynb)."""
        template = self.jinja_env.get_template("export-jupyter.jinja2")
        notebook_json = template.render(
            analysis_name=analysis.name,
            analysis_description=analysis.description,
            generated_at=datetime.now().isoformat(),
            dataset_path=analysis.dataset_path,
            operation_count=analysis.operation_count,
            operations=analysis.operations,
            kittiwake_version="0.1.0"
        )
        # Parse JSON and write as nbformat
        import json
        nb_dict = json.loads(notebook_json)
        nb = nbformat.from_dict(nb_dict)
        nbformat.write(nb, str(output_path))
```

---

## Adding New Features

### Adding a New Widget

1. **Create widget file**: `src/kittiwake/widgets/my_widget.py`
   ```python
   from textual.widgets import Static
   
   class MyWidget(Static):
       def compose(self):
           yield Label("Hello")
   ```

2. **Add to screen**: `src/kittiwake/screens/main_screen.py`
   ```python
   from widgets.my_widget import MyWidget
   
   def compose(self):
       yield MyWidget()
   ```

3. **Write unit test**: `tests/unit/test_widgets.py`
   ```python
   def test_my_widget():
       widget = MyWidget()
       assert widget is not None
   ```

### Adding a New Operation Type

1. **Update data model**: `src/kittiwake/models/operations.py`
   ```python
   class SortOperation(Operation):
       def __init__(self, column: str, descending: bool = False):
           self.column = column
           self.descending = descending
       
       def to_dict(self):
           return {
               "type": "sort",
               "column": self.column,
               "descending": self.descending
           }
       
       def apply(self, df: nw.LazyFrame) -> nw.LazyFrame:
           return df.sort(self.column, descending=self.descending)
   ```

2. **Update JSON schema**: `contracts/operations-schema.json`
3. **Update export templates**: Add sort handling to all three templates
4. **Add UI**: Create modal/widget for sort configuration
5. **Write tests**: Unit, integration, and contract tests

---

## Common Tasks

### Debugging TUI Issues

```bash
# Enable Textual devtools (see console logs)
uv run textual console

# In another terminal, run app with devtools
uv run textual run --dev src/kittiwake/cli.py

# Or directly
uv run kw --dev  # if configured in pyproject.toml
```

### Formatting & Linting

```bash
# Format code (add ruff to dev dependencies)
uv run ruff format .

# Lint
uv run ruff check .

# Type checking (add mypy to dev dependencies)
uv run mypy src/kittiwake
```

### Building Distribution

```bash
# Build package
uv build

# Install locally
uv pip install dist/kittiwake-0.1.0-py3-none-any.whl

# Test installed package
kw load data/sample.csv
```

---

## Troubleshooting

### Issue: "No backend available" error
**Solution**: Install at least one backend:
```bash
uv pip install polars  # Recommended for lazy evaluation
# OR
uv pip install pandas
```

### Issue: DuckDB database locked
**Solution**: Ensure no other kittiwake instances are running. WAL mode should prevent this, but check:
```bash
ls ~/.kittiwake/analyses.db*
# Should see: analyses.db, analyses.db-shm, analyses.db-wal
```

### Issue: Textual app doesn't respond to keys
**Solution**: Check terminal compatibility. Some keys may be captured by terminal emulator. Try different terminal or reconfigure bindings.

### Issue: Large file loading is slow
**Solution**: Verify lazy evaluation is working:
```python
# Should return LazyFrame, not DataFrame
df = nw.scan_csv("large.csv")
print(type(df))  # Should show LazyFrame
```

---

## Resources

- **Textual docs**: https://textual.textualize.io
- **Narwhals docs**: https://narwhals-dev.github.io/narwhals
- **DuckDB docs**: https://duckdb.org/docs
- **Typer docs**: https://typer.tiangolo.com

---

## Next Steps

1. **Explore codebase**: Read `src/kittiwake/app.py` to understand app structure
2. **Run tests**: `uv run pytest` to ensure everything works
3. **Pick a task**: See `specs/001-tui-data-explorer/tasks.md` (generated by `/speckit.tasks`)
4. **Submit PR**: Follow contribution guidelines in CONTRIBUTING.md

---

**Questions?** Check plan.md, data-model.md, and research.md in `specs/001-tui-data-explorer/`
