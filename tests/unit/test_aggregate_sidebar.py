"""Test AggregateSidebar functionality."""

import pytest
from kittiwake.widgets.sidebars import AggregateSidebar


def test_aggregate_sidebar_initialization():
    """Test AggregateSidebar initializes correctly."""
    columns = ["age", "salary", "name"]
    sidebar = AggregateSidebar(columns=columns)

    assert sidebar.columns == columns
    assert sidebar.callback is None
    assert len(sidebar.AGG_FUNCTIONS) == 7  # count, sum, mean, median, min, max, std


def test_aggregate_sidebar_callback():
    """Test AggregateSidebar callback handling."""
    columns = ["age", "salary", "name"]
    sidebar = AggregateSidebar(columns=columns)

    received_params = {}

    def test_callback(params):
        received_params.update(params)

    sidebar.callback = test_callback

    # Simulate callback trigger
    test_params = {
        "agg_column": "salary",
        "agg_functions": ["sum", "mean"],
        "group_by": "department",
    }
    sidebar.callback(test_params)

    assert received_params == test_params


def test_aggregate_sidebar_functions():
    """Test all aggregation functions are available."""
    sidebar = AggregateSidebar()

    expected_functions = ["count", "sum", "mean", "median", "min", "max", "std"]

    actual_functions = [func_id for func_id, _ in sidebar.AGG_FUNCTIONS]

    assert actual_functions == expected_functions


if __name__ == "__main__":
    test_aggregate_sidebar_initialization()
    test_aggregate_sidebar_callback()
    test_aggregate_sidebar_functions()
    print("All tests passed!")
