"""Unit tests for string column detection in search functionality."""

import pytest


class TestStringColumnDetection:
    """Test detection of string/text columns for search."""

    def test_string_column_filter_str(self):
        """Test that 'str' type columns are detected."""
        schema = {
            "name": "Utf8",
            "age": "Int64",
            "city": "Utf8",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert "name" in string_columns
        assert "city" in string_columns
        assert "age" not in string_columns

    def test_string_column_filter_string(self):
        """Test that 'String' type columns are detected."""
        schema = {
            "description": "String",
            "count": "Int32",
            "label": "String",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert "description" in string_columns
        assert "label" in string_columns
        assert "count" not in string_columns

    def test_string_column_filter_object(self):
        """Test that 'Object' type columns are detected."""
        schema = {
            "text": "Object",
            "value": "Float64",
            "notes": "Object",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert "text" in string_columns
        assert "notes" in string_columns
        assert "value" not in string_columns

    def test_string_column_filter_mixed_case(self):
        """Test that mixed case type names are handled."""
        schema = {
            "Name": "UTF8",
            "ID": "Int64",
            "Description": "STRING",
            "Price": "Float32",
            "Category": "oBjEcT",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert "Name" in string_columns
        assert "Description" in string_columns
        assert "Category" in string_columns
        assert "ID" not in string_columns
        assert "Price" not in string_columns

    def test_string_column_filter_no_string_columns(self):
        """Test schema with no string columns."""
        schema = {
            "id": "Int64",
            "age": "Int32",
            "salary": "Float64",
            "active": "Boolean",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert len(string_columns) == 0

    def test_string_column_filter_all_string_columns(self):
        """Test schema with all string columns."""
        schema = {
            "first_name": "Utf8",
            "last_name": "String",
            "address": "Object",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert len(string_columns) == 3
        assert "first_name" in string_columns
        assert "last_name" in string_columns
        assert "address" in string_columns

    def test_string_column_filter_numeric_types(self):
        """Test that numeric types are excluded."""
        schema = {
            "int8_col": "Int8",
            "int16_col": "Int16",
            "int32_col": "Int32",
            "int64_col": "Int64",
            "uint8_col": "UInt8",
            "float32_col": "Float32",
            "float64_col": "Float64",
            "decimal_col": "Decimal",
            "name": "Utf8",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert len(string_columns) == 1
        assert "name" in string_columns

    def test_string_column_filter_special_types(self):
        """Test that special types like Date, Boolean, etc. are excluded."""
        schema = {
            "created_at": "Date",
            "updated_at": "Datetime",
            "is_active": "Boolean",
            "tags": "List",
            "metadata": "Struct",
            "description": "Utf8",
        }

        # Check for string types but exclude "Struct" which contains "str"
        string_columns = [
            col
            for col, dtype in schema.items()
            if (
                any(keyword in dtype.lower() for keyword in ["string", "object", "utf"])
                or ("str" in dtype.lower() and "struct" not in dtype.lower())
            )
        ]

        assert len(string_columns) == 1
        assert "description" in string_columns
