"""Unit tests for Dataset model."""

import pytest
import pandas as pd
import narwhals as nw
from uuid import UUID

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation, OperationError


class TestDatasetBasics:
    """Test basic Dataset functionality."""

    def test_dataset_creation(self):
        """Test basic dataset creation."""
        ds = Dataset(name="Test Dataset", source="/path/to/data.csv")
        
        assert ds.name == "Test Dataset"
        assert ds.source == "/path/to/data.csv"
        assert isinstance(ds.id, UUID)
        assert ds.execution_mode == "lazy"  # Default mode
        assert ds.queued_operations == []
        assert ds.executed_operations == []
        assert ds.operation_history == []

    def test_dataset_with_dataframe(self):
        """Test dataset with loaded dataframe."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        
        ds = Dataset(
            name="Test",
            source="test.csv",
            frame=df,
            original_frame=df,
            row_count=2
        )
        
        assert ds.frame is not None
        assert ds.original_frame is not None
        assert ds.row_count == 2

    def test_unique_dataset_ids(self):
        """Test that each dataset gets a unique ID."""
        ds1 = Dataset(name="Dataset 1")
        ds2 = Dataset(name="Dataset 2")
        
        assert ds1.id != ds2.id


class TestLazyMode:
    """Test lazy execution mode."""

    def test_lazy_mode_default(self):
        """Test lazy mode is the default."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        assert ds.execution_mode == "lazy"

    def test_apply_operation_in_lazy_mode_queues(self):
        """Test that apply_operation queues in lazy mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="lazy")
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={}
        )
        
        ds.apply_operation(op)
        
        assert len(ds.queued_operations) == 1
        assert ds.queued_operations[0] == op
        assert op.state == "queued"
        assert len(ds.executed_operations) == 0

    def test_queue_operation_directly(self):
        """Test queue_operation method."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select name",
            operation_type="select",
            params={}
        )
        
        ds.queue_operation(op1)
        ds.queue_operation(op2)
        
        assert len(ds.queued_operations) == 2
        assert ds.queued_operations[0] == op1
        assert ds.queued_operations[1] == op2
        assert op1.state == "queued"
        assert op2.state == "queued"

    def test_execute_next_queued(self):
        """Test executing next queued operation."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={}
        )
        
        ds.queue_operation(op)
        assert len(ds.queued_operations) == 1
        
        result = ds.execute_next_queued()
        
        assert result is True
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 1
        assert ds.executed_operations[0] == op
        assert op.state == "executed"
        assert ds.current_frame is not None

    def test_execute_next_queued_empty_queue(self):
        """Test executing when queue is empty."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        result = ds.execute_next_queued()
        
        assert result is False

    def test_execute_next_queued_with_error(self):
        """Test executing queued operation that fails."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op = Operation(
            code="df = df.filter(nw.col('invalid_column') > 25)",
            display="Filter: invalid",
            operation_type="filter",
            params={}
        )
        
        ds.queue_operation(op)
        
        with pytest.raises(Exception):
            ds.execute_next_queued()
        
        # Operation should be marked as failed and stay in queue
        assert len(ds.queued_operations) == 1
        assert op.state == "failed"
        assert op.error_message is not None

    def test_execute_all_queued(self):
        """Test executing all queued operations."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select name",
            operation_type="select",
            params={}
        )
        op3 = Operation(
            code="df = df.sort('name')",
            display="Sort by name",
            operation_type="sort",
            params={}
        )
        
        ds.queue_operation(op1)
        ds.queue_operation(op2)
        ds.queue_operation(op3)
        
        count = ds.execute_all_queued()
        
        assert count == 3
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 3
        assert all(op.state == "executed" for op in ds.executed_operations)

    def test_execute_all_queued_stops_on_error(self):
        """Test execute_all_queued stops on first error."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.filter(nw.col('invalid') > 0)",
            display="Invalid filter",
            operation_type="filter",
            params={}
        )
        op3 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        
        ds.queue_operation(op1)
        ds.queue_operation(op2)
        ds.queue_operation(op3)
        
        count = ds.execute_all_queued()
        
        # Should execute op1, fail on op2, and stop
        assert count == 1
        assert len(ds.executed_operations) == 1
        assert ds.executed_operations[0] == op1
        
        # op2 should be failed and at front of queue, op3 still queued
        assert len(ds.queued_operations) == 2
        assert ds.queued_operations[0] == op2
        assert op2.state == "failed"
        assert ds.queued_operations[1] == op3
        assert op3.state == "queued"

    def test_clear_queued(self):
        """Test clearing queued operations."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        
        ds.queue_operation(op1)
        ds.queue_operation(op2)
        
        count = ds.clear_queued()
        
        assert count == 2
        assert len(ds.queued_operations) == 0


class TestEagerMode:
    """Test eager execution mode."""

    def test_eager_mode_executes_immediately(self):
        """Test that operations execute immediately in eager mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={}
        )
        
        ds.apply_operation(op)
        
        # Should execute immediately, not queue
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 1
        assert ds.executed_operations[0] == op
        assert op.state == "executed"
        assert ds.current_frame is not None

    def test_eager_mode_multiple_operations(self):
        """Test multiple operations in eager mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        
        ds.apply_operation(op1)
        ds.apply_operation(op2)
        
        assert len(ds.executed_operations) == 2
        assert len(ds.queued_operations) == 0
        assert all(op.state == "executed" for op in ds.executed_operations)

    def test_eager_mode_operation_failure(self):
        """Test operation failure in eager mode."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('invalid_column') > 25)",
            display="Invalid filter",
            operation_type="filter",
            params={}
        )
        
        with pytest.raises(OperationError):
            ds.apply_operation(op)


class TestModeSwitching:
    """Test switching between lazy and eager modes."""

    def test_switch_from_lazy_to_eager(self):
        """Test switching from lazy to eager mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="lazy")
        
        # Queue operation in lazy mode
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op1)
        assert len(ds.queued_operations) == 1
        
        # Switch to eager mode
        ds.execution_mode = "eager"
        
        # New operations should execute immediately
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        ds.apply_operation(op2)
        
        # op1 still queued, op2 executed
        assert len(ds.queued_operations) == 1
        assert len(ds.executed_operations) == 1

    def test_switch_from_eager_to_lazy(self):
        """Test switching from eager to lazy mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="eager")
        
        # Execute operation in eager mode
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op1)
        assert len(ds.executed_operations) == 1
        
        # Switch to lazy mode
        ds.execution_mode = "lazy"
        
        # New operations should queue
        op2 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        ds.apply_operation(op2)
        
        assert len(ds.executed_operations) == 1
        assert len(ds.queued_operations) == 1


class TestCheckpoints:
    """Test checkpoint functionality."""

    def test_checkpoint_created_at_interval(self):
        """Test checkpoints are created at specified interval."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            checkpoint_interval=2,
            execution_mode="eager"
        )
        
        for i in range(5):
            op = Operation(
                code=f"df = df.with_columns(nw.lit({i}).alias('col{i}'))",
                display=f"Add col{i}",
                operation_type="with_columns",
                params={}
            )
            ds.apply_operation(op)
        
        # Should have checkpoints at 2 and 4
        assert 2 in ds.checkpoints
        assert 4 in ds.checkpoints


class TestBackwardsCompatibility:
    """Test backwards compatibility with operation_history."""

    def test_operation_history_updated(self):
        """Test operation_history is updated for backwards compatibility."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        
        ds.apply_operation(op)
        
        # Should be in both executed_operations and operation_history
        assert len(ds.executed_operations) == 1
        assert len(ds.operation_history) == 1
        assert ds.operation_history[0] == op


class TestSerialization:
    """Test dataset serialization."""

    def test_to_dict(self):
        """Test dataset serialization to dict."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test Dataset",
            source="test.csv",
            backend="pandas",
            frame=df,
            original_frame=df,
            execution_mode="lazy"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.queue_operation(op)
        
        result = ds.to_dict()
        
        assert result["name"] == "Test Dataset"
        assert result["source"] == "test.csv"
        assert result["backend"] == "pandas"
        assert result["execution_mode"] == "lazy"
        assert len(result["queued_operations"]) == 1
        assert len(result["executed_operations"]) == 0


class TestUndoRedo:
    """Test undo/redo functionality."""

    def test_undo_single_operation(self):
        """Test undoing a single operation."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op)
        
        result = ds.undo()
        
        assert result is True
        assert len(ds.operation_history) == 0

    def test_undo_without_operations(self):
        """Test undo when no operations exist."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        result = ds.undo()
        
        assert result is False

    def test_undo_with_checkpoint(self):
        """Test undo with checkpoints."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25], "city": ["NYC"]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            checkpoint_interval=2,
            execution_mode="eager"
        )
        
        # Create 3 operations (checkpoint at 2)
        for i in range(3):
            op = Operation(
                code=f"df = df.with_columns(nw.lit({i}).alias('col{i}'))",
                display=f"Add col{i}",
                operation_type="with_columns",
                params={}
            )
            ds.apply_operation(op)
        
        result = ds.undo()
        
        assert result is True
        assert len(ds.operation_history) == 2

    def test_undo_with_none_frame(self):
        """Test undo when current_frame becomes None."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op)
        
        # Manually set current_frame to None to test edge case
        ds.current_frame = None
        
        result = ds.undo()
        
        # Should succeed because it restores from original_frame
        assert result is True

    def test_redo_after_undo(self):
        """Test redo after undoing an operation."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op)
        
        # Undo the operation
        assert ds.undo() is True
        assert len(ds.executed_operations) == 0
        assert len(ds.redo_stack) == 1
        
        # Redo the operation
        result = ds.redo()
        
        assert result is True
        assert len(ds.executed_operations) == 1
        assert len(ds.redo_stack) == 0
        assert ds.executed_operations[0] == op
    
    def test_redo_without_undo(self):
        """Test redo when no operations have been undone."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        result = ds.redo()
        
        assert result is False
        assert len(ds.redo_stack) == 0
    
    def test_redo_stack_cleared_on_new_operation(self):
        """Test redo stack is cleared when new operation is applied."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op1)
        
        # Undo and verify redo stack has the operation
        ds.undo()
        assert len(ds.redo_stack) == 1
        
        # Apply a new operation
        op2 = Operation(
            code="df = df.filter(nw.col('age') < 30)",
            display="Filter 2",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op2)
        
        # Redo stack should be cleared
        assert len(ds.redo_stack) == 0
    
    def test_multiple_undo_redo(self):
        """Test multiple undo and redo operations."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        op2 = Operation(
            code="df = df.filter(nw.col('age') < 35)",
            display="Filter 2",
            operation_type="filter",
            params={}
        )
        op3 = Operation(
            code="df = df.select(['name'])",
            display="Select",
            operation_type="select",
            params={}
        )
        
        ds.apply_operation(op1)
        ds.apply_operation(op2)
        ds.apply_operation(op3)
        
        assert len(ds.executed_operations) == 3
        
        # Undo twice
        assert ds.undo() is True
        assert ds.undo() is True
        assert len(ds.executed_operations) == 1
        assert len(ds.redo_stack) == 2
        
        # Redo once
        assert ds.redo() is True
        assert len(ds.executed_operations) == 2
        assert len(ds.redo_stack) == 1
        
        # Redo again
        assert ds.redo() is True
        assert len(ds.executed_operations) == 3
        assert len(ds.redo_stack) == 0
    
    def test_redo_stack_cleared_on_execute_queued(self):
        """Test redo stack is cleared when queued operation is executed."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="lazy"  # Start in lazy mode
        )
        
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={}
        )
        
        # Switch to eager to execute and create history
        ds.execution_mode = "eager"
        ds.apply_operation(op1)
        
        # Undo and verify redo stack
        ds.undo()
        assert len(ds.redo_stack) == 1
        
        # Switch back to lazy and queue + execute new operation
        ds.execution_mode = "lazy"
        op2 = Operation(
            code="df = df.filter(nw.col('age') < 30)",
            display="Filter 2",
            operation_type="filter",
            params={}
        )
        ds.queue_operation(op2)
        ds.execute_next_queued()
        
        # Redo stack should be cleared
        assert len(ds.redo_stack) == 0


class TestDataAccess:
    """Test data access methods."""

    def test_get_filtered_row_count_with_current_frame(self):
        """Test get_filtered_row_count with current_frame."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            row_count=2,
            execution_mode="eager"
        )
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op)
        
        # Now returns actual filtered row count after operations are applied
        count = ds.get_filtered_row_count()
        
        assert count == 1  # Only Bob (age=30) passes the filter (age > 25)

    def test_get_filtered_row_count_without_current_frame(self):
        """Test get_filtered_row_count without current_frame."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            row_count=2
        )
        
        count = ds.get_filtered_row_count()
        
        assert count == 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_execute_operation_without_dataframe(self):
        """Test executing operation when no dataframe is loaded."""
        ds = Dataset(name="Test", frame=None, original_frame=None)
        
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        
        ds.queue_operation(op)
        
        with pytest.raises(OperationError, match="No dataset loaded"):
            ds.execute_next_queued()

    def test_execute_all_on_empty_queue(self):
        """Test execute_all_queued on empty queue."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        count = ds.execute_all_queued()
        
        assert count == 0

    def test_clear_empty_queue(self):
        """Test clearing empty queue."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df)
        
        count = ds.clear_queued()
        
        assert count == 0

    def test_undo_with_empty_history(self):
        """Test undo with empty operation history."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="eager"
        )
        
        # Create and execute an operation
        op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Filter",
            operation_type="filter",
            params={}
        )
        ds.apply_operation(op)
        
        # Undo once
        ds.undo()
        
        # Try to undo again when history is empty
        result = ds.undo()
        
        assert result is False
