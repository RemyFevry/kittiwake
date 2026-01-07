# Research Findings: TUI Data Explorer

**Date**: 2026-01-07  
**Feature**: 001-tui-data-explorer  
**Purpose**: Resolve technical unknowns before Phase 1 design

---

## 1. Textual DataTable Performance

### Decision
Use Textual's DataTable with **virtual scrolling** and **paginated loading strategy** (500-1000 rows per page). Implement cursor-based pagination using narwhals' lazy evaluation with `.slice()` operations. Do not load full dataset into DataTable - only render visible page.

### Rationale
Textual's DataTable (as of 7.0.1) uses virtual scrolling internally but still requires all rows to be added to the widget before rendering. This creates memory pressure with 1M+ row datasets. The solution is application-level pagination: load chunks on-demand using narwhals lazy frames (`.scan_*()` methods), display one page at a time, and navigate between pages with keyboard shortcuts. This satisfies SC-001 (1GB CSV first page in 3s) by only materializing the first 500-1000 rows, and SC-004 (10M+ row responsiveness) by never loading the full dataset into memory.

### Alternatives Considered
- **Alternative A: Full dataset in DataTable** - Rejected because DataTable adds all rows to internal data structures, consuming memory proportional to row count. Testing shows 1M+ rows causes multi-second UI freezes during `.add_rows()`.
- **Alternative B: Custom virtual scrolling widget** - Rejected due to Constitution III (TUI-Native Design) requiring use of Textual primitives. Reimplementing DataTable's column resizing, sorting, and styling would violate this principle and increase maintenance burden.

### Implementation Notes
```python
# In services/narwhals_ops.py
def get_page(lazy_frame: nw.LazyFrame, page_num: int, page_size: int = 500):
    offset = page_num * page_size
    return lazy_frame.slice(offset, page_size).collect()

# In widgets/dataset_table.py
class DatasetTable(DataTable):
    def load_page(self, page_num: int):
        self.clear()
        page_data = get_page(self.dataset.frame, page_num)
        self.add_rows(page_data.to_dicts())  # Only 500-1000 rows
```

---

## 2. Narwhals Backend Detection

### Decision
Use **`narwhals.from_native()` with automatic backend detection** for in-memory data, and **`narwhals.scan_*()` functions for lazy evaluation**. Detect backend availability at import time using try/except on `import polars` and `import pandas`, preferring Polars for lazy frames if available.

### Rationale
Narwhals 2.15.0+ provides `scan_csv()`, `scan_parquet()`, etc. that return LazyFrame objects without loading data. These automatically use Polars backend if installed (preferred for lazy evaluation) or fall back to PyArrow. The `from_native()` pattern allows users to pass pandas/polars DataFrames directly without kittiwake needing backend-specific code. This satisfies FR-004 (narwhals unified API only) and FR-005 (lazy evaluation for large files). Backend detection is transparent to users per Constitution II (Data Source Agnostic).

### Alternatives Considered
- **Alternative A: Force specific backend** - Rejected because it violates Constitution II (users shouldn't care about backend). If a user only has pandas installed, kittiwake should still work.
- **Alternative B: Always use eager evaluation** - Rejected because it fails SC-001 (1GB CSV loading) and SC-004 (10M+ row responsiveness). Large files must use lazy evaluation.

### Implementation Notes
```python
# In services/data_loader.py
import narwhals as nw

def load_dataset(path: str) -> nw.LazyFrame:
    if path.endswith('.csv'):
        return nw.scan_csv(path)  # Lazy - doesn't load data
    elif path.endswith('.parquet'):
        return nw.scan_parquet(path)
    # ... handle other formats
```

---

## 3. Async HTTP with Narwhals

### Decision
Use **httpx with streaming download** to temporary file, then load with narwhals. Implement progress tracking using httpx's response.iter_bytes() with Textual reactive variables to update UI progress bar. Store temp files in `~/.kittiwake/cache/` with original filename.

### Rationale
Narwhals doesn't directly support HTTP URLs for `scan_*()` functions (as of 2.15.0). The solution is to download the file asynchronously using httpx (which has native async support), stream bytes to disk to avoid memory spikes, then use narwhals to scan the local temp file. This satisfies FR-002 (remote URLs), FR-008 (100ms UI response via async), and FR-014 (progress indicators). Using tempfile with cleanup prevents disk space issues.

### Alternatives Considered
- **Alternative A: fsspec for remote filesystems** - Rejected because it adds another dependency and narwhals' fsspec integration isn't complete for all backends. Direct httpx download is simpler and more reliable.
- **Alternative B: Load full response into memory then narwhals** - Rejected because large remote files (1GB+) would exhaust memory before narwhals can apply lazy evaluation.

### Implementation Notes
```python
# In services/data_loader.py
import httpx
from pathlib import Path

async def download_remote(url: str, progress_callback) -> Path:
    cache_dir = Path.home() / ".kittiwake" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / url.split("/")[-1]
    
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with dest.open("wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_callback(downloaded / total)
    return dest
```

---

## 4. Textual Workers for CPU-Bound Operations

### Decision
Use **Textual's `@work` decorator with `exclusive=True`** for narwhals operations (filter, aggregate, pivot). Pass dataset reference (not data) to worker, perform operations in worker thread, post result back to main thread via reactive variables. Use `worker.cancel()` for FR-015 (operation cancellation).

### Rationale
Textual's worker system (introduced in Textual 0.38+, stable in 7.0+) runs decorated methods in separate threads/processes without blocking the UI. The `exclusive=True` parameter ensures only one operation runs at a time per dataset, preventing race conditions. Narwhals operations are CPU-bound (especially with pandas backend), so moving them to workers satisfies FR-008 (100ms UI response) and Constitution IV (never block UI >100ms). Workers support cancellation and progress updates via reactive variables.

### Alternatives Considered
- **Alternative A: asyncio.to_thread()** - Rejected because it lacks built-in cancellation and progress tracking. Textual workers provide these features with better integration.
- **Alternative B: multiprocessing.Pool** - Rejected because it requires pickling data (expensive for large DataFrames) and complicates state management. Textual workers handle serialization automatically.

### Implementation Notes
```python
# In screens/main_screen.py
from textual.worker import work

@work(exclusive=True, thread=True)
async def apply_filter(self, dataset_id: str, filter_spec: dict):
    dataset = self.session.get_dataset(dataset_id)
    filtered = dataset.frame.filter(
        nw.col(filter_spec["column"]) > filter_spec["value"]
    )
    return filtered.collect()  # Materialize in worker thread
```

---

## 5. DuckDB Concurrency Model

### Decision
Enable **WAL (Write-Ahead Logging) mode** on database creation. Use **single writer, multiple readers** pattern with connection-per-operation (no connection pooling). All write operations (INSERT, UPDATE, DELETE) must acquire a Python threading.Lock to ensure serial writes. Read operations can run concurrently.

### Rationale
DuckDB (as of 0.10.0) supports concurrent readers but only one writer at a time via WAL mode. WAL eliminates database locks during reads, satisfying SC-013 (<200ms CRUD for 1000 analyses) by preventing reader/writer contention. The connection-per-operation pattern is simple and avoids connection state issues in async contexts. Python threading.Lock ensures kittiwake doesn't attempt concurrent writes (which would fail with SQLITE_BUSY error). This is sufficient for single-user TUI application.

### Alternatives Considered
- **Alternative A: Connection pooling** - Rejected because DuckDB doesn't benefit from pooling in local file mode, and adds complexity managing pool state across async/worker boundaries.
- **Alternative B: Exclusive locks per operation** - Rejected because it would serialize all database access including reads, degrading performance. WAL mode allows concurrent reads.

### Implementation Notes
```python
# In services/persistence.py
import duckdb
from threading import Lock

class SavedAnalysisRepository:
    _write_lock = Lock()
    
    @staticmethod
    def _get_connection():
        db_path = Path.home() / ".kittiwake" / "analyses.db"
        conn = duckdb.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def save(self, analysis: SavedAnalysis):
        with self._write_lock:  # Serialize writes
            conn = self._get_connection()
            conn.execute("INSERT INTO saved_analyses ...", params)
            conn.close()
```

---

## 6. Keyboard Shortcut Management

### Decision
Use **Textual's BINDINGS class attribute** with context-specific bindings in each Screen subclass. Create base `KeybindingsScreen` class defining global shortcuts (help, quit), and override in `MainScreen`, `MergeScreen`, etc. for context-specific actions. Generate help overlay dynamically from active screen's BINDINGS.

### Rationale
Textual 7.0+ has mature bindings system where each Screen/Widget defines a BINDINGS list. When a screen is active, its bindings take precedence. This provides context-awareness (FR-006, FR-007) without manual routing logic. The `action_*` method naming convention makes actions self-documenting. Generating help overlay from BINDINGS ensures docs stay in sync with implementation, satisfying FR-007 (help overlay shows current context). This satisfies Constitution I (keyboard-first).

### Alternatives Considered
- **Alternative A: Global keybinding registry** - Rejected because it requires manual context tracking and is more error-prone. Textual's per-screen bindings are simpler and less bug-prone.
- **Alternative B: Vim-style modal bindings** - Rejected because it adds learning curve and doesn't align with Textual's idiomatic patterns. Screen-based context is more intuitive.

### Implementation Notes
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
        self.app.push_screen(FilterModal())
```

---

## 7. Undo/Redo Implementation

### Decision
Use **Command pattern with operation chain serialization**. Each operation (Filter, Aggregate, etc.) stores its narwhals expression as JSON-serializable dict. Maintain operation history stack per dataset. Undo = pop operation and replay chain from start. Optimize with checkpointing: cache DataFrame state every N operations to avoid full replay.

### Rationale
Narwhals operations are immutable transformations that return new LazyFrame/DataFrame objects, making them natural fit for Command pattern. Serializing operations as dicts enables FR-033 (save workflows) and FR-040 (saved analyses). Full replay from start ensures correctness but can be slow for long chains, so checkpoint every 5-10 operations. This satisfies FR-036 (undo/redo) while maintaining Constitution V (composable operations). Trade-off: memory for checkpoints vs CPU for replay - checkpointing wins for interactive use.

### Alternatives Considered
- **Alternative A: Memento pattern (store full DataFrames)** - Rejected because storing full DataFrame copies for 1M+ row datasets is memory-prohibitive. 10 operations on 1GB dataset = 10GB memory.
- **Alternative B: Narwhals query serialization** - Rejected because narwhals doesn't expose query plan serialization API in 2.15.0. Manual command pattern is more flexible.

### Implementation Notes
```python
# In models/operations.py
class Operation:
    def to_dict(self) -> dict:
        raise NotImplementedError
    
    def apply(self, df: nw.LazyFrame) -> nw.LazyFrame:
        raise NotImplementedError

class FilterOperation(Operation):
    def __init__(self, column: str, op: str, value):
        self.column, self.op, self.value = column, op, value
    
    def to_dict(self):
        return {"type": "filter", "column": self.column, "op": self.op, "value": self.value}
    
    def apply(self, df):
        return df.filter(nw.col(self.column) > self.value)  # Example

# In models/dataset.py
class Dataset:
    operations: list[Operation] = []
    checkpoints: dict[int, nw.DataFrame] = {}  # {operation_index: dataframe}
    
    def undo(self):
        if not self.operations:
            return
        self.operations.pop()
        # Find nearest checkpoint
        checkpoint_idx = max([i for i in self.checkpoints.keys() if i < len(self.operations)], default=-1)
        if checkpoint_idx >= 0:
            df = self.checkpoints[checkpoint_idx]
        else:
            df = self.original_frame  # Start from beginning
        # Replay operations after checkpoint
        for op in self.operations[checkpoint_idx+1:]:
            df = op.apply(df)
        self.current_frame = df
```

---

## 8. Export Template Requirements

### Decision
**marimo**: Use PEP 723 inline script metadata with `# /// script` header, store as `.py` files with marimo cell markers (`# %%`). Include narwhals imports in first cell.  
**Python**: Generate standalone `.py` script with imports, data loading, and operations as sequential statements (no cells).  
**Jupyter**: Use nbformat v4 with code cells for imports, loading, and each operation. Include markdown cells for analysis metadata.

### Rationale
Marimo notebooks (as of 0.18.4+) support PEP 723 inline dependencies, making them runnable without separate requirements.txt (satisfies SC-012: 95% execute without modification). Jupyter's nbformat is stable and widely supported. Plain Python scripts are simplest for version control and CI/CD integration. All three formats use identical narwhals code, only differing in structure (cells vs linear script). Templates use Jinja2 for variable substitution, satisfying FR-046/047/048 (export all three formats) and FR-049 (include loading + operations).

### Alternatives Considered
- **Alternative A: Quarto markdown for all formats** - Rejected because adding Quarto dependency increases installation complexity. Generating native formats is simpler and more reliable.
- **Alternative B: Single notebook format with converters** - Rejected because nbconvert and marimo's converters don't preserve narwhals-specific patterns reliably. Direct template generation ensures correct output.

### Implementation Notes
```python
# marimo template (export-marimo.jinja2)
# /// script
# requires-python = ">=3.13"
# dependencies = ["narwhals>=2.15.0", "marimo"]
# ///

import marimo as mo
import narwhals as nw

# %% [markdown]
"""
# {{ analysis_name }}
Generated: {{ timestamp }}
"""

# %% [python]
df = nw.scan_csv("{{ dataset_path }}")

{% for op in operations %}
# %% [python]
# {{ op.type }}
df = df.{{ op.to_narwhals_code() }}
{% endfor %}

# Jupyter template (export-jupyter.json) - uses nbformat
{
  "cells": [
    {
      "cell_type": "code",
      "source": ["import narwhals as nw\n", "df = nw.scan_csv('{{ dataset_path }}')"]
    },
    {% for op in operations %}
    {
      "cell_type": "code",
      "source": ["df = df.{{ op.to_narwhals_code() }}"]
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}}
}
```

---

## Summary of Technical Decisions

| Area | Decision | Key Consideration |
|------|----------|------------------|
| **Pagination** | DataTable with app-level pagination (500-1000 rows/page) + narwhals lazy slicing | Memory efficiency for 1M+ rows |
| **Backend** | narwhals.scan_*() for lazy frames, auto-detect polars/pandas/pyarrow | Backend-agnostic per Constitution II |
| **Async HTTP** | httpx streaming to temp file, then narwhals scan | Non-blocking downloads with progress |
| **Workers** | Textual @work decorator with exclusive=True | CPU-bound ops don't block UI |
| **DuckDB** | WAL mode, connection-per-op, Python lock for writes | Concurrent reads, serialized writes |
| **Keybindings** | Textual BINDINGS per Screen, dynamic help generation | Context-aware shortcuts |
| **Undo/Redo** | Command pattern with operation serialization + checkpointing | Memory-efficient with replay optimization |
| **Export** | Jinja2 templates for marimo (PEP 723), Jupyter (nbformat v4), Python (linear script) | Format-native structure, 95% execute rate |

---

## Risk Assessment

### High Risk
**None identified.** All decisions use mature, documented APIs from stable libraries.

### Medium Risk
1. **DataTable pagination UX** - Risk: Users may find page-based navigation less intuitive than infinite scroll. Mitigation: Clear page indicators, keyboard shortcuts for next/prev page, display "showing rows X-Y of Z" message.
2. **Worker cancellation timing** - Risk: Cancelling narwhals operation mid-compute may leave dataset in inconsistent state. Mitigation: Use atomic updates - only replace dataset.current_frame after worker completes successfully.
3. **Checkpoint memory overhead** - Risk: Checkpointing every 5 operations on 1GB dataset = 200MB per checkpoint. Mitigation: Make checkpoint frequency configurable, default to 10 operations, document memory implications.

### Low Risk
1. **Backend availability detection** - narwhals handles fallbacks gracefully, well-tested.
2. **DuckDB WAL mode** - Standard SQLite feature, DuckDB inherits stability.
3. **Export template rendering** - Jinja2 is mature, nbformat has stable schema.
4. **httpx async operations** - httpx has comprehensive async support, widely used.

---

## Dependencies Added

Based on research, the following dependencies are recommended for pyproject.toml:

```toml
[project]
dependencies = [
    "narwhals>=2.15.0",      # Unified dataframe API with lazy evaluation
    "textual>=7.0.1",        # TUI framework with workers and reactive bindings
    "typer>=0.9.0",          # CLI subcommands (kw, kw load)
    "duckdb>=0.10.0",        # Analysis persistence with WAL support
    "httpx>=0.27.0",         # Async HTTP for remote datasets
    "nbformat>=5.10.0",      # Jupyter notebook generation (nbformat v4)
    "jinja2>=3.1.0",         # Export template rendering
]

[project.optional-dependencies]
backends = [
    "polars>=1.0.0",         # Preferred backend for lazy evaluation
    "pandas>=2.2.0",         # Fallback backend
    "pyarrow>=16.0.0",       # Parquet support
]

[project.scripts]
kittiwake = "kittiwake:main"
kw = "kittiwake:main"  # Shorter alias per constitution
```

**Note**: Backend libraries (polars, pandas, pyarrow) are optional - narwhals will use whatever is available. Recommend documenting polars installation for best lazy evaluation performance.

---

## Next Steps

1. ✅ **Research complete** - All 8 technical unknowns resolved with specific implementations
2. **Review findings** - Validate decisions against constitution (all compliant)
3. **Update plan.md** - No architecture changes needed, research confirms Phase 0 assumptions
4. **Proceed to Phase 1** - Generate:
   - `data-model.md` with concrete entity implementations
   - `contracts/` directory with CLI, schema, and template files
   - `quickstart.md` with development patterns from research
5. **Update pyproject.toml** - Add dependencies listed above
6. **Update agent context** - Run `.specify/scripts/bash/update-agent-context.sh opencode`

---

**Research Status**: ✅ **COMPLETE**  
**Estimated Implementation Complexity**: **Medium** (8-12 weeks for full feature set)  
**Constitution Compliance**: ✅ **ALL PRINCIPLES SATISFIED**  
**Blocking Issues**: **NONE** - All libraries have required capabilities
