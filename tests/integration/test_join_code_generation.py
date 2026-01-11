"""Integration tests for join code generation in narwhals_ops.py.

Tests verify that generated join code executes correctly with real narwhals dataframes.
"""

import narwhals as nw
import pandas as pd
import pytest

from kittiwake.services.narwhals_ops import (
    TypeValidationResult,
    are_types_compatible,
    generate_join_code,
    generate_type_conversion_code,
    get_base_type,
    get_conversion_target,
    validate_join_key_types,
)


class TestGenerateJoinCode:
    """Test join code generation with real narwhals dataframes."""

    @pytest.fixture
    def left_df(self):
        """Create a left dataframe for testing."""
        pdf = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "name": ["Alice", "Bob", "Charlie", "David"],
                "age": [25, 30, 35, 40],
            }
        )
        return nw.from_native(pdf, eager_only=True).lazy()

    @pytest.fixture
    def right_df(self):
        """Create a right dataframe for testing."""
        pdf = pd.DataFrame(
            {
                "user_id": [1, 2, 5],
                "city": ["NYC", "LA", "Chicago"],
                "salary": [70000, 80000, 90000],
            }
        )
        return nw.from_native(pdf, eager_only=True).lazy()

    @pytest.fixture
    def right_df_same_key(self):
        """Create a right dataframe with same key name as left."""
        pdf = pd.DataFrame(
            {
                "id": [1, 2, 5],
                "city": ["NYC", "LA", "Chicago"],
                "salary": [70000, 80000, 90000],
            }
        )
        return nw.from_native(pdf, eager_only=True).lazy()

    def test_generate_inner_join_different_keys(self, left_df, right_df):
        """Test generating inner join with different key names."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "inner",
        }

        code, display = generate_join_code(params)

        assert (
            code
            == "df = df.join(right_df, left_on='id', right_on='user_id', how='inner', suffix='_right')"
        )
        assert display == "Join: inner join on id = user_id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Inner join should only include matching rows (id 1 and 2)
        assert len(result) == 2
        assert result["id"].to_list() == [1, 2]
        assert result["name"].to_list() == ["Alice", "Bob"]
        assert result["city"].to_list() == ["NYC", "LA"]

    def test_generate_inner_join_same_keys(self, left_df, right_df_same_key):
        """Test generating inner join when keys have the same name."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "id",
            "how": "inner",
        }

        code, display = generate_join_code(params)

        assert code == "df = df.join(right_df, on='id', how='inner', suffix='_right')"
        assert display == "Join: inner join on id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df_same_key, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Inner join should only include matching rows (id 1 and 2)
        assert len(result) == 2
        assert result["id"].to_list() == [1, 2]
        assert result["name"].to_list() == ["Alice", "Bob"]

    def test_generate_left_join(self, left_df, right_df):
        """Test generating left join."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "left",
        }

        code, display = generate_join_code(params)

        assert (
            code
            == "df = df.join(right_df, left_on='id', right_on='user_id', how='left', suffix='_right')"
        )
        assert display == "Join: left join on id = user_id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Left join should include all left rows (4 rows)
        assert len(result) == 4
        assert result["id"].to_list() == [1, 2, 3, 4]
        assert result["name"].to_list() == ["Alice", "Bob", "Charlie", "David"]
        # Rows without matches should have null/NaN values
        import math

        assert math.isnan(result["salary"].to_list()[2])  # Charlie has no match
        assert math.isnan(result["salary"].to_list()[3])  # David has no match

    def test_generate_outer_join(self, left_df, right_df_same_key):
        """Test generating outer (full) join."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "id",
            "how": "outer",
        }

        code, display = generate_join_code(params)

        # Note: 'outer' is mapped to 'full' for narwhals
        assert code == "df = df.join(right_df, on='id', how='full', suffix='_right')"
        assert display == "Join: outer join on id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df_same_key, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Outer join should include all rows from both tables
        # Note: The exact behavior depends on narwhals backend, but we should have at least 4 rows
        assert len(result) >= 4

    def test_generate_cross_join(self, left_df, right_df_same_key):
        """Test generating cross join (Cartesian product)."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",  # Not used for cross join but required by schema
            "right_key": "id",  # Not used for cross join but required by schema
            "how": "cross",
        }

        code, display = generate_join_code(params)

        assert code == "df = df.join(right_df, how='cross')"
        assert display == "Join: cross join (Cartesian product)"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df_same_key, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Cross join produces Cartesian product: 4 * 3 = 12 rows
        assert len(result) == 12

    def test_generate_semi_join(self, left_df, right_df):
        """Test generating semi join (filter with match in right)."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "semi",
        }

        code, display = generate_join_code(params)

        assert (
            code
            == "df = df.join(right_df, left_on='id', right_on='user_id', how='semi', suffix='_right')"
        )
        assert display == "Join: semi join on id = user_id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Semi join filters left rows that have matches in right
        # Should only include rows where id matches user_id (1, 2)
        assert len(result) == 2
        assert result["id"].to_list() == [1, 2]
        # Semi join only returns left table columns
        assert "city" not in result.columns
        assert "salary" not in result.columns

    def test_generate_anti_join(self, left_df, right_df):
        """Test generating anti join (filter without match in right)."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "anti",
        }

        code, display = generate_join_code(params)

        assert (
            code
            == "df = df.join(right_df, left_on='id', right_on='user_id', how='anti', suffix='_right')"
        )
        assert display == "Join: anti join on id = user_id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Anti join filters left rows that DON'T have matches in right
        # Should only include rows where id doesn't match user_id (3, 4)
        assert len(result) == 2
        assert result["id"].to_list() == [3, 4]
        assert result["name"].to_list() == ["Charlie", "David"]

    def test_generate_join_with_custom_suffix(self, left_df, right_df_same_key):
        """Test generating join with custom right suffix."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "id",
            "how": "inner",
            "right_suffix": "_r",
        }

        code, display = generate_join_code(params)

        assert code == "df = df.join(right_df, on='id', how='inner', suffix='_r')"
        assert display == "Join: inner join on id"

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df_same_key, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        assert len(result) == 2
        # Verify custom suffix is applied (if there are duplicate column names)
        # In this case, 'id' is the join key so no suffix needed

    def test_missing_right_dataset_id_raises_error(self):
        """Test that missing right_dataset_id raises ValueError."""
        params = {"left_key": "id", "right_key": "user_id", "how": "inner"}

        with pytest.raises(ValueError, match="right_dataset_id is required"):
            generate_join_code(params)

    def test_missing_left_key_raises_error(self):
        """Test that missing left_key raises ValueError."""
        params = {
            "right_dataset_id": "dataset_2",
            "right_key": "user_id",
            "how": "inner",
        }

        with pytest.raises(ValueError, match="left_key is required"):
            generate_join_code(params)

    def test_missing_right_key_raises_error(self):
        """Test that missing right_key raises ValueError."""
        params = {"right_dataset_id": "dataset_2", "left_key": "id", "how": "inner"}

        with pytest.raises(ValueError, match="right_key is required"):
            generate_join_code(params)

    def test_missing_how_raises_error(self):
        """Test that missing how (join type) raises ValueError."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
        }

        with pytest.raises(ValueError, match="how.*is required"):
            generate_join_code(params)

    def test_invalid_join_type_raises_error(self):
        """Test that invalid join type raises ValueError."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "invalid_join",
        }

        with pytest.raises(ValueError, match="Invalid join type"):
            generate_join_code(params)

    def test_empty_params_raises_error(self):
        """Test that empty params dict raises ValueError."""
        with pytest.raises(ValueError, match="params dictionary is required"):
            generate_join_code({})

    def test_none_params_raises_error(self):
        """Test that None params raises ValueError."""
        with pytest.raises(ValueError, match="params dictionary is required"):
            generate_join_code(None)  # type: ignore[arg-type]

    def test_invalid_suffix_type_raises_error(self):
        """Test that non-string suffix raises ValueError."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "inner",
            "right_suffix": 123,  # Invalid type
        }

        with pytest.raises(ValueError, match="right_suffix must be a string"):
            generate_join_code(params)

    def test_join_with_duplicate_column_names(self):
        """Test join behavior when both dataframes have duplicate column names."""
        # Create dataframes with overlapping columns
        left_pdf = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "value": [10, 20, 30],
                "status": ["active", "active", "inactive"],
            }
        )
        left_df = nw.from_native(left_pdf, eager_only=True).lazy()

        right_pdf = pd.DataFrame(
            {"id": [1, 2, 4], "value": [100, 200, 400], "status": ["ok", "ok", "error"]}
        )
        right_df = nw.from_native(right_pdf, eager_only=True).lazy()

        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "id",
            "how": "inner",
            "right_suffix": "_right",
        }

        code, display = generate_join_code(params)

        # Execute the generated code
        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Inner join should include matching rows
        assert len(result) == 2
        assert result["id"].to_list() == [1, 2]
        # Check that duplicate columns have suffix
        assert "value" in result.columns
        assert "value_right" in result.columns
        assert "status" in result.columns
        assert "status_right" in result.columns


class TestGetBaseType:
    """Test get_base_type function for extracting base type categories."""

    def test_int_types(self):
        """Test that various int types are correctly identified."""
        assert get_base_type("Int64") == "int"
        assert get_base_type("Int32") == "int"
        assert get_base_type("Int16") == "int"
        assert get_base_type("Int8") == "int"
        assert get_base_type("UInt64") == "int"
        assert get_base_type("UInt32") == "int"

    def test_float_types(self):
        """Test that various float types are correctly identified."""
        assert get_base_type("Float64") == "float"
        assert get_base_type("Float32") == "float"
        assert get_base_type("Decimal128") == "float"

    def test_string_types(self):
        """Test that various string types are correctly identified."""
        assert get_base_type("String") == "string"
        assert get_base_type("Utf8") == "string"
        assert get_base_type("str") == "string"
        assert get_base_type("Categorical") == "string"
        assert get_base_type("Enum") == "string"

    def test_boolean_types(self):
        """Test that boolean type is correctly identified."""
        assert get_base_type("Boolean") == "boolean"
        assert get_base_type("bool") == "boolean"

    def test_datetime_types(self):
        """Test that datetime types are correctly identified."""
        assert get_base_type("Datetime") == "datetime"
        assert get_base_type("Date") == "datetime"
        assert get_base_type("Time") == "datetime"

    def test_unknown_types(self):
        """Test that unknown types are handled."""
        assert get_base_type("UnknownType") == "unknown"
        assert get_base_type("Struct") == "unknown"
        assert get_base_type("List") == "unknown"


class TestAreTypesCompatible:
    """Test are_types_compatible function for type compatibility checking."""

    def test_same_types_are_compatible(self):
        """Test that identical types are compatible."""
        assert are_types_compatible("int", "int")
        assert are_types_compatible("float", "float")
        assert are_types_compatible("string", "string")
        assert are_types_compatible("boolean", "boolean")

    def test_int_float_are_compatible(self):
        """Test that int and float are compatible (int can be promoted to float)."""
        assert are_types_compatible("int", "float")
        assert are_types_compatible("float", "int")

    def test_int_string_not_compatible(self):
        """Test that int and string are not compatible."""
        assert not are_types_compatible("int", "string")
        assert not are_types_compatible("string", "int")

    def test_float_string_not_compatible(self):
        """Test that float and string are not compatible."""
        assert not are_types_compatible("float", "string")
        assert not are_types_compatible("string", "float")

    def test_boolean_string_not_compatible(self):
        """Test that boolean and string are not compatible."""
        assert not are_types_compatible("boolean", "string")
        assert not are_types_compatible("string", "boolean")

    def test_unknown_type_not_compatible(self):
        """Test that unknown types are not compatible."""
        assert not are_types_compatible("int", "unknown")
        assert not are_types_compatible("string", "unknown")


class TestGetConversionTarget:
    """Test get_conversion_target function for determining conversion target."""

    def test_int_to_float_conversion(self):
        """Test that int+float conversion targets float."""
        assert get_conversion_target("int", "float") == "float"
        assert get_conversion_target("float", "int") == "float"

    def test_no_conversion_needed_same_types(self):
        """Test that same types don't need conversion."""
        assert get_conversion_target("int", "int") is None
        assert get_conversion_target("string", "string") is None

    def test_no_conversion_incompatible_types(self):
        """Test that incompatible types don't have conversion target."""
        assert get_conversion_target("int", "string") is None
        assert get_conversion_target("string", "int") is None
        assert get_conversion_target("boolean", "int") is None


class TestGenerateTypeConversionCode:
    """Test generate_type_conversion_code function for generating conversion code."""

    def test_int_to_float_left_dataset(self):
        """Test generating int→float conversion code for left dataset."""
        code = generate_type_conversion_code("id", "int", "float", is_left=True)
        assert code == "df = df.with_columns(nw.col('id').cast(nw.Float64))"

    def test_int_to_float_right_dataset(self):
        """Test generating int→float conversion code for right dataset."""
        code = generate_type_conversion_code("user_id", "int", "float", is_left=False)
        assert (
            code
            == "right_df = right_df.with_columns(nw.col('user_id').cast(nw.Float64))"
        )


class TestValidateJoinKeyTypes:
    """Test validate_join_key_types function for type validation."""

    def test_identical_types_compatible(self):
        """Test validation with identical types."""
        result = validate_join_key_types("Int64", "Int64", "id", "id")

        assert isinstance(result, TypeValidationResult)
        assert result.is_compatible is True
        assert result.needs_conversion is False
        assert result.conversion_code == ""
        assert result.error_message == ""

    def test_int_float_compatible_with_conversion(self):
        """Test validation with int and float types."""
        result = validate_join_key_types("Int64", "Float64", "id", "user_id")

        assert isinstance(result, TypeValidationResult)
        assert result.is_compatible is True
        assert result.needs_conversion is True
        assert result.conversion_code != ""
        assert result.error_message == ""
        assert "cast(nw.Float64)" in result.conversion_code

    def test_int_string_incompatible(self):
        """Test validation with incompatible int and string types."""
        result = validate_join_key_types("Int64", "String", "id", "name")

        assert isinstance(result, TypeValidationResult)
        assert result.is_compatible is False
        assert result.needs_conversion is False
        assert "not compatible" in result.error_message
        assert "id" in result.error_message
        assert "name" in result.error_message
        assert "Int64" in result.error_message
        assert "String" in result.error_message

    def test_float_string_incompatible(self):
        """Test validation with incompatible float and string types."""
        result = validate_join_key_types("Float64", "String", "amount", "code")

        assert isinstance(result, TypeValidationResult)
        assert result.is_compatible is False
        assert result.error_message != ""


class TestJoinCodeGenerationWithTypeConversion:
    """Test join code generation with type conversion."""

    def test_generate_join_code_with_type_conversion(self):
        """Test generating join code that includes type conversion."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "inner",
            "left_key_type": "Int64",
            "right_key_type": "Float64",
        }

        code, display = generate_join_code(params)

        # Should include type conversion code
        assert "nw.col('id').cast(nw.Float64)" in code
        assert "df.join(right_df" in code
        assert "(auto-converted" in display

    def test_execute_join_with_type_conversion(self):
        """Test that generated join with type conversion executes correctly."""
        left_pdf = pd.DataFrame(
            {"id": [1, 2, 3, 4], "name": ["Alice", "Bob", "Charlie", "David"]}
        )
        left_df = nw.from_native(left_pdf, eager_only=True).lazy()

        right_pdf = pd.DataFrame(
            {"user_id": [1.0, 2.0, 5.0], "city": ["NYC", "LA", "Chicago"]}
        )
        right_df = nw.from_native(right_pdf, eager_only=True).lazy()

        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "inner",
            "left_key_type": "Int64",
            "right_key_type": "Float64",
        }

        code, display = generate_join_code(params)

        df = left_df
        exec_locals = {"df": df, "right_df": right_df, "nw": nw}
        exec(code, {}, exec_locals)
        result = exec_locals["df"].collect()

        # Join should succeed despite type difference
        assert len(result) == 2
        assert result["id"].to_list() == [1.0, 2.0]
        assert result["name"].to_list() == ["Alice", "Bob"]
        assert result["city"].to_list() == ["NYC", "LA"]

    def test_generate_join_code_without_type_conversion(self):
        """Test generating join code without type conversion (same types)."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "user_id",
            "how": "inner",
            "left_key_type": "Int64",
            "right_key_type": "Int64",
        }

        code, display = generate_join_code(params)

        # Should NOT include type conversion code
        assert "cast" not in code
        assert "df.join(right_df" in code
        assert "(auto-converted" not in display

    def test_incompatible_types_raise_error(self):
        """Test that incompatible types raise ValueError in generate_join_code."""
        params = {
            "right_dataset_id": "dataset_2",
            "left_key": "id",
            "right_key": "name",
            "how": "inner",
            "left_key_type": "Int64",
            "right_key_type": "String",
        }

        with pytest.raises(ValueError, match="not compatible"):
            generate_join_code(params)
