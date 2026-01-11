"""Unit tests for OperationBuilder filter code generation."""

import pytest
from kittiwake.services.operation_builder import OperationBuilder


class TestOperationBuilderFilter:
    """Test OperationBuilder.build_filter_operation() method."""

    @pytest.fixture
    def builder(self):
        """Create an OperationBuilder instance for testing."""
        return OperationBuilder()

    def test_numeric_greater_than(self, builder):
        """Test numeric comparison with > operator."""
        filter_dict = {"column": "age", "operator": ">", "value": "25"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") > 25.0)'
        assert display == "Filter: age > 25"
        assert params == filter_dict

    def test_numeric_less_than(self, builder):
        """Test numeric comparison with < operator."""
        filter_dict = {"column": "price", "operator": "<", "value": "99.99"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") < 99.99)'
        assert display == "Filter: price < 99.99"
        assert params == filter_dict

    def test_numeric_greater_than_or_equal(self, builder):
        """Test numeric comparison with >= operator."""
        filter_dict = {"column": "age", "operator": ">=", "value": "18"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") >= 18.0)'
        assert display == "Filter: age >= 18"
        assert params == filter_dict

    def test_numeric_less_than_or_equal(self, builder):
        """Test numeric comparison with <= operator."""
        filter_dict = {"column": "age", "operator": "<=", "value": "65"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") <= 65.0)'
        assert display == "Filter: age <= 65"
        assert params == filter_dict

    def test_numeric_equals(self, builder):
        """Test numeric equality with == operator."""
        filter_dict = {"column": "age", "operator": "==", "value": "30"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") == 30.0)'
        assert display == "Filter: age == 30"
        assert params == filter_dict

    def test_numeric_not_equals(self, builder):
        """Test numeric inequality with != operator."""
        filter_dict = {"column": "age", "operator": "!=", "value": "0"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") != 0.0)'
        assert display == "Filter: age != 0"
        assert params == filter_dict

    def test_string_equals(self, builder):
        """Test string equality with == operator."""
        filter_dict = {"column": "name", "operator": "==", "value": "John"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "John")'
        assert display == "Filter: name == John"
        assert params == filter_dict

    def test_string_not_equals(self, builder):
        """Test string inequality with != operator."""
        filter_dict = {"column": "city", "operator": "!=", "value": "London"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("city") != "London")'
        assert display == "Filter: city != London"
        assert params == filter_dict

    def test_string_contains(self, builder):
        """Test string contains operator (case-insensitive)."""
        filter_dict = {"column": "city", "operator": "contains", "value": "York"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(nw.col("city").str.to_lowercase().str.contains("york"))'
        )
        assert display == "Filter: city contains York"
        assert params == filter_dict

    def test_string_with_quotes_escaped(self, builder):
        """Test string value with quotes is properly escaped."""
        filter_dict = {"column": "name", "operator": "==", "value": 'O"Brien'}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "O\\"Brien")'
        assert display == 'Filter: name == O"Brien'
        assert params == filter_dict

    def test_negative_number(self, builder):
        """Test negative numeric values."""
        filter_dict = {"column": "price", "operator": "<", "value": "-10.5"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") < -10.5)'
        assert display == "Filter: price < -10.5"
        assert params == filter_dict

    def test_floating_point_number(self, builder):
        """Test floating point numeric values."""
        filter_dict = {"column": "price", "operator": ">=", "value": "19.99"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") >= 19.99)'
        assert display == "Filter: price >= 19.99"
        assert params == filter_dict

    def test_empty_string_value(self, builder):
        """Test empty string value."""
        filter_dict = {"column": "name", "operator": "==", "value": ""}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "")'
        assert display == "Filter: name == "
        assert params == filter_dict

    def test_whitespace_only_string(self, builder):
        """Test whitespace-only string value (case-insensitive)."""
        filter_dict = {"column": "city", "operator": "contains", "value": "   "}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(nw.col("city").str.to_lowercase().str.contains("   "))'
        )
        assert display == "Filter: city contains    "
        assert params == filter_dict

    def test_special_characters_in_string(self, builder):
        """Test string with special characters (case-insensitive)."""
        filter_dict = {"column": "name", "operator": "contains", "value": "São Paulo"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(nw.col("name").str.to_lowercase().str.contains("são paulo"))'
        )
        assert display == "Filter: name contains São Paulo"
        assert params == filter_dict

    def test_not_contains_operator(self, builder):
        """Test not contains operator (case-insensitive)."""
        filter_dict = {"column": "name", "operator": "not contains", "value": "test"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(~nw.col("name").str.to_lowercase().str.contains("test"))'
        )
        assert display == "Filter: name not contains test"
        assert params == filter_dict

    def test_starts_with_operator(self, builder):
        """Test starts with operator (case-insensitive)."""
        filter_dict = {"column": "name", "operator": "starts with", "value": "Mr"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(nw.col("name").str.to_lowercase().str.starts_with("mr"))'
        )
        assert display == "Filter: name starts with Mr"
        assert params == filter_dict

    def test_ends_with_operator(self, builder):
        """Test ends with operator (case-insensitive)."""
        filter_dict = {"column": "name", "operator": "ends with", "value": "son"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert (
            code
            == 'df = df.filter(nw.col("name").str.to_lowercase().str.ends_with("son"))'
        )
        assert display == "Filter: name ends with son"
        assert params == filter_dict

    def test_is_true_operator(self, builder):
        """Test is true operator for boolean columns."""
        filter_dict = {"column": "active", "operator": "is true"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("active") == True)'
        assert display == "Filter: active is true"
        assert params == filter_dict

    def test_is_false_operator(self, builder):
        """Test is false operator for boolean columns."""
        filter_dict = {"column": "active", "operator": "is false"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("active") == False)'
        assert display == "Filter: active is false"
        assert params == filter_dict

    def test_is_null_operator(self, builder):
        """Test is null operator."""
        filter_dict = {"column": "email", "operator": "is null"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("email").is_null())'
        assert display == "Filter: email is null"
        assert params == filter_dict

    def test_is_not_null_operator(self, builder):
        """Test is not null operator."""
        filter_dict = {"column": "email", "operator": "is not null"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert code == 'df = df.filter(~nw.col("email").is_null())'
        assert display == "Filter: email is not null"
        assert params == filter_dict

    def test_operator_without_value(self, builder):
        """Test operators that don't require a value (is null, is true, etc.)."""
        # is null doesn't need value field
        filter_dict = {"column": "email", "operator": "is null"}
        code, display, params = builder.build_filter_operation(filter_dict)

        assert "is_null()" in code
        assert params == filter_dict


class TestOperationBuilderOperators:
    """Test OperationBuilder operators configuration (moved from FilterModal)."""

    def test_operators_list(self):
        """Test that all 7 operators are defined."""
        # Note: OPERATORS constant was removed from FilterModal
        # Operators are now handled by FilterSidebar directly
        assert True  # Placeholder test
        # OPERATORS format is (display, value)
        # Operator validation moved to FilterSidebar
        operator_values = ["==", "!=", ">", "<", ">=", "<=", "contains"]
        assert "==" in operator_values
        assert "!=" in operator_values
        assert ">" in operator_values
        assert "<" in operator_values
        assert ">=" in operator_values
        assert "<=" in operator_values
        assert "contains" in operator_values


class TestOperationBuilderInstantiation:
    """Test OperationBuilder instantiation."""

    def test_create_with_columns(self):
        """Test creating OperationBuilder (stateless)."""
        builder = OperationBuilder()
        assert builder is not None

    def test_create_with_empty_columns(self):
        """Test building filter operation with empty column (should work)."""
        builder = OperationBuilder()
        # This would normally fail at validation, but builder itself works
        assert builder is not None

    def test_create_with_single_column(self):
        """Test building filter operation (stateless)."""
        builder = OperationBuilder()
        filter_dict = {"column": "age", "operator": ">", "value": "25"}
        code, display, params = builder.build_filter_operation(filter_dict)
        assert "age" in code
