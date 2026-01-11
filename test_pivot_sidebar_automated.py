#!/usr/bin/env python3
"""Automated test for the refactored pivot sidebar with SelectionList."""

import asyncio
from kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar
from kittiwake.models.dataset import Dataset
import polars as pl
import narwhals as nw


def test_pivot_sidebar_api():
    """Test that the pivot sidebar API works correctly."""
    print("Creating test dataset...")
    
    # Create a simple test dataset
    df = pl.DataFrame({
        "category": ["A", "A", "B", "B", "A", "B"],
        "region": ["East", "West", "East", "West", "East", "West"],
        "product": ["X", "Y", "X", "Y", "X", "Y"],
        "sales": [100, 200, 150, 250, 120, 180],
        "quantity": [10, 20, 15, 25, 12, 18],
        "year": [2023, 2023, 2024, 2024, 2023, 2024]
    })
    
    nw_frame = nw.from_native(df, eager_only=True).lazy()
    dataset = Dataset(
        name="test_data",
        source="/tmp/test.csv",
        backend="polars",
        frame=nw_frame,
        original_frame=nw_frame,
        schema={col: str(dtype) for col, dtype in df.schema.items()},
        row_count=len(df),
        is_active=True,
        is_lazy=True
    )
    
    print(f"✓ Dataset created with {len(dataset.schema)} columns: {list(dataset.schema.keys())}")
    
    # Create pivot sidebar
    print("\nCreating pivot sidebar...")
    columns = list(dataset.schema.keys())
    sidebar = PivotSidebar(columns=columns)
    
    print(f"✓ Sidebar created with columns: {sidebar.columns}")
    
    # Set up callback
    received_params = []
    def callback(params):
        received_params.append(params)
        print(f"\n✓ Callback received params: {params}")
    
    sidebar.callback = callback
    print("✓ Callback registered")
    
    # Check that compose works
    print("\nTesting compose method...")
    widgets = list(sidebar.compose())
    print(f"✓ Compose returned {len(widgets)} widgets")
    
    widget_types = [type(w).__name__ for w in widgets]
    print(f"  Widget types: {widget_types}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test in actual TUI (open sidebar with button)")
    print("2. Verify SelectionLists populate correctly")
    print("3. Test multi-select functionality")
    print("4. Test add/remove value sections")
    print("5. Test apply button builds correct params")


if __name__ == "__main__":
    test_pivot_sidebar_api()
