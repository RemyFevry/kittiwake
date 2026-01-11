"""Integration tests for pivot code generation in narwhals_ops.py."""

import json
import pytest
import pandas as pd
import narwhals as nw

from kittiwake.services.narwhals_ops import generate_pivot_code


class TestPivotCodeGeneration:
    """Test generate_pivot_code function with real narwhals dataframes."""

    def test_simple_pivot_single_index_single_value_sum(self):
        """Test simple pivot with single index, single value column, and sum aggregation."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", "East", "West", "East", "East", "West"],
            "amount": [10, 15, 20, 30, 10, 40],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert code structure
        assert "df.collect().pivot(" in code
        assert "on='region'" in code
        assert "index='category'" in code
        assert "values='amount'" in code
        assert "aggregate_function='sum'" in code
        assert ".lazy()" in code

        # Assert display
        assert display == "Pivot: amount(sum) by category x region"

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure - should have category as index column plus renamed East/West columns
        assert "category" in result_df.columns
        assert len(result_df) == 2  # Two categories: A and B

        # With <Column>_<value> naming, pivot columns should be amount_East, amount_West
        assert "amount_East" in result_df.columns
        assert "amount_West" in result_df.columns

        # Verify values - category A should have amount_East=10+15=25, amount_West=20
        # category B should have amount_East=30+10=40, amount_West=40
        result_dict = result_df.to_dict(as_series=False)
        cat_a_idx = result_dict["category"].index("A")
        cat_b_idx = result_dict["category"].index("B")

        assert result_dict["amount_East"][cat_a_idx] == 25  # A: 10+15
        assert result_dict["amount_West"][cat_a_idx] == 20  # A: 20
        assert result_dict["amount_East"][cat_b_idx] == 40  # B: 30+10
        assert result_dict["amount_West"][cat_b_idx] == 40  # B: 40

    def test_pivot_multiple_index_columns(self):
        """Test pivot with multiple index columns."""
        # Arrange
        params = {
            "index": ["year", "quarter"],
            "columns": "product",
            "values": [{"column": "revenue", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {
            "year": [2023, 2023, 2023, 2023, 2024, 2024],
            "quarter": ["Q1", "Q1", "Q2", "Q2", "Q1", "Q1"],
            "product": ["A", "B", "A", "B", "A", "B"],
            "revenue": [100, 150, 120, 180, 110, 160],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert code structure
        assert "index=['year', 'quarter']" in code
        assert "on='product'" in code
        assert "values='revenue'" in code
        assert "aggregate_function='sum'" in code

        # Assert display
        assert display == "Pivot: revenue(sum) by year, quarter x product"

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure
        assert "year" in result_df.columns
        assert "quarter" in result_df.columns
        assert len(result_df) == 3  # Three unique year/quarter combinations

    def test_pivot_multiple_value_columns(self):
        """Test pivot with multiple value columns."""
        # Arrange
        params = {
            "index": "store",
            "columns": "month",
            "values": [{"column": "sales", "agg_functions": ["sum"]}, {"column": "quantity", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {
            "store": ["S1", "S1", "S2", "S2"],
            "month": ["Jan", "Feb", "Jan", "Feb"],
            "sales": [1000, 1200, 800, 900],
            "quantity": [50, 60, 40, 45],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert code structure
        assert "index='store'" in code
        assert "on='month'" in code

        # Assert display
        assert display == "Pivot: sales(sum), quantity(sum) by store x month"

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure - should have store plus columns for each month/value combination
        assert "store" in result_df.columns
        assert len(result_df) == 2  # Two stores

    def test_pivot_multiple_aggregation_functions(self):
        """Test pivot with multiple aggregation functions."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum", "mean"]}],
        }

        # Create test data
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", "East", "West", "East", "East", "West"],
            "amount": [10, 20, 30, 40, 50, 60],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert code structure - should create multiple pivots
        assert "df_amount_sum_0 = df.collect().pivot(" in code
        assert "df_amount_mean_0 = df.collect().pivot(" in code
        assert "aggregate_function='sum'" in code
        assert "aggregate_function='mean'" in code
        assert ".join(df_amount_mean_0, on='category', suffix='_v1')" in code
        assert ".lazy()" in code

        # Assert display
        assert display == "Pivot: amount(sum, mean) by category x region"

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure - should have both sum and mean columns
        assert "category" in result_df.columns
        assert len(result_df) == 2  # Two categories

    def test_pivot_with_mean_aggregation(self):
        """Test pivot with mean aggregation function."""
        # Arrange
        params = {
            "index": "product",
            "columns": "quarter",
            "values": [{"column": "price", "agg_functions": ["mean"]}],
        }

        # Create test data with multiple prices per product/quarter
        data = {
            "product": ["Widget", "Widget", "Gadget", "Gadget"],
            "quarter": ["Q1", "Q1", "Q1", "Q1"],
            "price": [10.0, 12.0, 20.0, 22.0],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert
        assert "aggregate_function='mean'" in code
        assert display == "Pivot: price(mean) by product x quarter"

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()
        assert len(result_df) == 2

    def test_new_format_single_value_multiple_aggs(self):
        """Test new format with single value and multiple aggregations."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "sales", "agg_functions": ["sum", "mean"]}],
        }

        # Create test data
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "sales": [100, 200, 300, 400],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert display
        assert display == "Pivot: sales(sum, mean) by category x region"

        # Assert code structure
        assert "df_sales_sum_0 = df.collect().pivot(" in code
        assert "df_sales_mean_0 = df.collect().pivot(" in code
        assert "aggregate_function='sum'" in code
        assert "aggregate_function='mean'" in code

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure
        assert "category" in result_df.columns
        assert len(result_df) == 2  # Two categories: A and B
        # Should have sales_East and sales_West columns (not sales_amount_East)
        # because narwhals automatically prefixes with value column name
        assert "sales_East" in result_df.columns
        assert "sales_West" in result_df.columns

    def test_new_format_multiple_values_different_aggs(self):
        """Test new format with multiple values each having different aggregations."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [
                {"column": "sales", "agg_functions": ["sum"]},
                {"column": "quantity", "agg_functions": ["mean", "count"]},
            ],
        }

        # Create test data
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "sales": [100, 200, 300, 400],
            "quantity": [10, 20, 30, 40],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert display
        assert (
            display == "Pivot: sales(sum), quantity(mean, count) by category x region"
        )

        # Assert code structure
        assert "df_sales_sum_0 = df.collect().pivot(" in code
        assert "df_quantity_mean_1 = df.collect().pivot(" in code
        assert "df_quantity_count_1 = df.collect().pivot(" in code

        # Execute generated code and verify result
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Verify structure
        assert "category" in result_df.columns
        assert len(result_df) == 2
        # Should have prefixed column names like sales_East, quantity_East
        assert "sales_East" in result_df.columns
        assert "quantity_East" in result_df.columns

    def test_new_format_multiple_index_columns(self):
        """Test new format with multiple index columns."""
        # Arrange
        params = {
            "index": ["year", "quarter"],
            "columns": "product",
            "values": [{"column": "revenue", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {
            "year": [2023, 2023, 2024, 2024],
            "quarter": ["Q1", "Q2", "Q1", "Q2"],
            "product": ["A", "A", "A", "A"],
            "revenue": [100, 150, 110, 160],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert
        assert display == "Pivot: revenue(sum) by year, quarter x product"
        assert "index=['year', 'quarter']" in code

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        assert "year" in result_df.columns
        assert "quarter" in result_df.columns
        assert len(result_df) == 4

    def test_new_format_multiple_pivot_columns(self):
        """Test new format with multiple columns to pivot on."""
        # Arrange
        params = {
            "index": "category",
            "columns": ["region", "quarter"],
            "values": [{"column": "sales", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "quarter": ["Q1", "Q1", "Q1", "Q1"],
            "sales": [100, 200, 300, 400],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert
        assert display == "Pivot: sales(sum) by category x region, quarter"
        assert "on=['region', 'quarter']" in code

        # Execute and verify - narwhals creates hierarchical column names
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        assert "category" in result_df.columns
        assert len(result_df) == 2

    def test_new_format_validation_missing_column(self):
        """Test that new format raises error if value config missing column."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [
                {"agg_functions": ["sum"]}  # Missing 'column'
            ],
        }

        with pytest.raises(ValueError, match="must have a 'column' key"):
            generate_pivot_code(params)

    def test_new_format_validation_missing_agg_functions(self):
        """Test that new format raises error if value config missing agg_functions."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [
                {"column": "sales"}  # Missing 'agg_functions'
            ],
        }

        with pytest.raises(ValueError, match="must have 'agg_functions'"):
            generate_pivot_code(params)

    def test_new_format_validation_empty_agg_functions(self):
        """Test that new format raises error if agg_functions is empty."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "sales", "agg_functions": []}],
        }

        with pytest.raises(ValueError, match="must have 'agg_functions'"):
            generate_pivot_code(params)

    def test_new_format_validation_invalid_agg_function(self):
        """Test that new format raises error for invalid aggregation function."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "sales", "agg_functions": ["invalid_func"]}],
        }

        with pytest.raises(
            ValueError, match="Invalid aggregation function 'invalid_func'"
        ):
            generate_pivot_code(params)

    def test_pivot_validation_missing_params(self):
        """Test that generate_pivot_code raises error for missing parameters."""
        with pytest.raises(ValueError, match="params dictionary is required"):
            generate_pivot_code(None)  # type: ignore

        with pytest.raises(ValueError, match="index is required"):
            generate_pivot_code({"columns": "region"})

        with pytest.raises(ValueError, match="columns is required"):
            generate_pivot_code({"index": "category"})

        with pytest.raises(ValueError, match="values is required"):
            generate_pivot_code({"index": "category", "columns": "region"})

    def test_pivot_validation_invalid_aggregation_function(self):
        """Test that generate_pivot_code raises error for invalid aggregation functions."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["invalid_func"]}],
        }

        with pytest.raises(
            ValueError, match="Invalid aggregation function 'invalid_func'"
        ):
            generate_pivot_code(params)

    def test_pivot_validation_unsupported_aggregation_function(self):
        """Test that median and std are not supported for pivot."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["median"]}],
        }

        with pytest.raises(ValueError, match="Invalid aggregation function 'median'"):
            generate_pivot_code(params)

        params["values"] = [{"column": "amount", "agg_functions": ["std"]}]
        with pytest.raises(ValueError, match="Invalid aggregation function 'std'"):
            generate_pivot_code(params)

    def test_pivot_with_first_last_aggregations(self):
        """Test pivot with first and last aggregation functions."""
        # Arrange
        params = {
            "index": "user",
            "columns": "event_type",
            "values": [{"column": "timestamp", "agg_functions": ["first", "last"]}],
        }

        # Create test data
        data = {
            "user": ["Alice", "Alice", "Bob", "Bob"],
            "event_type": ["login", "login", "login", "login"],
            "timestamp": [100, 200, 150, 250],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert
        assert "aggregate_function='first'" in code
        assert "aggregate_function='last'" in code
        assert display == "Pivot: timestamp(first, last) by user x event_type"

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        assert len(result_df) == 2  # Two users

    def test_pivot_with_len_aggregation(self):
        """Test pivot with len aggregation function."""
        # Arrange
        params = {
            "index": "team",
            "columns": "project",
            "values": [{"column": "task_id", "agg_functions": ["len"]}],
        }

        # Create test data
        data = {
            "team": ["Alpha", "Alpha", "Beta", "Beta"],
            "project": ["ProjectX", "ProjectX", "ProjectX", "ProjectY"],
            "task_id": [1, 2, 3, 4],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert
        assert "aggregate_function='len'" in code
        assert display == "Pivot: task_id(len) by team x project"

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        assert len(result_df) == 2  # Two teams

    def test_pivot_validation_empty_aggregation_functions_list(self):
        """Test that empty aggregation functions list raises error."""
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": []}],
        }

        with pytest.raises(ValueError, match="must have 'agg_functions' as a non-empty"):
            generate_pivot_code(params)

    def test_pivot_single_index_as_list(self):
        """Test pivot with single index column provided as list."""
        # Arrange
        params = {
            "index": ["category"],  # Single item list
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {"category": ["A", "B"], "region": ["East", "East"], "amount": [10, 20]}
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert - single item list should be formatted as string
        assert "index='category'" in code

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()
        assert len(result_df) == 2

    def test_pivot_single_value_as_list(self):
        """Test pivot with single value column provided as list."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data
        data = {"category": ["A", "B"], "region": ["East", "East"], "amount": [10, 20]}
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute and verify
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()
        assert len(result_df) == 2

    def test_pivot_with_nulls_in_single_pivot_column(self):
        """Test pivot with null values in a single pivot column - should filter them out."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",  # Has nulls
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data with nulls in pivot column
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", None, "West", "East", None, "West"],
            "amount": [10, 15, 20, 30, 10, 40],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert - should include null filter
        assert "df = df.filter(~nw.col('region').is_null())" in code

        # Execute generated code - should not error with duplicate "null" columns
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Should only have 4 rows (filtered out 2 nulls)
        # Categories A and B, each with East and West regions
        assert "category" in result_df.columns
        assert len(result_df) == 2  # Two categories after pivot

    def test_pivot_with_nulls_in_multiple_pivot_columns(self):
        """Test pivot with null values in multiple pivot columns - prevents duplicate 'null' columns."""
        # Arrange
        params = {
            "index": "category",
            "columns": ["region", "quarter"],  # Both have nulls
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data with nulls in both pivot columns
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", None, "West", "East", None, "West"],
            "quarter": ["Q1", "Q2", None, "Q1", "Q2", None],
            "amount": [10, 15, 20, 30, 10, 40],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert - should include null filter for both columns
        assert "~nw.col('region').is_null()" in code
        assert "~nw.col('quarter').is_null()" in code
        assert " & " in code  # Should be AND condition

        # Execute generated code - should not error with duplicate "null" columns
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Only rows without nulls in pivot columns should remain
        assert len(result_df) == 2  # Two categories after pivot

    def test_pivot_v2_with_nulls_in_pivot_column(self):
        """Test new format pivot with null values in pivot column."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",  # Has nulls
            "values": [
                {"column": "amount", "agg_functions": ["sum", "mean"]},
                {"column": "count", "agg_functions": ["count"]},
            ],
        }

        # Create test data with nulls in pivot column
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", None, "West", "East", None, "West"],
            "amount": [10, 15, 20, 30, 10, 40],
            "count": [1, 1, 1, 1, 1, 1],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert - should include null filter
        assert "df = df.filter(~nw.col('region').is_null())" in code

        # Execute generated code - should not error
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Should have filtered out nulls
        assert len(result_df) == 2  # Two categories after pivot
        assert "category" in result_df.columns

    def test_pivot_with_all_nulls_in_pivot_column(self):
        """Test pivot when all values in pivot column are null - should result in empty df."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",  # All nulls
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data where all pivot column values are null
        data = {
            "category": ["A", "A", "B", "B"],
            "region": [None, None, None, None],
            "amount": [10, 15, 20, 30],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code - all rows should be filtered out
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Should be empty after filtering nulls
        assert len(result_df) == 0

    def test_pivot_without_nulls_no_filtering_impact(self):
        """Test that null filtering doesn't affect data without nulls."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data WITHOUT any nulls
        data = {
            "category": ["A", "A", "A", "B", "B", "B"],
            "region": ["East", "East", "West", "East", "East", "West"],
            "amount": [10, 15, 20, 30, 10, 40],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Should have all data since no nulls to filter
        assert len(result_df) == 2  # Two categories
        result_dict = result_df.to_dict(as_series=False)
        
        # Verify values are correct (same as test_simple_pivot_single_index_single_value_sum)
        cat_a_idx = result_dict["category"].index("A")
        cat_b_idx = result_dict["category"].index("B")
        assert result_dict["amount_East"][cat_a_idx] == 25  # A: 10+15
        assert result_dict["amount_West"][cat_a_idx] == 20  # A: 20
        assert result_dict["amount_East"][cat_b_idx] == 40  # B: 30+10
        assert result_dict["amount_West"][cat_b_idx] == 40  # B: 40

    def test_pivot_result_columns_are_float64(self):
        """Test that all pivot result columns (non-index) are Float64."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum", "count"]}],  # Even count should be Float64
        }

        # Create test data with integer amounts
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "amount": [10, 20, 30, 40],  # integers
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Assert all non-index columns are Float64
        for col in result_df.columns:
            if col != "category":
                col_dtype = str(result_df.schema[col])
                assert "Float64" in col_dtype, f"Column {col} is {col_dtype}, expected Float64"

    def test_pivot_multi_column_names_normalized(self):
        """Test that multi-pivot column names are normalized to ColA_valA-ColB_valB."""
        # Arrange
        params = {
            "index": "category",
            "columns": ["PClass", "Sex"],
            "values": [{"column": "Age", "agg_functions": ["sum"]}],
        }

        # Create test data with all combinations (convert PClass to string for pivot)
        data = {
            "category": ["A", "A", "A", "A", "B", "B"],
            "PClass": ["1", "1", "2", "2", "1", "2"],  # String values
            "Sex": ["male", "female", "male", "female", "male", "male"],
            "Age": [25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Assert column names follow PClass_1-Sex_male pattern
        expected_patterns = ["PClass_", "Sex_"]
        for col in result_df.columns:
            if col != "category":
                # Should contain both pivot column names
                for pattern in expected_patterns:
                    assert pattern in col, f"Column {col} missing {pattern}"
                # Should use hyphen separator
                assert "-" in col, f"Column {col} missing hyphen separator"

    def test_pivot_v1_multi_column_names_normalized(self):
        """Test v1 format multi-pivot column normalization."""
        # Arrange
        params = {
            "index": "category",
            "columns": ["region", "quarter"],
            "values": [{"column": "sales", "agg_functions": ["sum"]}],
        }

        # Create test data with all combinations
        data = {
            "category": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "region": ["East", "East", "West", "West", "East", "East", "West", "West"],
            "quarter": ["Q1", "Q2", "Q1", "Q2", "Q1", "Q2", "Q1", "Q2"],
            "sales": [100.0, 150.0, 200.0, 250.0, 120.0, 180.0, 220.0, 280.0],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Assert columns like amount_East-quarter_Q1
        for col in result_df.columns:
            if col != "category":
                assert "region_" in col, f"Column {col} missing region_ prefix"
                assert "quarter_" in col, f"Column {col} missing quarter_ prefix"
                assert "-" in col, f"Column {col} missing hyphen separator"

    def test_pivot_casts_integers_to_float64(self):
        """Test that integer value columns are cast to Float64 for pivot."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [{"column": "amount", "agg_functions": ["sum"]}],
        }

        # Create test data with integer amounts
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "amount": [10, 20, 30, 40],  # Pure integers
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Assert code includes cast
        assert "cast(nw.Float64)" in code

        # Execute and verify result types
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # All value columns should be Float64
        for col in result_df.columns:
            if col != "category":
                col_dtype = str(result_df.schema[col])
                assert "Float64" in col_dtype, f"Column {col} is {col_dtype}, not Float64"

    def test_pivot_v2_result_columns_are_float64(self):
        """Test v2 format pivot result columns are Float64."""
        # Arrange
        params = {
            "index": "category",
            "columns": "region",
            "values": [
                {"column": "amount", "agg_functions": ["sum", "mean"]},
                {"column": "quantity", "agg_functions": ["count"]},
            ],
        }

        # Create test data
        data = {
            "category": ["A", "A", "B", "B"],
            "region": ["East", "West", "East", "West"],
            "amount": [10, 20, 30, 40],
            "quantity": [1, 2, 3, 4],
        }
        pdf = pd.DataFrame(data)
        df = nw.from_native(pdf, eager_only=True).lazy()

        # Act
        code, display = generate_pivot_code(params)

        # Execute generated code
        exec_locals = {"df": df, "nw": nw, "json": json}
        exec(code, {}, exec_locals)
        result_df = exec_locals["df"].collect()

        # Assert all non-index columns are Float64
        for col in result_df.columns:
            if col != "category":
                col_dtype = str(result_df.schema[col])
                assert "Float64" in col_dtype, f"Column {col} is {col_dtype}, expected Float64"
