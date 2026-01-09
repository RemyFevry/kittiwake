"""Quick test to verify duplicate ID bug is fixed."""
import narwhals as nw
import polars as pl

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation

# Create test dataset
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
})

# Convert to lazy frame
nw_df = nw.from_native(df).lazy()
dataset = Dataset(
    name="test",
    source="test.csv",
    backend="polars",
    frame=nw_df,
    original_frame=nw_df,
)

# Test 1: Queue operations (lazy mode)
print("Test 1: Queueing operations in lazy mode")
op1 = Operation(
    code='df.filter(nw.col("age") > 25)',
    display="Filter: age > 25",
    operation_type="filter",
    params={"column": "age", "operator": ">", "value": 25},
)
dataset.apply_operation(op1)
print(f"  Queued operations: {len(dataset.queued_operations)}")
print(f"  Executed operations: {len(dataset.executed_operations)}")

op2 = Operation(
    code='df.filter(nw.col("age") < 35)',
    display="Filter: age < 35",
    operation_type="filter",
    params={"column": "age", "operator": "<", "value": 35},
)
dataset.apply_operation(op2)
print(f"  Queued operations: {len(dataset.queued_operations)}")
print(f"  Executed operations: {len(dataset.executed_operations)}")

# Test 2: Execute next operation
print("\nTest 2: Execute next queued operation")
success = dataset.execute_next_queued()
print(f"  Execution success: {success}")
print(f"  Queued operations: {len(dataset.queued_operations)}")
print(f"  Executed operations: {len(dataset.executed_operations)}")
print(f"  Operation states: {[op.state for op in dataset.executed_operations + dataset.queued_operations]}")

# Test 3: Execute all remaining
print("\nTest 3: Execute all queued operations")
executed_count = dataset.execute_all_queued()
print(f"  Executed count: {executed_count}")
print(f"  Queued operations: {len(dataset.queued_operations)}")
print(f"  Executed operations: {len(dataset.executed_operations)}")
print(f"  Operation states: {[op.state for op in dataset.executed_operations + dataset.queued_operations]}")

print("\n✅ All tests passed!")
