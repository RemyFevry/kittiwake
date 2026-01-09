"""Dataset entity for managing loaded data and operations."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

import narwhals as nw

from .operations import Operation, OperationError


@dataclass
class Dataset:
    """Represents a loaded dataset."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    source: str = ""
    backend: str = ""
    frame: nw.LazyFrame | None = None
    original_frame: nw.LazyFrame | None = None  # Keep original for reset
    schema: dict[str, str] = field(default_factory=dict)
    row_count: int = 0
    is_active: bool = False
    is_lazy: bool = True
    
    # Lazy/Eager execution mode
    execution_mode: str = "lazy"  # "lazy" | "eager"
    queued_operations: list[Operation] = field(default_factory=list)
    executed_operations: list[Operation] = field(default_factory=list)
    
    # Legacy field for backwards compatibility (deprecated)
    operation_history: list[Operation] = field(default_factory=list)
    
    # Undo/redo stacks
    redo_stack: list[Operation] = field(default_factory=list)
    
    current_frame: nw.LazyFrame | None = None
    checkpoints: dict[int, nw.LazyFrame] = field(default_factory=dict)
    checkpoint_interval: int = 10

    def apply_operation(self, operation: Operation) -> None:
        """Apply operation based on execution mode.
        
        In lazy mode: queue operation without executing
        In eager mode: execute operation immediately
        
        Clears redo stack when new operation is applied.
        """
        # Clear redo stack when new operation is applied
        self.redo_stack.clear()
        
        if self.execution_mode == "lazy":
            # Queue operation for later execution
            operation.state = "queued"
            self.queued_operations.append(operation)
        else:
            # Eager mode: execute immediately
            self._execute_operation(operation)
    
    def _execute_operation(self, operation: Operation) -> None:
        """Execute a single operation and update state."""
        try:
            # Apply operation to current frame
            current = self.current_frame or self.original_frame or self.frame
            if current is None:
                raise OperationError("No dataset loaded")

            result = operation.apply(current)

            # Mark as executed and move to executed list
            operation.state = "executed"
            self.executed_operations.append(operation)
            self.current_frame = result
            
            # Also update legacy operation_history for backwards compatibility
            self.operation_history.append(operation)

            # Create checkpoint if needed
            if len(self.executed_operations) % self.checkpoint_interval == 0:
                self.checkpoints[len(self.executed_operations)] = result

        except OperationError:
            raise
        except Exception as e:
            raise OperationError(f"Operation failed: {e}")
    
    def queue_operation(self, operation: Operation) -> None:
        """Add operation to queue without executing."""
        operation.state = "queued"
        self.queued_operations.append(operation)
    
    def execute_next_queued(self) -> bool:
        """Execute next queued operation.
        
        Returns:
            True if operation executed successfully, False if queue is empty
            
        Clears redo stack when operation is executed.
        """
        if not self.queued_operations:
            return False
        
        # Clear redo stack when executing new operations
        self.redo_stack.clear()
        
        operation = self.queued_operations.pop(0)  # FIFO
        try:
            self._execute_operation(operation)
            return True
        except Exception as e:
            # Mark as failed and re-add to front of queue
            operation.state = "failed"
            operation.error_message = str(e)
            self.queued_operations.insert(0, operation)
            raise
    
    def execute_all_queued(self) -> int:
        """Execute all queued operations.
        
        Stops on first error, preserving remaining operations in queue.
        
        Returns:
            Number of operations executed successfully
        """
        count = 0
        while self.queued_operations:
            try:
                if self.execute_next_queued():
                    count += 1
                else:
                    break
            except Exception:
                # Stop on error, remaining operations stay queued
                break
        return count
    
    def clear_queued(self) -> int:
        """Clear all queued operations.
        
        Returns:
            Number of operations cleared
        """
        count = len(self.queued_operations)
        self.queued_operations.clear()
        return count

    def undo(self) -> bool:
        """Undo last executed operation.
        
        Removes the last operation from executed_operations and adds it to redo_stack.
        Also updates legacy operation_history for backwards compatibility.
        
        Returns:
            True if undo was successful, False if no operations to undo
        """
        # Check both new executed_operations and legacy operation_history
        has_executed = bool(self.executed_operations)
        has_legacy = bool(self.operation_history)
        
        if not has_executed and not has_legacy:
            return False

        # Pop from executed_operations if available
        if has_executed:
            undone_op = self.executed_operations.pop()
            self.redo_stack.append(undone_op)
        
        # Also remove from legacy operation_history for backwards compatibility
        if has_legacy:
            self.operation_history.pop()

        # Restore from checkpoint or replay
        # Use the count from whichever list is being used
        op_count = len(self.executed_operations) if has_executed else len(self.operation_history)
        
        checkpoint_idx = max(
            [i for i in self.checkpoints.keys() if i <= op_count],
            default=0,
        )

        if checkpoint_idx > 0:
            self.current_frame = self.checkpoints[checkpoint_idx]
        else:
            self.current_frame = self.original_frame or self.frame

        # Replay operations after checkpoint
        ops_to_replay = self.executed_operations if has_executed else self.operation_history
        for op in ops_to_replay[checkpoint_idx:]:
            try:
                if self.current_frame is None:
                    return False
                self.current_frame = op.apply(self.current_frame)
            except Exception:
                return False

        return True

    def redo(self) -> bool:
        """Redo previously undone operation.
        
        Takes the last operation from redo_stack and re-executes it.
        
        Returns:
            True if redo was successful, False if no operations to redo
        """
        if not self.redo_stack:
            return False
        
        # Pop from redo stack
        operation = self.redo_stack.pop()
        
        # Re-execute the operation
        try:
            current = self.current_frame or self.original_frame or self.frame
            if current is None:
                # Restore to redo_stack if execution fails
                self.redo_stack.append(operation)
                return False

            result = operation.apply(current)

            # Add back to executed operations
            self.executed_operations.append(operation)
            self.current_frame = result
            
            # Also update legacy operation_history for backwards compatibility
            self.operation_history.append(operation)

            # Create checkpoint if needed
            if len(self.executed_operations) % self.checkpoint_interval == 0:
                self.checkpoints[len(self.executed_operations)] = result

            return True
            
        except Exception:
            # Restore to redo_stack if execution fails
            self.redo_stack.append(operation)
            return False

    def get_page(self, page_num: int, page_size: int = 500) -> nw.DataFrame | None:
        """Get a page of data for display."""
        from ..services.narwhals_ops import NarwhalsOps

        frame = self.current_frame or self.original_frame or self.frame

        if frame is None:
            return None

        return NarwhalsOps.get_page(frame, page_num, page_size)

    def to_dict(self) -> dict[str, Any]:
        """Serialize dataset metadata."""
        return {
            "name": self.name,
            "source": self.source,
            "backend": self.backend,
            "execution_mode": self.execution_mode,
            "queued_operations": [op.to_dict() for op in self.queued_operations],
            "executed_operations": [op.to_dict() for op in self.executed_operations],
            # Legacy field
            "operations": [op.to_dict() for op in self.operation_history],
        }

    def get_filtered_row_count(self) -> int:
        """Get row count after applying operations."""
        if self.current_frame is None:
            return self.row_count
        
        # Collect the filtered frame to get actual row count
        try:
            # For lazy frames, we need to collect to get row count
            collected = self.current_frame.collect()
            return len(collected)
        except Exception:
            # Fallback to original count if something goes wrong
            return self.row_count
