# Research Task R4: DuckDB Async Operations in Textual

**Context**: Building a Textual TUI that needs to perform DuckDB CRUD operations without blocking the UI thread.

**Question**: How to perform DuckDB operations without blocking Textual UI thread?

## Summary

DuckDB operations can be performed asynchronously in Textual using the `run_worker()` method with thread workers. Key findings:

1. **DuckDB is NOT async-aware** - it provides a synchronous API only
2. **Textual's `run_worker()` with `thread=True`** is the recommended pattern
3. **Connection-per-thread strategy** is required for thread safety
4. **Use `call_from_thread()` to update UI** from worker threads

## 1. Textual Worker Pattern for DuckDB Operations

### Basic Pattern with `@work` Decorator

```python
from textual import work
from textual.app import App
from textual.worker import Worker, get_current_worker
import duckdb

class MyApp(App):
    
    @work(exclusive=True, thread=True)
    def save_analysis_worker(self, data: dict) -> int:
        """Save analysis to DuckDB in background thread.
        
        Args:
            data: Analysis data to save
            
        Returns:
            ID of saved analysis
        """
        worker = get_current_worker()
        
        # Create connection in THIS thread
        conn = duckdb.connect(str(self.db_path))
        
        try:
            # Check if cancelled before starting work
            if worker.is_cancelled:
                return None
                
            result = conn.execute(
                """
                INSERT INTO saved_analyses (name, description, operations)
                VALUES (?, ?, ?)
                RETURNING id
                """,
                [data["name"], data["description"], json.dumps(data["operations"])]
            ).fetchone()
            
            analysis_id = result[0] if result else None
            
            # Update UI from main thread
            if not worker.is_cancelled and analysis_id:
                self.call_from_thread(
                    self.notify, 
                    f"Analysis '{data['name']}' saved successfully"
                )
            
            return analysis_id
            
        finally:
            # Always close connection
            conn.close()
    
    def on_button_save(self) -> None:
        """Handle save button click."""
        data = self.collect_analysis_data()
        
        # Start worker - returns immediately
        worker = self.save_analysis_worker(data)
        
        # Optional: handle completion
        worker.wait()  # Only if you need to block
```

### Alternative: Using `run_worker()` Directly

```python
import asyncio
from functools import partial

class MyApp(App):
    
    def do_duckdb_query(self, query: str, params: list) -> list:
        """Execute DuckDB query in worker thread.
        
        This is a sync function that will be run in a thread.
        """
        conn = duckdb.connect(str(self.db_path))
        try:
            result = conn.execute(query, params).fetchall()
            return result
        finally:
            conn.close()
    
    async def load_analyses_async(self) -> None:
        """Load analyses using run_worker."""
        # Create a thread worker for the DB operation
        worker = self.run_worker(
            asyncio.to_thread(
                self.do_duckdb_query,
                "SELECT * FROM saved_analyses ORDER BY created_at DESC",
                []
            ),
            thread=True,
            exclusive=False
        )
        
        # Wait for result (this is async, so won't block UI)
        results = await worker.wait()
        
        # Update UI with results
        self.update_analysis_list(results)
```

## 2. DuckDB Connection Management (Thread-Safe)

### Connection-Per-Thread Strategy (Recommended)

```python
from pathlib import Path
from threading import Lock
import duckdb

class DuckDBManager:
    """Thread-safe DuckDB manager using connection-per-thread pattern."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._write_lock = Lock()  # Only for write operations
        
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get a NEW connection for this thread.
        
        IMPORTANT: Caller must close the connection when done.
        Each thread gets its own connection.
        """
        conn = duckdb.connect(str(self.db_path))
        # Optional: Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def execute_read(self, query: str, params: list = None) -> list:
        """Execute read-only query (thread-safe for concurrent reads)."""
        conn = self.get_connection()
        try:
            result = conn.execute(query, params or []).fetchall()
            return result
        finally:
            conn.close()
    
    def execute_write(self, query: str, params: list = None) -> Any:
        """Execute write query (serialized with lock)."""
        with self._write_lock:
            conn = self.get_connection()
            try:
                result = conn.execute(query, params or []).fetchone()
                return result
            finally:
                conn.close()
```

### What NOT to Do

```python
# ❌ BAD: Sharing connection across threads
class BadExample:
    def __init__(self):
        self.conn = duckdb.connect("data.db")  # DON'T DO THIS
    
    @work(thread=True)
    def bad_query(self):
        # This uses shared connection - NOT THREAD-SAFE
        return self.conn.execute("SELECT * FROM table").fetchall()


# ❌ BAD: Using cursors (they share the same connection)
class AlsoBad:
    @work(thread=True)
    def bad_cursor_use(self):
        conn = duckdb.connect("data.db")
        cursor1 = conn.cursor()  # Not a new connection!
        cursor2 = conn.cursor()  # Still the same connection!
        # These can't run concurrently
```

### Key Rules

1. **One connection per thread** - Create new connection in each worker
2. **Always close connections** - Use try/finally blocks
3. **Reads can be concurrent** - Multiple threads can read simultaneously
4. **Writes must be serialized** - Use locks for write operations
5. **Don't share connections** - Each thread creates its own

## 3. Error Handling Pattern for Database Failures

```python
from textual import work
from textual.worker import Worker, WorkerFailed, get_current_worker
import duckdb

class MyApp(App):
    
    @work(thread=True, exclusive=False, exit_on_error=False)
    def load_analysis_worker(self, analysis_id: int) -> dict | None:
        """Load analysis with comprehensive error handling."""
        worker = get_current_worker()
        conn = None
        
        try:
            # Check cancellation before expensive operations
            if worker.is_cancelled:
                return None
            
            # Create connection
            conn = duckdb.connect(str(self.db_path))
            
            # Execute query
            result = conn.execute(
                "SELECT * FROM saved_analyses WHERE id = ?",
                [analysis_id]
            ).fetchone()
            
            if result is None:
                # Not found - notify user
                if not worker.is_cancelled:
                    self.call_from_thread(
                        self.notify,
                        f"Analysis {analysis_id} not found",
                        severity="warning"
                    )
                return None
            
            # Convert to dict
            analysis = self._row_to_dict(result)
            
            # Success notification
            if not worker.is_cancelled:
                self.call_from_thread(
                    self.notify,
                    f"Loaded analysis: {analysis['name']}"
                )
            
            return analysis
            
        except duckdb.Error as e:
            # Database-specific errors
            error_msg = f"Database error: {e}"
            if not worker.is_cancelled:
                self.call_from_thread(
                    self.notify_error,
                    error_msg,
                    title="Database Error"
                )
            self.log.error(error_msg)
            return None
            
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error loading analysis: {type(e).__name__}: {e}"
            if not worker.is_cancelled:
                self.call_from_thread(
                    self.notify_error,
                    error_msg,
                    title="Error"
                )
            self.log.exception("Unexpected error in load_analysis_worker")
            return None
            
        finally:
            # Always close connection
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:
                    self.log.error(f"Error closing connection: {e}")
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes globally."""
        if event.state == WorkerState.ERROR:
            self.log.error(f"Worker failed: {event.worker.error}")
            self.notify_error(
                f"Background task failed: {event.worker.error}",
                title="Worker Error"
            )
```

### Error Handling Best Practices

1. **Set `exit_on_error=False`** - Prevents app crash on DB errors
2. **Use try/except/finally** - Always close connections
3. **Check `worker.is_cancelled`** - Before expensive operations and UI updates
4. **Use `call_from_thread()`** - For all UI notifications from threads
5. **Log exceptions** - Use `self.log.exception()` for debugging
6. **Handle specific exceptions** - `duckdb.Error` separately from general errors

## 4. Progress Feedback Approach for Slow Queries

### Using Notifications

```python
import time
from textual import work

class MyApp(App):
    
    @work(thread=True)
    def slow_query_with_progress(self, query: str) -> list:
        """Execute slow query with progress feedback."""
        worker = get_current_worker()
        start_time = time.time()
        
        # Show start notification
        self.call_from_thread(
            self.notify,
            "Running query...",
            timeout=1
        )
        
        conn = duckdb.connect(str(self.db_path))
        try:
            if worker.is_cancelled:
                return []
            
            # Execute query
            result = conn.execute(query).fetchall()
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            
            # Show completion with timing if slow (>500ms)
            if not worker.is_cancelled:
                if elapsed > 0.5:
                    self.call_from_thread(
                        self.notify,
                        f"Query completed ({elapsed:.1f}s)",
                        timeout=3
                    )
                else:
                    self.call_from_thread(
                        self.notify,
                        "Query completed",
                        timeout=2
                    )
            
            return result
            
        finally:
            conn.close()
```

### Using Loading Indicators

```python
from textual.widgets import LoadingIndicator

class MyApp(App):
    
    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="query-loading")
    
    async def run_query_with_indicator(self, query: str) -> None:
        """Run query with loading indicator."""
        loading = self.query_one("#query-loading", LoadingIndicator)
        
        # Show loading indicator
        loading.display = True
        
        try:
            # Run query in worker
            worker = self.run_worker(
                asyncio.to_thread(self._execute_query, query),
                thread=True
            )
            
            # Wait for result
            result = await worker.wait()
            
            # Update UI with result
            self.update_results(result)
            
        finally:
            # Hide loading indicator
            loading.display = False
    
    def _execute_query(self, query: str) -> list:
        """Execute query in thread."""
        conn = duckdb.connect(str(self.db_path))
        try:
            return conn.execute(query).fetchall()
        finally:
            conn.close()
```

### Progress Bar for Multi-Step Operations

```python
from textual.widgets import ProgressBar

class MyApp(App):
    
    @work(thread=True)
    def multi_step_operation(self, items: list) -> None:
        """Process items with progress updates."""
        worker = get_current_worker()
        total = len(items)
        
        conn = duckdb.connect(str(self.db_path))
        try:
            for i, item in enumerate(items):
                if worker.is_cancelled:
                    break
                
                # Process item
                conn.execute(
                    "INSERT INTO processed_items VALUES (?)",
                    [item]
                )
                
                # Update progress bar
                progress = (i + 1) / total
                self.call_from_thread(
                    self._update_progress,
                    progress,
                    f"Processing {i + 1}/{total}"
                )
        finally:
            conn.close()
    
    def _update_progress(self, value: float, message: str) -> None:
        """Update progress bar (runs in main thread)."""
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(progress=value)
        self.notify(message, timeout=0.5)
```

## Comparison: Async API vs Thread Workers

| Aspect | Async (httpx) | Threads (DuckDB) |
|--------|---------------|------------------|
| **API Type** | `async def` with `await` | Sync functions |
| **Textual Pattern** | `@work` or `run_worker` | `@work(thread=True)` |
| **Function Type** | `async def` | Regular `def` |
| **Cancellation** | Automatic | Manual with `worker.is_cancelled` |
| **UI Updates** | Direct calls | `call_from_thread()` required |
| **Connection Sharing** | Safe (async-native) | Unsafe (need per-thread) |

## Complete Working Example

```python
"""Complete example of DuckDB async operations in Textual."""

import json
import time
from pathlib import Path
from threading import Lock
from typing import Any

import duckdb
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Button, DataTable, Static
from textual.worker import Worker, get_current_worker


class DuckDBAsyncApp(App):
    """Example app showing async DuckDB operations."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #container {
        width: 80;
        height: 30;
        border: solid blue;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.db_path = Path.home() / ".example" / "data.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = Lock()
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema (runs once at startup)."""
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        finally:
            conn.close()
    
    def compose(self) -> ComposeResult:
        """Compose UI."""
        with Vertical(id="container"):
            yield Button("Load Items", id="load-btn")
            yield Button("Add Item", id="add-btn")
            yield DataTable(id="results")
            yield Static("", id="status")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "load-btn":
            self.load_items()
        elif event.button.id == "add-btn":
            self.add_item(f"Item {time.time()}")
    
    @work(thread=True, exclusive=False)
    def load_items(self) -> list[tuple]:
        """Load items from database."""
        worker = get_current_worker()
        start_time = time.time()
        
        # Show loading notification
        self.call_from_thread(self.notify, "Loading items...")
        
        # Create connection for THIS thread
        conn = duckdb.connect(str(self.db_path))
        
        try:
            if worker.is_cancelled:
                return []
            
            # Execute query
            result = conn.execute(
                "SELECT id, name, created_at FROM items ORDER BY created_at DESC"
            ).fetchall()
            
            # Show completion with timing
            elapsed = time.time() - start_time
            if not worker.is_cancelled:
                if elapsed > 0.5:
                    self.call_from_thread(
                        self.notify,
                        f"Loaded {len(result)} items ({elapsed:.1f}s)"
                    )
                
                # Update UI
                self.call_from_thread(self._update_table, result)
            
            return result
            
        except duckdb.Error as e:
            if not worker.is_cancelled:
                self.call_from_thread(
                    self.notify_error,
                    f"Database error: {e}",
                    title="Error"
                )
            return []
            
        finally:
            conn.close()
    
    @work(thread=True, exclusive=False)
    def add_item(self, name: str) -> int | None:
        """Add item to database."""
        worker = get_current_worker()
        
        # Use lock for write operations
        with self._write_lock:
            conn = duckdb.connect(str(self.db_path))
            
            try:
                if worker.is_cancelled:
                    return None
                
                result = conn.execute(
                    "INSERT INTO items (name) VALUES (?) RETURNING id",
                    [name]
                ).fetchone()
                
                item_id = result[0] if result else None
                
                if not worker.is_cancelled and item_id:
                    self.call_from_thread(
                        self.notify,
                        f"Added: {name}"
                    )
                    # Reload items
                    self.call_from_thread(self.load_items)
                
                return item_id
                
            except duckdb.Error as e:
                if not worker.is_cancelled:
                    self.call_from_thread(
                        self.notify_error,
                        f"Failed to add item: {e}",
                        title="Error"
                    )
                return None
                
            finally:
                conn.close()
    
    def _update_table(self, data: list[tuple]) -> None:
        """Update table with results (runs in main thread)."""
        table = self.query_one(DataTable)
        table.clear()
        
        if not table.columns:
            table.add_columns("ID", "Name", "Created")
        
        for row in data:
            table.add_row(*[str(cell) for cell in row])
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.ERROR:
            self.log.error(f"Worker failed: {event.worker.error}")


if __name__ == "__main__":
    app = DuckDBAsyncApp()
    app.run()
```

## Key Takeaways

1. ✅ **Use `@work(thread=True)`** - DuckDB requires thread workers, not async
2. ✅ **Connection per thread** - Create new connection in each worker
3. ✅ **Use `call_from_thread()`** - Required for all UI updates from threads
4. ✅ **Lock write operations** - Use `threading.Lock()` for serialization
5. ✅ **Check cancellation** - Use `worker.is_cancelled` before expensive ops
6. ✅ **Always close connections** - Use try/finally blocks
7. ✅ **Handle errors gracefully** - Set `exit_on_error=False` and catch exceptions
8. ✅ **Provide feedback** - Use notifications, loading indicators, or progress bars

## References

- [Textual Workers Documentation](https://textual.textualize.io/guide/workers/)
- [DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview.html)
- [DuckDB Concurrency](https://duckdb.org/docs/stable/connect/concurrency.html)
- Existing pattern in `src/kittiwake/app.py:load_dataset_async()`
- Existing pattern in `src/kittiwake/services/persistence.py:SavedAnalysisRepository`
