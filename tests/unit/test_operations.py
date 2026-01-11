"""Unit tests for Operation model."""

import pytest
import pandas as pd
import narwhals as nw
from uuid import UUID

from kittiwake.models.operations import Operation, OperationError, OPERATION_TYPES


class TestOperation:
    """Test Operation model functionality."""

    def test_operation_creation(self):
        """Test basic operation creation."""
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        )

        assert op.code == "df = df.filter(nw.col('age') > 25)"
        assert op.display == "Filter: age > 25"
        assert op.operation_type == "filter"
        assert op.params == {"column": "age", "operator": ">", "value": 25}
        assert op.state == "queued"  # Default state
        assert op.error_message is None
        assert isinstance(op.id, UUID)

    def test_operation_with_custom_state(self):
        """Test operation creation with custom state."""
        op = Operation(
            code="df = df.select(['name', 'age'])",
            display="Select: name, age",
            operation_type="select",
            params={"columns": ["name", "age"]},
            state="executed",
        )

        assert op.state == "executed"

    def test_operation_with_error_message(self):
        """Test operation with error message."""
        op = Operation(
            code="df = df.filter(nw.col('invalid') > 0)",
            display="Filter: invalid > 0",
            operation_type="filter",
            params={"column": "invalid", "operator": ">", "value": 0},
            state="failed",
            error_message="Column 'invalid' not found",
        )

        assert op.state == "failed"
        assert op.error_message == "Column 'invalid' not found"

    def test_to_dict(self):
        """Test operation serialization."""
        op = Operation(
            code="df = df.sort('age')",
            display="Sort: age",
            operation_type="sort",
            params={"column": "age", "descending": False},
            state="executed",
        )

        result = op.to_dict()

        assert result["code"] == "df = df.sort('age')"
        assert result["display"] == "Sort: age"
        assert result["operation_type"] == "sort"
        assert result["params"] == {"column": "age", "descending": False}
        assert result["state"] == "executed"

    def test_from_dict(self):
        """Test operation deserialization."""
        data = {
            "code": "df = df.head(10)",
            "display": "Head: 10 rows",
            "operation_type": "head",
            "params": {"n": 10},
        }

        op = Operation.from_dict(data)

        assert op.code == data["code"]
        assert op.display == data["display"]
        assert op.operation_type == data["operation_type"]
        assert op.params == data["params"]
        assert op.state == "queued"  # Default

    def test_to_code(self):
        """Test code generation method."""
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        )

        assert op.to_code() == "df = df.filter(nw.col('age') > 25)"

    def test_apply_filter_operation(self):
        """Test applying a filter operation to a dataframe."""
        # Create sample data
        pdf = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.filter(nw.col('age') > 28)",
            display="Filter: age > 28",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 28},
        )

        result = op.apply(df)
        result_collected = result.collect()

        assert len(result_collected) == 2  # Bob and Charlie
        assert result_collected["age"].to_list() == [30, 35]

    def test_apply_select_operation(self):
        """Test applying a select operation."""
        pdf = pd.DataFrame(
            {"name": ["Alice", "Bob"], "age": [25, 30], "city": ["NYC", "LA"]}
        )
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.select(['name', 'age'])",
            display="Select: name, age",
            operation_type="select",
            params={"columns": ["name", "age"]},
        )

        result = op.apply(df)
        result_collected = result.collect()

        assert list(result_collected.columns) == ["name", "age"]

    def test_apply_sort_operation(self):
        """Test applying a sort operation."""
        pdf = pd.DataFrame({"name": ["Charlie", "Alice", "Bob"], "age": [35, 25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.sort('age')",
            display="Sort: age ascending",
            operation_type="sort",
            params={"column": "age", "descending": False},
        )

        result = op.apply(df)
        result_collected = result.collect()

        assert result_collected["age"].to_list() == [25, 30, 35]

    def test_apply_with_none_dataframe_raises_error(self):
        """Test that applying operation to None dataframe raises error."""
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        )

        with pytest.raises(
            OperationError, match="Cannot apply operation to None dataframe"
        ):
            op.apply(None)

    def test_apply_with_invalid_code_raises_error(self):
        """Test that invalid operation code raises error."""
        pdf = pd.DataFrame({"name": ["Alice"], "age": [25]})
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.invalid_method()",
            display="Invalid operation",
            operation_type="filter",
            params={},
        )

        with pytest.raises(OperationError, match="Failed to apply operation"):
            op.apply(df)

    def test_validate_valid_operation(self):
        """Test validation of a valid operation."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.filter(nw.col('age') > 20)",
            display="Filter: age > 20",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 20},
        )

        is_valid, error = op.validate(df)

        assert is_valid is True
        assert error is None

    def test_validate_invalid_operation(self):
        """Test validation of an invalid operation."""
        pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        df = nw.from_native(pdf, eager_only=True).lazy()

        op = Operation(
            code="df = df.filter(nw.col('invalid_column') > 20)",
            display="Filter: invalid_column > 20",
            operation_type="filter",
            params={"column": "invalid_column", "operator": ">", "value": 20},
        )

        is_valid, error = op.validate(df)

        assert is_valid is False
        assert error is not None
        assert "invalid_column" in error.lower() or "not found" in error.lower()

    def test_validate_with_none_dataframe(self):
        """Test validation with None dataframe."""
        op = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter: age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        )

        is_valid, error = op.validate(None)

        assert is_valid is False
        assert error == "Dataframe is None"

    def test_operation_types_constant(self):
        """Test that OPERATION_TYPES constant is defined."""
        assert isinstance(OPERATION_TYPES, list)
        assert len(OPERATION_TYPES) > 0
        assert "filter" in OPERATION_TYPES
        assert "select" in OPERATION_TYPES
        assert "sort" in OPERATION_TYPES

    def test_unique_operation_ids(self):
        """Test that each operation gets a unique ID."""
        op1 = Operation(
            code="df = df.filter(nw.col('age') > 25)",
            display="Filter 1",
            operation_type="filter",
            params={},
        )
        op2 = Operation(
            code="df = df.filter(nw.col('age') > 30)",
            display="Filter 2",
            operation_type="filter",
            params={},
        )

        assert op1.id != op2.id

    def test_operation_state_transitions(self):
        """Test operation state can be changed."""
        op = Operation(
            code="df = df.select(['name'])",
            display="Select: name",
            operation_type="select",
            params={"columns": ["name"]},
        )

        assert op.state == "queued"

        op.state = "executed"
        assert op.state == "executed"

        op.state = "failed"
        op.error_message = "Test error"
        assert op.state == "failed"
        assert op.error_message == "Test error"
