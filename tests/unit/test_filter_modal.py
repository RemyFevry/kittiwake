"""Unit tests for FilterModal widget and filter code generation."""

import pytest
from kittiwake.widgets.modals.filter_modal import FilterModal


class TestFilterModalBuildOperation:
    """Test FilterModal._build_filter_operation() method."""

    @pytest.fixture
    def filter_modal(self):
        """Create a FilterModal instance for testing."""
        return FilterModal(columns=["age", "name", "city", "price"])

    def test_numeric_greater_than(self, filter_modal):
        """Test numeric comparison with > operator."""
        filter_dict = {"column": "age", "operator": ">", "value": "25"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") > 25.0)'
        assert display == "Filter: age > 25"
        assert params == filter_dict

    def test_numeric_less_than(self, filter_modal):
        """Test numeric comparison with < operator."""
        filter_dict = {"column": "price", "operator": "<", "value": "99.99"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") < 99.99)'
        assert display == "Filter: price < 99.99"
        assert params == filter_dict

    def test_numeric_greater_than_or_equal(self, filter_modal):
        """Test numeric comparison with >= operator."""
        filter_dict = {"column": "age", "operator": ">=", "value": "18"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") >= 18.0)'
        assert display == "Filter: age >= 18"
        assert params == filter_dict

    def test_numeric_less_than_or_equal(self, filter_modal):
        """Test numeric comparison with <= operator."""
        filter_dict = {"column": "age", "operator": "<=", "value": "65"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") <= 65.0)'
        assert display == "Filter: age <= 65"
        assert params == filter_dict

    def test_numeric_equals(self, filter_modal):
        """Test numeric equality with == operator."""
        filter_dict = {"column": "age", "operator": "==", "value": "30"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") == 30.0)'
        assert display == "Filter: age == 30"
        assert params == filter_dict

    def test_numeric_not_equals(self, filter_modal):
        """Test numeric inequality with != operator."""
        filter_dict = {"column": "age", "operator": "!=", "value": "0"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("age") != 0.0)'
        assert display == "Filter: age != 0"
        assert params == filter_dict

    def test_string_equals(self, filter_modal):
        """Test string equality with == operator."""
        filter_dict = {"column": "name", "operator": "==", "value": "John"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "John")'
        assert display == "Filter: name == John"
        assert params == filter_dict

    def test_string_not_equals(self, filter_modal):
        """Test string inequality with != operator."""
        filter_dict = {"column": "city", "operator": "!=", "value": "London"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("city") != "London")'
        assert display == "Filter: city != London"
        assert params == filter_dict

    def test_string_contains(self, filter_modal):
        """Test string contains operator (case-insensitive)."""
        filter_dict = {"column": "city", "operator": "contains", "value": "York"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("city").str.to_lowercase().str.contains("york"))'
        assert display == "Filter: city contains York"
        assert params == filter_dict

    def test_string_with_quotes_escaped(self, filter_modal):
        """Test string value with quotes is properly escaped."""
        filter_dict = {"column": "name", "operator": "==", "value": 'O"Brien'}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "O\\"Brien")'
        assert display == 'Filter: name == O"Brien'
        assert params == filter_dict

    def test_negative_number(self, filter_modal):
        """Test negative numeric values."""
        filter_dict = {"column": "price", "operator": "<", "value": "-10.5"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") < -10.5)'
        assert display == "Filter: price < -10.5"
        assert params == filter_dict

    def test_floating_point_number(self, filter_modal):
        """Test floating point numeric values."""
        filter_dict = {"column": "price", "operator": ">=", "value": "19.99"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("price") >= 19.99)'
        assert display == "Filter: price >= 19.99"
        assert params == filter_dict

    def test_empty_string_value(self, filter_modal):
        """Test empty string value."""
        filter_dict = {"column": "name", "operator": "==", "value": ""}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name") == "")'
        assert display == "Filter: name == "
        assert params == filter_dict

    def test_whitespace_only_string(self, filter_modal):
        """Test whitespace-only string value (case-insensitive)."""
        filter_dict = {"column": "city", "operator": "contains", "value": "   "}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("city").str.to_lowercase().str.contains("   "))'
        assert display == "Filter: city contains    "
        assert params == filter_dict

    def test_special_characters_in_string(self, filter_modal):
        """Test string with special characters (case-insensitive)."""
        filter_dict = {"column": "name", "operator": "contains", "value": "São Paulo"}
        code, display, params = filter_modal._build_filter_operation(filter_dict)

        assert code == 'df = df.filter(nw.col("name").str.to_lowercase().str.contains("são paulo"))'
        assert display == "Filter: name contains São Paulo"
        assert params == filter_dict


class TestFilterModalOperators:
    """Test FilterModal operators configuration."""

    def test_operators_list(self):
        """Test that all 7 operators are defined."""
        assert len(FilterModal.OPERATORS) == 7
        # OPERATORS format is (display, value)
        operator_values = [op[1] for op in FilterModal.OPERATORS]
        assert "==" in operator_values
        assert "!=" in operator_values
        assert ">" in operator_values
        assert "<" in operator_values
        assert ">=" in operator_values
        assert "<=" in operator_values
        assert "contains" in operator_values


class TestFilterModalInstantiation:
    """Test FilterModal widget instantiation."""

    def test_create_with_columns(self):
        """Test creating FilterModal with column list."""
        columns = ["age", "name", "city"]
        modal = FilterModal(columns=columns)
        assert modal.columns == columns

    def test_create_with_empty_columns(self):
        """Test creating FilterModal with empty column list."""
        modal = FilterModal(columns=[])
        assert modal.columns == []

    def test_create_with_single_column(self):
        """Test creating FilterModal with single column."""
        modal = FilterModal(columns=["age"])
        assert modal.columns == ["age"]
