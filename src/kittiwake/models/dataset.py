"""Dataset entity for managing loaded data and operations."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
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
    frame: Optional[nw.LazyFrame] = None
    original_frame: Optional[nw.LazyFrame] = None  # Keep original for reset
    schema: Dict[str, str] = field(default_factory=dict)
    row_count: int = 0
    is_active: bool = False
    is_lazy: bool = True
    operation_history: List[Operation] = field(default_factory=list)
    current_frame: Optional[nw.LazyFrame] = None
    checkpoints: Dict[int, nw.LazyFrame] = field(default_factory=dict)
    checkpoint_interval: int = 10

    def apply_operation(self, operation: Operation) -> None:
        """Apply operation and update history."""
        try:
            # Apply operation to current frame
            current = self.current_frame or self.original_frame or self.frame
            if current is None:
                raise OperationError("No dataset loaded")

            result = operation.apply(current)

            # Add to history
            self.operation_history.append(operation)
            self.current_frame = result

            # Create checkpoint if needed
            if len(self.operation_history) % self.checkpoint_interval == 0:
                self.checkpoints[len(self.operation_history)] = result

        except OperationError:
            raise
        except Exception as e:
            raise OperationError(f"Operation failed: {e}")

    def undo(self) -> bool:
        """Undo last operation."""
        if not self.operation_history:
            return False

        # Remove last operation
        self.operation_history.pop()

        # Restore from checkpoint or replay
        checkpoint_idx = max(
            [i for i in self.checkpoints.keys() if i < len(self.operation_history)],
            default=0,
        )

        if checkpoint_idx > 0:
            self.current_frame = self.checkpoints[checkpoint_idx]
        else:
            self.current_frame = self.original_frame or self.frame

        # Replay operations after checkpoint
        for op in self.operation_history[checkpoint_idx:]:
            try:
                if self.current_frame is None:
                    return False
                self.current_frame = op.apply(self.current_frame)
            except Exception:
                return False

        return True

    def redo(self) -> bool:
        """Redo undone operation."""
        # For now, we don't store undo stack
        return False

    def get_page(self, page_num: int, page_size: int = 500) -> Optional[nw.DataFrame]:
        """Get a page of data for display."""
        from ..services.narwhals_ops import NarwhalsOps

        frame = self.current_frame or self.original_frame or self.frame

        if frame is None:
            return None

        return NarwhalsOps.get_page(frame, page_num, page_size)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataset metadata."""
        return {
            "name": self.name,
            "source": self.source,
            "backend": self.backend,
            "operations": [op.to_dict() for op in self.operation_history],
        }

    def get_filtered_row_count(self) -> int:
        """Get row count after applying operations."""
        if self.current_frame is None:
            return self.row_count
        # For now, return original count - should be optimized
        return self.row_count
