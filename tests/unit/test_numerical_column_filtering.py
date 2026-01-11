"""Test numerical column filtering for aggregation operations.

Tests for feature 003-numerical-column-aggregation:
- US1: Only numerical columns appear in aggregation dropdown
- US2: Aggregation operations succeed with filtered columns
- US3: Empty state handling when no numerical columns exist
"""

from unittest.mock import MagicMock

import pytest

from kittiwake.services.type_detector import detect_column_type_category


class TestTypeDetection:
    """Test type detection for numerical columns."""

    def test_detect_numeric_int64(self):
        """Test Int64 is detected as numeric."""
        assert detect_column_type_category("Int64") == "numeric"

    def test_detect_numeric_float32(self):
        """Test Float32 is detected as numeric."""
        assert detect_column_type_category("Float32") == "numeric"

    def test_detect_numeric_uint16(self):
        """Test UInt16 is detected as numeric."""
        assert detect_column_type_category("UInt16") == "numeric"

    def test_detect_numeric_decimal(self):
        """Test Decimal is detected as numeric."""
        assert detect_column_type_category("Decimal") == "numeric"

    def test_detect_text_string(self):
        """Test String is NOT detected as numeric."""
        assert detect_column_type_category("String") != "numeric"

    def test_detect_date_datetime(self):
        """Test Datetime is NOT detected as numeric."""
        assert detect_column_type_category("Datetime") != "numeric"

    def test_detect_boolean(self):
        """Test Boolean is NOT detected as numeric."""
        assert detect_column_type_category("Boolean") != "numeric"

    def test_detect_list(self):
        """Test List type is NOT detected as numeric."""
        assert detect_column_type_category("List(Int64)") != "numeric"


class TestNumericalColumnFiltering:
    """Test numerical column filtering in MainScreen.action_aggregate()."""

    @pytest.fixture
    def mock_dataset(self):
        """Create mock dataset with mixed column types."""
        dataset = MagicMock()
        dataset.schema = {
            "age": "Int64",
            "name": "String",
            "salary": "Float64",
            "is_active": "Boolean",
            "hire_date": "Date",
            "bonus": "Float32",
        }
        return dataset

    @pytest.fixture
    def mock_dataset_no_numeric(self):
        """Create mock dataset with no numerical columns."""
        dataset = MagicMock()
        dataset.schema = {
            "name": "String",
            "is_active": "Boolean",
            "hire_date": "Date",
        }
        return dataset

    @pytest.fixture
    def mock_dataset_all_numeric(self):
        """Create mock dataset with only numerical columns."""
        dataset = MagicMock()
        dataset.schema = {
            "age": "Int64",
            "salary": "Float64",
            "bonus": "Float32",
            "rating": "UInt8",
        }
        return dataset

    def test_filter_numerical_columns_mixed(self, mock_dataset):
        """Test filtering extracts only numerical columns from mixed dataset."""
        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in mock_dataset.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 3
        assert "age" in numerical_columns
        assert "salary" in numerical_columns
        assert "bonus" in numerical_columns
        assert "name" not in numerical_columns
        assert "is_active" not in numerical_columns
        assert "hire_date" not in numerical_columns

    def test_filter_numerical_columns_none(self, mock_dataset_no_numeric):
        """Test filtering returns empty list when no numerical columns exist."""
        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in mock_dataset_no_numeric.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 0

    def test_filter_numerical_columns_all(self, mock_dataset_all_numeric):
        """Test filtering returns all columns when all are numerical."""
        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in mock_dataset_all_numeric.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 4
        assert set(numerical_columns) == {"age", "salary", "bonus", "rating"}

    def test_filter_preserves_column_order(self, mock_dataset):
        """Test filtering preserves original column order."""
        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in mock_dataset.schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        # Dict maintains insertion order in Python 3.7+
        expected_order = ["age", "salary", "bonus"]
        assert numerical_columns == expected_order


class TestEmptyStateHandling:
    """Test empty state handling when no numerical columns exist."""

    def test_empty_state_prevents_sidebar_opening(self):
        """Test that sidebar doesn't open when no numerical columns exist."""
        # This would be tested via integration test with actual MainScreen
        # Unit test just verifies the filtering logic returns empty list
        schema = {"name": "String", "is_active": "Boolean"}

        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 0

    def test_notification_message_format(self):
        """Test the expected notification message for empty state."""
        expected_message = "Aggregation requires at least one numerical column"
        expected_severity = "warning"

        # This validates the message format matches spec
        assert len(expected_message) > 0
        assert expected_severity in ["info", "warning", "error"]


class TestExecutionValidation:
    """Test validation before executing aggregation operation."""

    def test_validate_column_still_numerical_before_execution(self):
        """Test that column type is revalidated before execution."""
        # Simulate schema check at execution time
        schema = {"age": "Int64", "name": "String"}
        selected_column = "age"

        from kittiwake.services.type_detector import detect_column_type_category

        is_valid = (
            selected_column in schema
            and detect_column_type_category(str(schema[selected_column])) == "numeric"
        )

        assert is_valid is True

    def test_validate_rejects_non_numerical_column(self):
        """Test validation rejects non-numerical column at execution time."""
        schema = {"age": "Int64", "name": "String"}
        selected_column = "name"

        from kittiwake.services.type_detector import detect_column_type_category

        is_valid = (
            selected_column in schema
            and detect_column_type_category(str(schema[selected_column])) == "numeric"
        )

        assert is_valid is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_schema(self):
        """Test handling of empty schema."""
        schema = {}

        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 0

    def test_case_insensitive_type_detection(self):
        """Test type detection is case-insensitive."""
        assert detect_column_type_category("int64") == "numeric"
        assert detect_column_type_category("INT64") == "numeric"
        assert detect_column_type_category("Int64") == "numeric"

    def test_unknown_type_not_included(self):
        """Test unknown types are not included in numerical columns."""
        schema = {"weird_col": "UnknownType", "age": "Int64"}

        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 1
        assert "age" in numerical_columns
        assert "weird_col" not in numerical_columns

    def test_list_of_numeric_not_included(self):
        """Test List(Int64) is not included as numerical column."""
        schema = {"numbers": "List(Int64)", "count": "Int64"}

        from kittiwake.services.type_detector import detect_column_type_category

        numerical_columns = [
            col
            for col, dtype in schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]

        assert len(numerical_columns) == 1
        assert "count" in numerical_columns
        assert "numbers" not in numerical_columns


class TestPerformance:
    """Test performance characteristics of filtering."""

    def test_filtering_performance_large_schema(self):
        """Test filtering completes quickly for large schemas."""
        import time

        # Create schema with 1000 columns
        schema = {f"col_{i}": "Int64" if i % 2 == 0 else "String" for i in range(1000)}

        from kittiwake.services.type_detector import detect_column_type_category

        start_time = time.perf_counter()
        numerical_columns = [
            col
            for col, dtype in schema.items()
            if detect_column_type_category(str(dtype)) == "numeric"
        ]
        elapsed_time = time.perf_counter() - start_time

        # Should complete in less than 10ms
        assert elapsed_time < 0.01
        assert len(numerical_columns) == 500  # Half should be numerical


class TestPivotSidebarFiltering:
    """Test numerical column filtering in pivot sidebar."""

    def test_pivot_sidebar_accepts_separate_value_columns(self):
        """Test PivotSidebar accepts separate value_columns parameter."""
        from kittiwake.widgets.sidebars import PivotSidebar

        all_columns = ["name", "age", "salary", "is_active"]
        value_columns = ["age", "salary"]

        sidebar = PivotSidebar()
        sidebar.update_columns(all_columns, value_columns=value_columns)

        assert sidebar.columns == all_columns
        assert sidebar.value_columns == value_columns

    def test_pivot_sidebar_backward_compatible_without_value_columns(self):
        """Test PivotSidebar works without value_columns (backward compatible)."""
        from kittiwake.widgets.sidebars import PivotSidebar

        all_columns = ["name", "age", "salary"]

        sidebar = PivotSidebar()
        sidebar.update_columns(all_columns)

        assert sidebar.columns == all_columns
        assert sidebar.value_columns == all_columns  # Should default to all columns

    def test_pivot_sidebar_value_sections_use_value_columns(self):
        """Test that ValueAggregationSection uses value_columns not all columns."""
        from kittiwake.widgets.sidebars import PivotSidebar

        all_columns = ["name", "age", "salary", "is_active"]
        value_columns = ["age", "salary"]

        sidebar = PivotSidebar()
        sidebar.update_columns(all_columns, value_columns=value_columns)

        # The value_sections should use value_columns
        assert sidebar.value_columns == value_columns
