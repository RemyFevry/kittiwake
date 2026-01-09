# Research R7: Operation Execution Sequencing

**Feature**: 001-tui-data-explorer  
**Date**: 2026-01-09  
**Research Question**: How to execute queued operations one-by-one with error handling in a TUI application?

## Context

The TUI Data Explorer supports two execution modes:
- **Lazy mode (default)**: Operations queue up without executing until user triggers execution
- **Eager mode**: Operations execute immediately when applied

Users need to:
- Press **Ctrl+E** to execute the next queued operation
- Press **Ctrl+Shift+E** to execute all queued operations at once
- See clear visual feedback during execution (queued → executing → executed/failed)
- Handle errors gracefully (stop on failure, preserve remaining queued operations)

## Investigation Areas

### 1. Iterator Pattern for Stepping Through Operations

**Current State**: 
- `Dataset.operation_history` stores all operations (currently no distinction between queued/executed)
- Operations are applied immediately via `Dataset.apply_operation()` in main_screen.py:225, 293

**Required Changes**:
- Split `operation_history` into `queued_operations` and `executed_operations`
- Track execution state for each operation
- Maintain operation order across both lists

**Pattern**: Iterator with State Management

```python
class OperationQueue:
    """Manages queued operations with execution state tracking."""
    
    def __init__(self):
        self.queued: list[Operation] = []
        self.executed: list[Operation] = []
        self.current_index: int = 0  # Points to next operation to execute
    
    def enqueue(self, operation: Operation) -> None:
        """Add operation to queue."""
        self.queued.append(operation)
    
    def has_next(self) -> bool:
        """Check if there are more queued operations."""
        return self.current_index < len(self.queued)
    
    def peek_next(self) -> Operation | None:
        """View next operation without executing."""
        if self.has_next():
            return self.queued[self.current_index]
        return None
    
    def execute_next(self) -> Operation | None:
        """Get next operation for execution and advance pointer."""
        if self.has_next():
            operation = self.queued[self.current_index]
            self.current_index += 1
            return operation
        return None
    
    def mark_executed(self, operation: Operation) -> None:
        """Move operation from queued to executed."""
        if operation in self.queued:
            self.queued.remove(operation)
            self.executed.append(operation)
            # Reset index if we removed an operation before current position
            self.current_index = max(0, self.current_index - 1)
    
    def mark_failed(self, operation: Operation) -> None:
        """Mark operation as failed (keep in queued for user to fix/remove)."""
        # Don't move to executed, keep in queued with failed state
        operation.state = "failed"  # Requires adding state attribute to Operation
    
    def clear_queued(self) -> None:
        """Remove all queued operations."""
        self.queued.clear()
        self.current_index = 0
```

### 2. State Management (Which Operation is "Next"?)

**Approach**: Three-state operation model with explicit execution tracking

**Operation States**:
- `queued` - Operation created but not yet executed
- `executing` - Operation currently being applied (for UI feedback)
- `executed` - Operation successfully completed
- `failed` - Operation attempted but failed (remains in queue for user action)

**State Storage**:

Option A: Add `state` field to Operation entity
```python
@dataclass
class Operation:
    code: str
    display: str
    operation_type: str
    params: dict[str, Any]
    id: UUID = None
    state: str = "queued"  # NEW: queued | executing | executed | failed
    error_message: str | None = None  # NEW: Store error for failed operations
```

Option B: Separate lists in Dataset (cleaner separation)
```python
@dataclass
class Dataset:
    # ... existing fields ...
    execution_mode: str = "lazy"  # "lazy" | "eager"
    queued_operations: list[Operation] = field(default_factory=list)
    executed_operations: list[Operation] = field(default_factory=list)
```

**Recommendation**: Option B - Use separate lists in Dataset entity
- Clearer separation of concerns
- Easier to query "all queued" vs "all executed"
- Matches the spec's data model (data-model.md:299)
- Aligns with right sidebar visual grouping

### 3. Error Recovery (Stop on Failure, Mark Failed, Preserve Queued)

**Error Handling Strategy**:

```python
class OperationExecutionError(Exception):
    """Operation execution failed."""
    def __init__(self, operation: Operation, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Operation '{operation.display}' failed: {original_error}")
```

**Execution Flow with Error Handling**:

```python
def execute_next_operation(self, dataset: Dataset) -> tuple[bool, str | None]:
    """Execute next queued operation.
    
    Returns:
        (success: bool, error_message: str | None)
    """
    if not dataset.queued_operations:
        return False, "No queued operations"
    
    operation = dataset.queued_operations[0]  # Peek first
    
    try:
        # Update UI state to "executing"
        self.notify(f"Executing: {operation.display}...")
        
        # Apply operation to current frame
        current_frame = dataset.current_frame or dataset.original_frame
        if current_frame is None:
            raise OperationError("No dataset loaded")
        
        result_frame = operation.apply(current_frame)
        
        # Success: Move from queued to executed
        dataset.queued_operations.pop(0)
        dataset.executed_operations.append(operation)
        dataset.current_frame = result_frame
        
        return True, None
        
    except OperationError as e:
        # Execution failed: Keep in queued, mark as failed
        operation.state = "failed"
        operation.error_message = str(e)
        
        # Stop execution chain (don't proceed to next operation)
        return False, str(e)
        
    except Exception as e:
        # Unexpected error
        operation.state = "failed"
        operation.error_message = f"Unexpected error: {e}"
        return False, operation.error_message
```

**Execute All with Stop-on-Error**:

```python
def execute_all_operations(self, dataset: Dataset) -> tuple[int, int, str | None]:
    """Execute all queued operations until completion or first error.
    
    Returns:
        (executed_count: int, remaining_count: int, error_message: str | None)
    """
    executed_count = 0
    
    while dataset.queued_operations:
        success, error = self.execute_next_operation(dataset)
        
        if success:
            executed_count += 1
        else:
            # Stop on first error
            remaining_count = len(dataset.queued_operations)
            return executed_count, remaining_count, error
    
    return executed_count, 0, None
```

### 4. Progress Feedback During Sequential Execution

**Integration with Textual's Worker System**:

The app already uses `run_worker()` for async operations (app.py:227). Apply same pattern for execution:

```python
async def execute_operations_async(
    self, 
    dataset: Dataset, 
    mode: str = "next"  # "next" | "all"
) -> None:
    """Execute operations asynchronously with progress feedback.
    
    Args:
        dataset: Dataset with queued operations
        mode: "next" for single operation, "all" for all queued
    """
    from time import time
    
    start_time = time()
    
    if mode == "next":
        # Execute single operation
        success, error = self.execution_manager.execute_next_operation(dataset)
        
        if success:
            operation = dataset.executed_operations[-1]
            self.notify(f"✓ Executed: {operation.display}", severity="success")
        else:
            failed_op = dataset.queued_operations[0]
            self.notify_error(
                f"Operation failed: {error}",
                title=f"Failed: {failed_op.display}"
            )
    
    elif mode == "all":
        # Execute all with progress updates
        total_queued = len(dataset.queued_operations)
        
        if total_queued == 0:
            self.notify("No queued operations to execute", severity="information")
            return
        
        # Show initial progress
        self.notify(f"Executing {total_queued} operations...", timeout=1)
        
        executed_count, remaining_count, error = (
            self.execution_manager.execute_all_operations(dataset)
        )
        
        elapsed = time() - start_time
        
        if error:
            # Partial execution with error
            self.notify_error(
                f"Executed {executed_count}/{total_queued} operations. "
                f"{remaining_count} remaining. Error: {error}",
                title="Execution Stopped"
            )
        else:
            # All operations succeeded
            if elapsed > 0.5:
                self.notify(
                    f"✓ Executed all {executed_count} operations ({elapsed:.1f}s)",
                    severity="success",
                    timeout=3
                )
            else:
                self.notify(
                    f"✓ Executed all {executed_count} operations",
                    severity="success"
                )
    
    # Refresh UI
    self._refresh_dataset_view(dataset)
    self._refresh_operations_sidebar(dataset)
```

**Keyboard Binding Integration**:

In MainScreen, add action handlers:

```python
BINDINGS = [
    # ... existing bindings ...
    Binding("ctrl+e", "execute_next", "Execute Next", priority=True),
    Binding("ctrl+shift+e", "execute_all", "Execute All", priority=True),
]

def action_execute_next(self) -> None:
    """Execute next queued operation (Ctrl+E)."""
    dataset = self.session.get_active_dataset()
    if not dataset:
        self.notify("No active dataset", severity="warning")
        return
    
    if dataset.execution_mode != "lazy":
        self.notify("No queued operations (eager mode active)", severity="information")
        return
    
    if not dataset.queued_operations:
        self.notify("No queued operations", severity="information")
        return
    
    # Run in worker to avoid blocking UI
    self.kittiwake_app.run_worker(
        self.kittiwake_app.execute_operations_async(dataset, mode="next"),
        exclusive=False
    )

def action_execute_all(self) -> None:
    """Execute all queued operations (Ctrl+Shift+E)."""
    dataset = self.session.get_active_dataset()
    if not dataset:
        self.notify("No active dataset", severity="warning")
        return
    
    if dataset.execution_mode != "lazy":
        self.notify("No queued operations (eager mode active)", severity="information")
        return
    
    if not dataset.queued_operations:
        self.notify("No queued operations", severity="information")
        return
    
    # Run in worker to avoid blocking UI
    self.kittiwake_app.run_worker(
        self.kittiwake_app.execute_operations_async(dataset, mode="all"),
        exclusive=False
    )
```

**Visual Feedback in Operations Sidebar**:

Update operations_sidebar.py to show execution state:

```python
def refresh_operations(self, dataset: Dataset) -> None:
    """Update operations list with queued and executed operations.
    
    Args:
        dataset: Dataset with queued_operations and executed_operations
    """
    operations_list = self.query_one("#operations_list", ListView)
    operations_list.clear()
    
    # Show executed operations first (green checkmark)
    for idx, op in enumerate(dataset.executed_operations):
        display_text = f"[green]✓[/green] {idx + 1}. {op.display}"
        operations_list.append(
            ListItem(Static(display_text, markup=True), id=f"op_{op.id}")
        )
    
    # Show queued operations (yellow pause icon)
    executed_count = len(dataset.executed_operations)
    for idx, op in enumerate(dataset.queued_operations):
        state_icon = "⏸" if not hasattr(op, 'state') or op.state == "queued" else "✗"
        color = "yellow" if state_icon == "⏸" else "red"
        display_text = f"[{color}]{state_icon}[/{color}] {executed_count + idx + 1}. {op.display}"
        
        # Add error indicator for failed operations
        if hasattr(op, 'state') and op.state == "failed":
            display_text += f" [red](Failed)[/red]"
        
        operations_list.append(
            ListItem(Static(display_text, markup=True), id=f"op_{op.id}")
        )
    
    # Update status
    status = self.query_one("#operations_status", Static)
    total = executed_count + len(dataset.queued_operations)
    if total == 0:
        status.update("No operations")
    else:
        status.update(
            f"{executed_count} executed, {len(dataset.queued_operations)} queued"
        )
```

## ExecutionManager Service Class Design

### Class Structure and Methods

```python
"""Service for managing operation execution sequencing."""

from dataclasses import dataclass
from typing import Protocol

import narwhals as nw

from ..models.dataset import Dataset
from ..models.operations import Operation, OperationError


class ExecutionProgressCallback(Protocol):
    """Protocol for progress callbacks during execution."""
    
    def __call__(
        self, 
        current: int, 
        total: int, 
        operation: Operation | None = None
    ) -> None:
        """Called during execution progress.
        
        Args:
            current: Number of operations executed so far
            total: Total operations to execute
            operation: Currently executing operation (None if complete)
        """
        ...


@dataclass
class ExecutionResult:
    """Result of operation execution."""
    success: bool
    operation: Operation
    error_message: str | None = None
    execution_time_ms: float = 0.0


class ExecutionManager:
    """Manages sequential execution of queued operations with error handling.
    
    Responsibilities:
    - Execute operations one-by-one or all at once
    - Track execution state (queued → executing → executed/failed)
    - Handle errors and stop execution on failure
    - Provide progress feedback during execution
    
    Usage:
        manager = ExecutionManager()
        
        # Execute next operation
        result = await manager.execute_next(dataset)
        if not result.success:
            print(f"Failed: {result.error_message}")
        
        # Execute all operations
        results = await manager.execute_all(
            dataset, 
            progress_callback=lambda cur, tot, op: print(f"{cur}/{tot}")
        )
    """
    
    def __init__(self):
        """Initialize execution manager."""
        self._executing_operation: Operation | None = None
    
    async def execute_next(
        self, 
        dataset: Dataset
    ) -> ExecutionResult:
        """Execute next queued operation.
        
        Args:
            dataset: Dataset with queued operations
            
        Returns:
            ExecutionResult with success status and optional error
            
        Raises:
            ValueError: If no queued operations available
        """
        import time
        
        if not dataset.queued_operations:
            raise ValueError("No queued operations to execute")
        
        operation = dataset.queued_operations[0]
        self._executing_operation = operation
        
        start_time = time.perf_counter()
        
        try:
            # Get current frame state
            current_frame = dataset.current_frame or dataset.original_frame
            if current_frame is None:
                raise OperationError("No dataset frame available")
            
            # Apply operation
            result_frame = operation.apply(current_frame)
            
            # Update dataset state
            dataset.queued_operations.pop(0)
            dataset.executed_operations.append(operation)
            dataset.current_frame = result_frame
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            self._executing_operation = None
            
            return ExecutionResult(
                success=True,
                operation=operation,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # Mark operation as failed (keep in queue)
            if hasattr(operation, '__dict__'):
                operation.state = "failed"
                operation.error_message = str(e)
            
            self._executing_operation = None
            
            return ExecutionResult(
                success=False,
                operation=operation,
                error_message=str(e),
                execution_time_ms=execution_time
            )
    
    async def execute_all(
        self, 
        dataset: Dataset,
        progress_callback: ExecutionProgressCallback | None = None
    ) -> list[ExecutionResult]:
        """Execute all queued operations sequentially.
        
        Stops on first error, leaving remaining operations queued.
        
        Args:
            dataset: Dataset with queued operations
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ExecutionResult for each executed operation
        """
        results: list[ExecutionResult] = []
        total_operations = len(dataset.queued_operations)
        
        if total_operations == 0:
            return results
        
        while dataset.queued_operations:
            # Execute next operation
            result = await self.execute_next(dataset)
            results.append(result)
            
            # Call progress callback
            if progress_callback:
                progress_callback(
                    current=len(results),
                    total=total_operations,
                    operation=result.operation
                )
            
            # Stop on first error
            if not result.success:
                break
        
        return results
    
    def handle_error(
        self, 
        operation: Operation, 
        error: Exception,
        dataset: Dataset
    ) -> str:
        """Handle operation execution error.
        
        Args:
            operation: Failed operation
            error: Exception that occurred
            dataset: Dataset being operated on
            
        Returns:
            User-friendly error message
        """
        # Store error details on operation
        if hasattr(operation, '__dict__'):
            operation.state = "failed"
            operation.error_message = str(error)
        
        # Generate user-friendly message
        if isinstance(error, OperationError):
            return f"Operation '{operation.display}' failed: {error}"
        elif "column" in str(error).lower():
            return (
                f"Column error in '{operation.display}': {error}. "
                "The column may have been removed by a previous operation."
            )
        else:
            return f"Unexpected error in '{operation.display}': {error}"
    
    def get_execution_summary(
        self, 
        results: list[ExecutionResult]
    ) -> dict[str, int | float]:
        """Generate summary statistics from execution results.
        
        Args:
            results: List of execution results
            
        Returns:
            Dictionary with summary stats:
                - total: Total operations attempted
                - successful: Number of successful executions
                - failed: Number of failed executions
                - total_time_ms: Total execution time in milliseconds
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        total_time = sum(r.execution_time_ms for r in results)
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "total_time_ms": total_time
        }
```

### Integration with Textual UI for Progress Feedback

**App-Level Integration** (in app.py):

```python
class KittiwakeApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_manager = ExecutionManager()
    
    async def execute_operations_async(
        self, 
        dataset: Dataset, 
        mode: str = "next"
    ) -> None:
        """Execute operations with UI progress feedback.
        
        Args:
            dataset: Dataset with queued operations
            mode: "next" or "all"
        """
        if mode == "next":
            result = await self.execution_manager.execute_next(dataset)
            
            if result.success:
                self.notify(
                    f"✓ Executed: {result.operation.display}",
                    severity="success"
                )
            else:
                self.notify_error(
                    result.error_message,
                    title=f"Failed: {result.operation.display}"
                )
        
        elif mode == "all":
            total = len(dataset.queued_operations)
            
            def progress_callback(current: int, total: int, operation: Operation | None):
                """Update progress in UI."""
                if operation:
                    self.notify(
                        f"Executing {current}/{total}: {operation.display}",
                        timeout=1
                    )
            
            results = await self.execution_manager.execute_all(
                dataset, 
                progress_callback=progress_callback
            )
            
            summary = self.execution_manager.get_execution_summary(results)
            
            if summary["failed"] == 0:
                self.notify(
                    f"✓ Executed all {summary['successful']} operations "
                    f"({summary['total_time_ms']:.0f}ms)",
                    severity="success",
                    timeout=3
                )
            else:
                failed_op = next(r for r in results if not r.success)
                self.notify_error(
                    f"Executed {summary['successful']}/{summary['total']} operations. "
                    f"Stopped at: {failed_op.error_message}",
                    title="Execution Stopped"
                )
        
        # Refresh UI
        main_screen = self.query_one(MainScreen)
        main_screen._refresh_dataset_view(dataset)
        main_screen._refresh_operations_sidebar(dataset)
```

## Summary

### Recommended Implementation Approach

1. **State Management**: Use separate `queued_operations` and `executed_operations` lists in Dataset
2. **Execution Flow**: Iterator pattern with explicit state tracking (queued → executing → executed/failed)
3. **Error Handling**: Stop-on-error with operation marked as failed, remaining operations preserved
4. **Progress Feedback**: Textual worker system with async execution and progress callbacks
5. **Service Design**: ExecutionManager service class with clean separation of concerns

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Separate queued/executed lists | Clearer than single list with state field; matches spec |
| Stop-on-error strategy | Safer for users to fix issues incrementally; prevents cascade failures |
| Async execution with workers | Non-blocking UI; consistent with existing data loading pattern |
| Rich markup for visual state | Icons + colors provide redundant signals (accessibility) |
| ExecutionResult return type | Clean, testable interface with explicit success/error handling |

### Files to Modify

1. **src/kittiwake/models/dataset.py**
   - Add `execution_mode`, `queued_operations`, `executed_operations` fields
   - Remove immediate execution from `apply_operation()`
   
2. **src/kittiwake/services/execution_manager.py** (NEW)
   - Implement ExecutionManager class
   
3. **src/kittiwake/app.py**
   - Add `execution_manager` instance
   - Add `execute_operations_async()` method
   
4. **src/kittiwake/screens/main_screen.py**
   - Add `action_execute_next()` and `action_execute_all()` handlers
   - Update operation creation to queue instead of execute immediately (in lazy mode)
   
5. **src/kittiwake/widgets/sidebars/operations_sidebar.py**
   - Update `refresh_operations()` to show queued/executed with icons and colors
   - Update status text to show "X executed, Y queued"

### Testing Strategy

```python
# tests/unit/test_execution_manager.py

async def test_execute_next_success():
    """Test successful single operation execution."""
    # Setup dataset with queued operation
    # Execute next
    # Assert: operation moved from queued to executed
    # Assert: result.success is True

async def test_execute_next_failure():
    """Test failed operation execution."""
    # Setup dataset with invalid operation
    # Execute next
    # Assert: operation remains in queued with failed state
    # Assert: result.success is False
    # Assert: error_message is not None

async def test_execute_all_stop_on_error():
    """Test execute all stops on first error."""
    # Setup dataset with 3 operations, 2nd fails
    # Execute all
    # Assert: 1 operation executed, 2 remain queued
    # Assert: results contains 2 items (1 success, 1 failure)

async def test_progress_callback():
    """Test progress callback is called during execution."""
    # Setup progress tracker
    # Execute all with callback
    # Assert: callback called N times with correct current/total
```

## Conclusion

The ExecutionManager service class provides a clean, testable abstraction for operation execution sequencing with:
- Clear state management using separate queued/executed lists
- Stop-on-error behavior with preserved queue state
- Async execution with progress feedback via Textual workers
- Rich visual feedback using icons and colors in the operations sidebar
- Consistent error handling with user-friendly messages

This design integrates seamlessly with the existing Textual UI patterns (app.py:227 worker usage) and maintains the separation of concerns between models (Dataset), services (ExecutionManager), and UI (MainScreen, OperationsSidebar).
