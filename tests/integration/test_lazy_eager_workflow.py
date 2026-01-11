"""Integration tests for lazy/eager execution workflow."""

import pytest
import pandas as pd
import narwhals as nw

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation, OperationError


class TestLazyWorkflow:
    """Test complete lazy execution workflows."""

    def test_lazy_queue_and_execute_workflow(self):
        """Test queuing multiple operations and executing them."""
        # Setup: Create dataset with sample data
        pdf = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "age": [25, 30, 35, 28, 32],
                "city": ["NYC", "LA", "NYC", "SF", "LA"],
            }
        )
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="People",
            source="people.csv",
            frame=df,
            original_frame=df,
            execution_mode="lazy",
        )

        # Queue operations
        filter_op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        )

        select_op = Operation(
            code="df = df.select(['name', 'age'])",
            display="Select: name, age",
            operation_type="select",
            params={"columns": ["name", "age"]},
        )

        sort_op = Operation(
            code="df = df.sort('age')",
            display="Sort by age",
            operation_type="sort",
            params={"column": "age"},
        )

        # Apply operations (should queue in lazy mode)
        ds.apply_operation(filter_op)
        ds.apply_operation(select_op)
        ds.apply_operation(sort_op)

        # Verify all queued
        assert len(ds.queued_operations) == 3
        assert len(ds.executed_operations) == 0
        assert all(op.state == "queued" for op in ds.queued_operations)

        # Execute all
        count = ds.execute_all_queued()

        # Verify execution
        assert count == 3
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 3
        assert all(op.state == "executed" for op in ds.executed_operations)
        assert ds.current_frame is not None

        # Verify result
        result = ds.current_frame.collect()
        assert len(result.columns) == 2
        assert list(result.columns) == ["name", "age"]
        # After filter (age > 25), select, and sort, should have 4 rows
        assert len(result) == 4

    def test_lazy_partial_execution(self):
        """Test executing operations one at a time."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="lazy")

        # Queue three operations
        for i in range(3):
            op = Operation(
                code=f"df = df.with_columns(nw.lit({i}).alias('col{i}'))",
                display=f"Add col{i}",
                operation_type="with_columns",
                params={},
            )
            ds.apply_operation(op)

        assert len(ds.queued_operations) == 3

        # Execute one at a time
        assert ds.execute_next_queued() is True
        assert len(ds.queued_operations) == 2
        assert len(ds.executed_operations) == 1

        assert ds.execute_next_queued() is True
        assert len(ds.queued_operations) == 1
        assert len(ds.executed_operations) == 2

        assert ds.execute_next_queued() is True
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 3

    def test_lazy_error_recovery(self):
        """Test error handling and recovery in lazy mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="lazy")

        # Queue valid operation
        good_op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Valid filter",
            operation_type="filter",
            params={},
        )

        # Queue invalid operation
        bad_op = Operation(
            code="df = df.filter(nw.col('invalid_column') > 0)",
            display="Invalid filter",
            operation_type="filter",
            params={},
        )

        # Queue another valid operation
        good_op2 = Operation(
            code="df = df.select(['name'])",
            display="Select name",
            operation_type="select",
            params={},
        )

        ds.apply_operation(good_op)
        ds.apply_operation(bad_op)
        ds.apply_operation(good_op2)

        # Execute all (should stop at bad_op)
        count = ds.execute_all_queued()

        # First operation executed successfully
        assert count == 1
        assert len(ds.executed_operations) == 1

        # Bad operation marked as failed and still in queue
        assert len(ds.queued_operations) == 2
        assert ds.queued_operations[0] == bad_op
        assert bad_op.state == "failed"
        assert bad_op.error_message is not None

        # Good op2 still queued
        assert ds.queued_operations[1] == good_op2
        assert good_op2.state == "queued"

        # Clear bad operation
        ds.queued_operations.pop(0)

        # Execute remaining valid operation
        count = ds.execute_all_queued()
        assert count == 1
        assert len(ds.executed_operations) == 2


class TestEagerWorkflow:
    """Test complete eager execution workflows."""

    def test_eager_immediate_execution(self):
        """Test that operations execute immediately in eager mode."""
        pdf = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "city": ["NYC", "LA", "SF"],
            }
        )
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="eager")

        # Apply operations
        filter_op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={},
        )

        select_op = Operation(
            code="df = df.select(['name', 'city'])",
            display="Select: name, city",
            operation_type="select",
            params={},
        )

        ds.apply_operation(filter_op)

        # First operation executed immediately
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 1
        assert filter_op.state == "executed"

        ds.apply_operation(select_op)

        # Second operation also executed immediately
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 2
        assert select_op.state == "executed"

        # Verify result
        result = ds.current_frame.collect()
        assert list(result.columns) == ["name", "city"]
        assert len(result) == 2  # Bob and Charlie

    def test_eager_error_handling(self):
        """Test error handling in eager mode."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="eager")

        # Apply valid operation
        good_op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Valid filter",
            operation_type="filter",
            params={},
        )
        ds.apply_operation(good_op)
        assert len(ds.executed_operations) == 1

        # Try to apply invalid operation
        bad_op = Operation(
            code="df = df.filter(nw.col('invalid_column') > 0)",
            display="Invalid filter",
            operation_type="filter",
            params={},
        )

        with pytest.raises(OperationError):
            ds.apply_operation(bad_op)

        # Verify state: good operation executed, bad operation not added
        assert len(ds.executed_operations) == 1
        assert len(ds.queued_operations) == 0


class TestModeSwitching:
    """Test switching between lazy and eager modes."""

    def test_mode_switch_workflow(self):
        """Test complete workflow switching between modes."""
        pdf = pd.DataFrame(
            {"name": ["Alice", "Bob", "Charlie", "David"], "age": [25, 30, 35, 28]}
        )
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            execution_mode="lazy",  # Start in lazy mode
        )

        # Phase 1: Queue operations in lazy mode
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={},
        )
        op2 = Operation(
            code="df = df.select(['name', 'age'])",
            display="Select",
            operation_type="select",
            params={},
        )

        ds.apply_operation(op1)
        ds.apply_operation(op2)

        assert len(ds.queued_operations) == 2
        assert len(ds.executed_operations) == 0

        # Phase 2: Execute queued operations
        count = ds.execute_all_queued()
        assert count == 2
        assert len(ds.executed_operations) == 2

        # Phase 3: Switch to eager mode
        ds.execution_mode = "eager"

        op3 = Operation(
            code="df = df.sort('age')", display="Sort", operation_type="sort", params={}
        )
        ds.apply_operation(op3)

        # Should execute immediately
        assert len(ds.queued_operations) == 0
        assert len(ds.executed_operations) == 3
        assert op3.state == "executed"

        # Phase 4: Switch back to lazy mode
        ds.execution_mode = "lazy"

        op4 = Operation(
            code="df = df.with_columns(nw.lit(True).alias('verified'))",
            display="Add verified",
            operation_type="with_columns",
            params={},
        )
        ds.apply_operation(op4)

        # Should queue again
        assert len(ds.queued_operations) == 1
        assert len(ds.executed_operations) == 3
        assert op4.state == "queued"


class TestComplexWorkflows:
    """Test complex real-world workflows."""

    def test_data_exploration_workflow(self):
        """Test a typical data exploration workflow."""
        # Load data
        pdf = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
                "age": [25, 30, 35, 28, 32, 29],
                "salary": [50000, 60000, 75000, 55000, 68000, 58000],
                "department": ["Sales", "IT", "Sales", "IT", "HR", "Sales"],
            }
        )
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Employees",
            source="employees.csv",
            frame=df,
            original_frame=df,
            row_count=6,
            execution_mode="lazy",
        )

        # Explore: Queue multiple filters and transformations
        operations = [
            Operation(
                code="df = df.filter(nw.col('age') >= 28)",
                display="Filter: age >= 28",
                operation_type="filter",
                params={},
            ),
            Operation(
                code="df = df.filter(nw.col('salary') > 55000)",
                display="Filter: salary > 55000",
                operation_type="filter",
                params={},
            ),
            Operation(
                code="df = df.select(['name', 'department', 'salary'])",
                display="Select key columns",
                operation_type="select",
                params={},
            ),
            Operation(
                code="df = df.sort('salary')",
                display="Sort by salary",
                operation_type="sort",
                params={},
            ),
        ]

        # Queue all operations
        for op in operations:
            ds.apply_operation(op)

        assert len(ds.queued_operations) == 4

        # Execute all at once
        count = ds.execute_all_queued()

        assert count == 4
        assert len(ds.executed_operations) == 4

        # Verify final result
        result = ds.current_frame.collect()
        assert list(result.columns) == ["name", "department", "salary"]
        assert (
            len(result) == 4
        )  # Bob, Eve, Charlie, Frank (all age >= 28 and salary > 55000)

    def test_checkpoint_and_undo_workflow(self):
        """Test workflow with checkpoints and undo."""
        pdf = pd.DataFrame(
            {"name": ["Alice", "Bob", "Charlie"], "value": [100, 200, 300]}
        )
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(
            name="Test",
            frame=df,
            original_frame=df,
            checkpoint_interval=2,
            execution_mode="eager",
        )

        # Apply 5 operations (checkpoints at 2 and 4)
        for i in range(5):
            op = Operation(
                code=f"df = df.with_columns(nw.lit({i}).alias('step{i}'))",
                display=f"Step {i}",
                operation_type="with_columns",
                params={},
            )
            ds.apply_operation(op)

        # Verify checkpoints exist
        assert 2 in ds.checkpoints
        assert 4 in ds.checkpoints
        assert len(ds.executed_operations) == 5

        # Undo last operation
        result = ds.undo()
        assert result is True
        assert len(ds.operation_history) == 4

        # Undo again
        result = ds.undo()
        assert result is True
        assert len(ds.operation_history) == 3


class TestEdgeCases:
    """Test edge cases in workflows."""

    def test_empty_dataset_operations(self):
        """Test operations on empty dataset."""
        pdf = pd.DataFrame({"name": [], "age": []})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Empty", frame=df, original_frame=df, execution_mode="lazy")

        op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Filter",
            operation_type="filter",
            params={},
        )
        ds.apply_operation(op)

        count = ds.execute_all_queued()
        assert count == 1

        result = ds.current_frame.collect()
        assert len(result) == 0

    def test_clear_and_restart(self):
        """Test clearing queue and restarting."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()
        ds = Dataset(name="Test", frame=df, original_frame=df, execution_mode="lazy")

        # Queue some operations
        for i in range(3):
            op = Operation(
                code=f"df = df.with_columns(nw.lit({i}).alias('col{i}'))",
                display=f"Op {i}",
                operation_type="with_columns",
                params={},
            )
            ds.apply_operation(op)

        assert len(ds.queued_operations) == 3

        # Clear queue
        count = ds.clear_queued()
        assert count == 3
        assert len(ds.queued_operations) == 0

        # Queue new operations
        new_op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="New filter",
            operation_type="filter",
            params={},
        )
        ds.apply_operation(new_op)

        count = ds.execute_all_queued()
        assert count == 1
        assert len(ds.executed_operations) == 1
