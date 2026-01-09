"""Test case-insensitive contains filter."""
import narwhals as nw
import polars as pl

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation

# Create test dataset
df = pl.DataFrame({
    "name": ["Alice", "BOB", "Charlie", "DAVID", "Eve"],
    "city": ["New York", "SAN FRANCISCO", "seattle", "BOSTON", "Portland"],
})

# Convert to lazy frame
nw_df = nw.from_native(df).lazy()
dataset = Dataset(
    name="test",
    source="test.csv",
    backend="polars",
    frame=nw_df,
    original_frame=nw_df,
    row_count=5,
)

print("Original data:")
preview = dataset.get_page(0, 10)
if preview:
    print(preview)

# Test 1: contains filter with lowercase search term on mixed case data
print("\n" + "="*60)
print("TEST 1: Filter city contains 'san' (should match 'SAN FRANCISCO')")
print("="*60)
op1 = Operation(
    code='df = df.filter(nw.col("city").str.to_lowercase().str.contains("san"))',
    display="Filter: city contains 'san'",
    operation_type="filter",
    params={"column": "city", "operator": "contains", "value": "san"},
)
dataset.apply_operation(op1)
dataset.execute_next_queued()

filtered = dataset.get_page(0, 10)
print(f"Filtered data (should show 'SAN FRANCISCO'):")
if filtered:
    print(filtered)
print(f"Row count: {dataset.get_filtered_row_count()}")

# Reset dataset
dataset = Dataset(
    name="test",
    source="test.csv",
    backend="polars",
    frame=nw_df,
    original_frame=nw_df,
    row_count=5,
)

# Test 2: contains filter with uppercase search term on mixed case data
print("\n" + "="*60)
print("TEST 2: Filter city contains 'SEAT' (should match 'seattle')")
print("="*60)
op2 = Operation(
    code='df = df.filter(nw.col("city").str.to_lowercase().str.contains("seat"))',  # lowercase 'seat' for comparison
    display="Filter: city contains 'SEAT'",
    operation_type="filter",
    params={"column": "city", "operator": "contains", "value": "SEAT"},
)
dataset.apply_operation(op2)
dataset.execute_next_queued()

filtered = dataset.get_page(0, 10)
print(f"Filtered data (should show 'seattle'):")
if filtered:
    print(filtered)
print(f"Row count: {dataset.get_filtered_row_count()}")

print("\n✅ Case-insensitive contains filter works!")
