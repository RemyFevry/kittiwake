"""Test PivotSidebar functionality."""

import pytest
from kittiwake.widgets.sidebars import PivotSidebar


def test_pivot_sidebar_initialization():
    """Test PivotSidebar initializes correctly."""
    columns = ["category", "region", "sales", "quantity"]
    sidebar = PivotSidebar(columns=columns)

    assert sidebar.columns == columns
    assert sidebar.callback is None
    assert len(sidebar.AGG_FUNCTIONS) == 8  # count, sum, mean, min, max, first, last, len


def test_pivot_sidebar_callback():
    """Test PivotSidebar callback handling."""
    columns = ["category", "region", "sales", "quantity"]
    sidebar = PivotSidebar(columns=columns)

    received_params = {}

    def test_callback(params):
        received_params.update(params)

    sidebar.callback = test_callback

    # Simulate callback trigger
    test_params = {
        "index": "category",
        "columns": "region",
        "values": "sales",
        "agg_functions": ["sum", "mean"],
    }
    sidebar.callback(test_params)

    assert received_params == test_params


def test_pivot_sidebar_functions():
    """Test all aggregation functions are available."""
    sidebar = PivotSidebar()

    expected_functions = ["count", "sum", "mean", "min", "max", "first", "last", "len"]

    actual_functions = [func_id for func_id, _ in sidebar.AGG_FUNCTIONS]

    assert actual_functions == expected_functions


def test_pivot_sidebar_update_columns():
    """Test updating columns after initialization."""
    sidebar = PivotSidebar(columns=["col1", "col2"])

    assert sidebar.columns == ["col1", "col2"]

    # Update columns
    new_columns = ["category", "region", "sales", "quantity"]
    sidebar.update_columns(new_columns)

    assert sidebar.columns == new_columns


if __name__ == "__main__":
    test_pivot_sidebar_initialization()
    test_pivot_sidebar_callback()
    test_pivot_sidebar_functions()
    test_pivot_sidebar_update_columns()
    print("All tests passed!")
