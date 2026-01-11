"""Manual test for AggregateSidebar integration."""

from kittiwake.widgets.sidebars import AggregateSidebar
from kittiwake.services.narwhals_ops import generate_aggregate_code
from kittiwake.models.operations import Operation


def test_aggregate_flow():
    """Test the complete aggregate flow."""
    print("=" * 60)
    print("Testing AggregateSidebar Integration")
    print("=" * 60)

    # Step 1: Create sidebar
    columns = ["salary", "age", "department", "years_experience"]
    sidebar = AggregateSidebar(columns=columns)
    print(f"\n✓ Created AggregateSidebar with {len(columns)} columns")

    # Step 2: Test with single function
    print("\n--- Test 1: Single aggregation with group by ---")
    params = {
        "agg_column": "salary",
        "agg_functions": ["sum"],
        "group_by": "department",
    }

    code_params = {
        "agg_col": params["agg_column"],
        "agg_func": params["agg_functions"],
        "group_by": params["group_by"],
    }

    code, display = generate_aggregate_code(code_params)
    operation = Operation(
        code=code, display=display, operation_type="aggregate", params=params
    )

    print(f"  Code: {code}")
    print(f"  Display: {display}")
    print(f"  ✓ Operation created")

    # Step 3: Test with multiple functions
    print("\n--- Test 2: Multiple aggregations with group by ---")
    params = {
        "agg_column": "salary",
        "agg_functions": ["sum", "mean", "count", "min", "max"],
        "group_by": "department",
    }

    code_params = {
        "agg_col": params["agg_column"],
        "agg_func": params["agg_functions"],
        "group_by": params["group_by"],
    }

    code, display = generate_aggregate_code(code_params)
    operation = Operation(
        code=code, display=display, operation_type="aggregate", params=params
    )

    print(f"  Code: {code}")
    print(f"  Display: {display}")
    print(f"  ✓ Operation created")

    # Step 4: Test without group by (global aggregation)
    print("\n--- Test 3: Global aggregation (no group by) ---")
    params = {
        "agg_column": "salary",
        "agg_functions": ["mean", "median", "std"],
        "group_by": None,
    }

    code_params = {"agg_col": params["agg_column"], "agg_func": params["agg_functions"]}

    code, display = generate_aggregate_code(code_params)
    operation = Operation(
        code=code, display=display, operation_type="aggregate", params=params
    )

    print(f"  Code: {code}")
    print(f"  Display: {display}")
    print(f"  ✓ Operation created")

    print("\n" + "=" * 60)
    print("✓ All integration tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_aggregate_flow()
