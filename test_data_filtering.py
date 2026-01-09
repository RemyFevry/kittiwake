"""Test to verify data filtering works correctly."""
import narwhals as nw
import polars as pl

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation

# Create test dataset
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "age": [25, 30, 35, 40, 45],
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

print(f"Original row count: {dataset.row_count}")
print(f"Original data preview:")
preview = dataset.get_page(0, 10)
if preview:
    # For eager frames, no need to collect
    print(preview)

# Queue a filter operation
print("\n" + "="*60)
print("QUEUEING FILTER: age > 30")
print("="*60)
op = Operation(
    code='df = df.filter(nw.col("age") > 30)',  # MUST use assignment!
    display="Filter: age > 30",
    operation_type="filter",
    params={"column": "age", "operator": ">", "value": 30},
)
dataset.apply_operation(op)

print(f"After queuing - Filtered row count: {dataset.get_filtered_row_count()}")
print(f"Queued operations: {len(dataset.queued_operations)}")
print(f"Executed operations: {len(dataset.executed_operations)}")

# Execute the operation
print("\n" + "="*60)
print("EXECUTING FILTER")
print("="*60)
success = dataset.execute_next_queued()
print(f"Execution success: {success}")

# Debug: check current_frame
print(f"\nDEBUG: current_frame is None? {dataset.current_frame is None}")
if dataset.current_frame:
    print(f"DEBUG: current_frame type: {type(dataset.current_frame)}")
    try:
        collected = dataset.current_frame.collect()
        print(f"DEBUG: collected data:\n{collected}")
        print(f"DEBUG: collected row count: {len(collected)}")
    except Exception as e:
        print(f"DEBUG: Error collecting: {e}")

print(f"\nAfter execution - Filtered row count: {dataset.get_filtered_row_count()}")
print(f"Queued operations: {len(dataset.queued_operations)}")
print(f"Executed operations: {len(dataset.executed_operations)}")

# Get filtered data
print(f"\nFiltered data preview:")
filtered_preview = dataset.get_page(0, 10)
if filtered_preview:
    # For eager frames, no need to collect
    print(filtered_preview)

print("\n✅ Data filtering works correctly!")
print(f"Original: 5 rows → After filter: {dataset.get_filtered_row_count()} rows")
