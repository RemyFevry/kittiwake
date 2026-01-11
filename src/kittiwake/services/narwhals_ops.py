"""Service for narwhals operations and pagination."""

from dataclasses import dataclass

import narwhals as nw


@dataclass
class TypeValidationResult:
    """Result of type compatibility validation for join keys.

    Attributes:
        is_compatible: True if types are compatible for joining
        needs_conversion: True if automatic type conversion should be applied
        conversion_code: Code to apply type conversion (empty if no conversion needed)
        left_type: Type of left join key column
        right_type: Type of right join key column
        error_message: Error message if types are incompatible
    """

    is_compatible: bool
    needs_conversion: bool = False
    conversion_code: str = ""
    left_type: str = ""
    right_type: str = ""
    error_message: str = ""


def get_base_type(dtype_str: str) -> str:
    """Extract base type from narwhals dtype string.

    Narwhals dtype strings can have variations like "Int64", "Int32", "Float64",
    "String", "Utf8", etc. This function extracts the base type category.

    Args:
        dtype_str: Narwhals dtype as string (e.g., "Int64", "Float64", "String", "Boolean")

    Returns:
        Base type category: "int", "float", "string", "boolean", "datetime", "unknown"

    Examples:
        >>> get_base_type("Int64")
        'int'
        >>> get_base_type("Int32")
        'int'
        >>> get_base_type("Float64")
        'float'
        >>> get_base_type("String")
        'string'
        >>> get_base_type("Utf8")
        'string'
        >>> get_base_type("Boolean")
        'boolean'
    """
    dtype_lower = dtype_str.lower()

    # Check for struct/dict types first (before checking for "str" in "struct")
    if dtype_lower.startswith("struct"):
        return "unknown"

    # Check for list types (before checking for numeric types since "list(int64)" contains "int")
    if dtype_lower.startswith("list"):
        return "unknown"

    if any(t in dtype_lower for t in ["int", "uint"]):
        return "int"
    if "float" in dtype_lower or "decimal" in dtype_lower:
        return "float"
    if any(t in dtype_lower for t in ["string", "str", "utf", "categorical", "enum"]):
        return "string"
    if "bool" in dtype_lower:
        return "boolean"
    if any(t in dtype_lower for t in ["date", "time", "datetime"]):
        return "datetime"

    return "unknown"


def are_types_compatible(left_type: str, right_type: str) -> bool:
    """Check if two types are compatible for joining.

    Types are considered compatible if:
    - They are exactly the same
    - One is int and the other is float (int can be losslessly promoted)
    - Both are string types
    - Both are numeric types (int/float)

    Args:
        left_type: Base type of left column (from get_base_type)
        right_type: Base type of right column (from get_base_type)

    Returns:
        True if types are compatible for joining

    Examples:
        >>> are_types_compatible("int", "int")
        True
        >>> are_types_compatible("int", "float")
        True
        >>> are_types_compatible("string", "string")
        True
        >>> are_types_compatible("int", "string")
        False
        >>> are_types_compatible("boolean", "string")
        False
    """
    if left_type == right_type:
        return True

    # int can be promoted to float (lossless conversion)
    if {left_type, right_type} == {"int", "float"}:
        return True

    # Both string types (including categorical, utf8, etc.)
    if left_type == "string" and right_type == "string":
        return True

    return False


def get_conversion_target(left_type: str, right_type: str) -> str | None:
    """Determine target type for automatic conversion.

    Returns the type to convert to, or None if conversion is not possible.

    Args:
        left_type: Base type of left column
        right_type: Base type of right column

    Returns:
        Target type for conversion, or None if no conversion possible

    Examples:
        >>> get_conversion_target("int", "float")
        'float'
        >>> get_conversion_target("float", "int")
        'float'
        >>> get_conversion_target("string", "string")
        None
        >>> get_conversion_target("int", "string")
        None
    """
    # int -> float conversion (promote int to float)
    if {left_type, right_type} == {"int", "float"}:
        return "float"

    return None


def generate_type_conversion_code(
    column: str, from_type: str, to_type: str, is_left: bool
) -> str:
    """Generate code to convert a column to a different type.

    Args:
        column: Column name to convert
        from_type: Source type (base type, not full dtype)
        to_type: Target type (base type, not full dtype)
        is_left: True if converting left dataset, False if right

    Returns:
        Narwhals code to perform the type conversion

    Examples:
        >>> generate_type_conversion_code("id", "int", "float", True)
        "df = df.with_columns(nw.col('id').cast(nw.Float64))"
        >>> generate_type_conversion_code("user_id", "int", "float", False)
        "right_df = right_df.with_columns(nw.col('user_id').cast(nw.Float64))"
    """
    df_var = "df" if is_left else "right_df"

    if to_type == "float":
        return f"{df_var} = {df_var}.with_columns(nw.col('{column}').cast(nw.Float64))"

    return ""


def validate_join_key_types(
    left_key_type: str, right_key_type: str, left_key: str, right_key: str
) -> TypeValidationResult:
    """Validate if join key types are compatible.

    Checks if the two join key columns have compatible types and determines
    if automatic type conversion is needed.

    Args:
        left_key_type: Narwhals dtype string for left join key
        right_key_type: Narwhals dtype string for right join key
        left_key: Column name of left join key (for error messages)
        right_key: Column name of right join key (for error messages)

    Returns:
        TypeValidationResult with compatibility information and optional conversion code

    Examples:
        >>> result = validate_join_key_types("Int64", "Int64", "id", "id")
        >>> result.is_compatible
        True
        >>> result.needs_conversion
        False

        >>> result = validate_join_key_types("Int64", "Float64", "id", "id")
        >>> result.is_compatible
        True
        >>> result.needs_conversion
        True
        >>> result.conversion_code
        "df = df.with_columns(nw.col('id').cast(nw.Float64))"

        >>> result = validate_join_key_types("Int64", "String", "id", "name")
        >>> result.is_compatible
        False
        >>> result.error_message
        "Type mismatch: left column 'id' (Int64) is not compatible with right column 'name' (String)"
    """
    left_base_type = get_base_type(left_key_type)
    right_base_type = get_base_type(right_key_type)

    result = TypeValidationResult(
        is_compatible=False, left_type=left_key_type, right_type=right_key_type
    )

    # Check if types are compatible
    if not are_types_compatible(left_base_type, right_base_type):
        result.error_message = (
            f"Type mismatch: left column '{left_key}' ({left_key_type}) "
            f"is not compatible with right column '{right_key}' ({right_key_type})"
        )
        return result

    # Check if conversion is needed
    target_type = get_conversion_target(left_base_type, right_base_type)

    if target_type:
        result.is_compatible = True
        result.needs_conversion = True

        # Generate conversion code for the type that needs to be converted
        if left_base_type == "int" and right_base_type == "float":
            # Convert left (int) to float
            result.conversion_code = generate_type_conversion_code(
                left_key, "int", "float", is_left=True
            )
        else:
            # Convert right (int) to float
            result.conversion_code = generate_type_conversion_code(
                right_key, "int", "float", is_left=False
            )
    else:
        result.is_compatible = True
        result.needs_conversion = False

    return result


class NarwhalsOps:
    """Wrapper for narwhals operations."""

    @staticmethod
    def get_page(lazy_frame: nw.LazyFrame, page_num: int, page_size: int = 500):
        """Get a page of data from lazy frame.

        Uses row indexing and filtering for pagination since narwhals LazyFrame
        doesn't have a slice method. This creates a row_index column temporarily.
        """
        if lazy_frame is None:
            return None

        offset = page_num * page_size

        # Get first column name for ordering (stable pagination)
        try:
            order_col = lazy_frame.columns[0] if lazy_frame.columns else None
        except Exception:
            order_col = None

        if order_col is None:
            # Fallback: just use head if we can't determine column
            return lazy_frame.head(page_size).collect()

        # Use with_row_index + filter for pagination
        # This is more efficient than head().tail() for large offsets
        try:
            result = (
                lazy_frame.with_row_index(name="__row_idx__", order_by=order_col)
                .filter(
                    (nw.col("__row_idx__") >= offset)
                    & (nw.col("__row_idx__") < offset + page_size)
                )
                .drop("__row_idx__")
                .collect()
            )
            return result
        except Exception:
            # Fallback: use head if with_row_index fails
            return lazy_frame.head(page_size).collect()

    @staticmethod
    def get_schema(frame: nw.LazyFrame) -> dict[str, str]:
        """Get schema from frame."""
        if frame is None:
            return {}

        try:
            # Use collect_schema() to avoid collecting the entire frame
            if hasattr(frame, "collect_schema"):
                schema = frame.collect_schema()
            else:
                # Fallback for backends that don't support collect_schema
                schema = frame.schema
            return {col: str(dtype) for col, dtype in schema.items()}
        except Exception:
            return {}

    @staticmethod
    def get_row_count(frame: nw.LazyFrame) -> int:
        """Get row count from lazy frame.

        Note: This collects the frame which may be expensive for large datasets.
        Consider using a count() aggregation if possible.
        """
        if frame is None:
            return 0

        try:
            # Collect and count rows using len()
            collected = frame.collect()
            return len(collected)
        except Exception:
            return 0


def generate_aggregate_code(params: dict) -> tuple[str, str]:
    """Generate narwhals aggregation code from parameters.

    Args:
        params: Dictionary containing:
            - agg_col (str): Column to aggregate
            - agg_func (str|list[str]): Aggregation function(s) - one of:
                "sum", "mean", "count", "min", "max", "median", "std"
                Can be a single string or list of strings for multiple aggregations
            - group_by (str|list[str], optional): Column(s) to group by
                Can be None for global aggregation

    Returns:
        Tuple of (code: str, display: str) where:
            - code: Executable narwhals code string
            - display: Human-readable description

    Raises:
        ValueError: If required parameters are missing or invalid

    Examples:
        >>> code, display = generate_aggregate_code({
        ...     "agg_col": "amount",
        ...     "agg_func": "sum",
        ...     "group_by": "category"
        ... })
        >>> print(code)
        df = df.group_by('category').agg([nw.col('amount').sum().alias('amount_sum')])
        >>> print(display)
        Aggregate: sum(amount) by category

        >>> code, display = generate_aggregate_code({
        ...     "agg_col": "amount",
        ...     "agg_func": ["sum", "mean", "count"],
        ...     "group_by": ["category", "region"]
        ... })
        >>> print(code)
        df = df.group_by(['category', 'region']).agg([nw.col('amount').sum().alias('amount_sum'), nw.col('amount').mean().alias('amount_mean'), nw.col('amount').count().alias('amount_count')])
        >>> print(display)
        Aggregate: sum(amount), mean(amount), count(amount) by category, region

        >>> code, display = generate_aggregate_code({
        ...     "agg_col": "amount",
        ...     "agg_func": ["sum", "mean"]
        ... })
        >>> print(code)
        df = df.select([nw.col('amount').sum().alias('amount_sum'), nw.col('amount').mean().alias('amount_mean')])
        >>> print(display)
        Aggregate: sum(amount), mean(amount)

    """
    # Validate required parameters
    if not params:
        raise ValueError("params dictionary is required")

    agg_col = params.get("agg_col")
    if not agg_col:
        raise ValueError("agg_col is required in params")

    agg_func = params.get("agg_func")
    if not agg_func:
        raise ValueError("agg_func is required in params")

    # Normalize agg_func to list
    agg_funcs = [agg_func] if isinstance(agg_func, str) else agg_func
    if not agg_funcs:
        raise ValueError("agg_func must be a non-empty string or list")

    # Validate aggregation functions
    valid_funcs = {"sum", "mean", "count", "min", "max", "median", "std"}
    for func in agg_funcs:
        if func not in valid_funcs:
            raise ValueError(
                f"Invalid aggregation function '{func}'. "
                f"Must be one of: {', '.join(sorted(valid_funcs))}"
            )

    # Get optional group_by parameter
    group_by = params.get("group_by")

    # Normalize group_by to list or None
    if group_by is not None:
        group_by_cols = [group_by] if isinstance(group_by, str) else group_by
        if not group_by_cols:
            group_by_cols = None
    else:
        group_by_cols = None

    # Generate aggregation expressions with aliases to avoid duplicate column names
    agg_exprs = [
        f"nw.col('{agg_col}').{func}().alias('{agg_col}_{func}')" for func in agg_funcs
    ]
    agg_list = f"[{', '.join(agg_exprs)}]"

    # Generate code based on whether we have group_by
    if group_by_cols:
        # Format group_by columns
        if len(group_by_cols) == 1:
            group_by_str = f"'{group_by_cols[0]}'"
        else:
            group_by_str = str([col for col in group_by_cols])

        code = f"df = df.group_by({group_by_str}).agg({agg_list})"
    else:
        # No grouping - use select for global aggregation
        code = f"df = df.select({agg_list})"

    # Generate display string
    agg_display_parts = [f"{func}({agg_col})" for func in agg_funcs]
    agg_display = ", ".join(agg_display_parts)

    if group_by_cols:
        group_display = ", ".join(group_by_cols)
        display = f"Aggregate: {agg_display} by {group_display}"
    else:
        display = f"Aggregate: {agg_display}"

    return code, display


def generate_join_code(params: dict) -> tuple[str, str]:
    """Generate narwhals join code from parameters.

    Args:
        params: Dictionary containing:
            - right_dataset_id (str): ID of the dataset to join with
            - left_key (str): Column name in the left (active) dataset to join on
            - right_key (str): Column name in the right dataset to join on
            - how (str): Join type - one of: "inner", "left", "outer", "full", "cross", "semi", "anti"
                Note: "right" join is not supported by narwhals
            - left_suffix (str, optional): Suffix for duplicate column names from left dataset (default: "_left")
            - right_suffix (str, optional): Suffix for duplicate column names from right dataset (default: "_right")
            - left_key_type (str, optional): Narwhals dtype of left join key column
            - right_key_type (str, optional): Narwhals dtype of right join key column

    Returns:
        Tuple of (code: str, display: str) where:
            - code: Executable narwhals code string
            - display: Human-readable description

    Raises:
        ValueError: If required parameters are missing or invalid

    Examples:
        >>> code, display = generate_join_code({
        ...     "right_dataset_id": "dataset_2",
        ...     "left_key": "id",
        ...     "right_key": "user_id",
        ...     "how": "inner"
        ... })
        >>> print(code)
        df = df.join(right_df, left_on='id', right_on='user_id', how='inner', suffix='_right')
        >>> print(display)
        Join: inner join on id = user_id

        >>> code, display = generate_join_code({
        ...     "right_dataset_id": "dataset_2",
        ...     "left_key": "id",
        ...     "right_key": "id",
        ...     "how": "left",
        ...     "right_suffix": "_r"
        ... })
        >>> print(code)
        df = df.join(right_df, on='id', how='left', suffix='_r')
        >>> print(display)
        Join: left join on id

        >>> code, display = generate_join_code({
        ...     "right_dataset_id": "dataset_2",
        ...     "left_key": "customer_id",
        ...     "right_key": "id",
        ...     "how": "outer",
        ...     "left_suffix": "_customer",
        ...     "right_suffix": "_order"
        ... })
        >>> print(code)
        df = df.join(right_df, left_on='customer_id', right_on='id', how='outer', suffix='_order')
        >>> print(display)
        Join: outer join on customer_id = id

        >>> code, display = generate_join_code({
        ...     "right_dataset_id": "dataset_2",
        ...     "left_key": "id",
        ...     "right_key": "user_id",
        ...     "how": "inner",
        ...     "left_key_type": "Int64",
        ...     "right_key_type": "Float64"
        ... })
        >>> print(code)
        df = df.with_columns(nw.col('id').cast(nw.Float64))
        df = df.join(right_df, left_on='id', right_on='user_id', how='inner', suffix='_right')
        >>> print(display)
        Join: inner join on id = user_id (auto-converted Int64→Float64)

    Notes:
        - The actual join operation requires access to both datasets, which will be handled
          by MainScreen or the Dataset model where multiple datasets are managed.
        - The generated code uses 'right_df' as a placeholder variable name for the right dataset.
        - Narwhals join method signature:
          join(other, on=None, how='inner', left_on=None, right_on=None, suffix='_right')
        - Join types supported by narwhals:
          * inner: Returns rows with matching values in both tables
          * left: Returns all rows from left table, matched rows from right table
          * outer/full: Returns all rows from both tables with suffix appended to right join keys
          * cross: Returns Cartesian product of rows from both tables (no join keys needed)
          * semi: Filter rows that have a match in the right table
          * anti: Filter rows that do not have a match in the right table
          Note: "right" join is not directly supported (use left join with swapped datasets)
        - When type information is provided (left_key_type, right_key_type), automatic type
          conversion is applied for compatible types (e.g., int ↔ float).
        - Supported automatic conversions: int → float (lossless promotion)
        - Incompatible types (e.g., int → string) will not auto-convert.
    """
    # Validate required parameters
    if not params:
        raise ValueError("params dictionary is required")

    right_dataset_id = params.get("right_dataset_id")
    if not right_dataset_id:
        raise ValueError("right_dataset_id is required in params")

    left_key = params.get("left_key")
    if not left_key:
        raise ValueError("left_key is required in params")

    right_key = params.get("right_key")
    if not right_key:
        raise ValueError("right_key is required in params")

    how = params.get("how")
    if not how:
        raise ValueError("how (join type) is required in params")

    # Validate join type
    # Narwhals supports: inner, left, full (not outer), cross, semi, anti
    # Note: 'right' join is not supported by narwhals (use left join with swapped dataframes instead)
    valid_join_types = {"inner", "left", "outer", "full", "cross", "semi", "anti"}
    if how not in valid_join_types:
        raise ValueError(
            f"Invalid join type '{how}'. "
            f"Must be one of: {', '.join(sorted(valid_join_types))}"
        )

    # Get optional suffix parameters
    left_suffix = params.get("left_suffix", "_left")
    right_suffix = params.get("right_suffix", "_right")

    # Validate suffix parameters
    if not isinstance(right_suffix, str):
        raise ValueError("right_suffix must be a string")
    if not isinstance(left_suffix, str):
        raise ValueError("left_suffix must be a string")

    # Map 'outer' to 'full' for narwhals compatibility
    join_how = "full" if how == "outer" else how

    # Generate code based on join type and key configuration
    if how == "cross":
        # Cross join doesn't use join keys - it creates a Cartesian product
        code = "df = df.join(right_df, how='cross')"
        display = "Join: cross join (Cartesian product)"
    elif left_key == right_key:
        # Use simplified 'on' parameter when keys are the same
        code = f"df = df.join(right_df, on='{left_key}', how='{join_how}', suffix='{right_suffix}')"
        display = f"Join: {how} join on {left_key}"
    else:
        # Use left_on/right_on parameters when keys differ
        code = f"df = df.join(right_df, left_on='{left_key}', right_on='{right_key}', how='{join_how}', suffix='{right_suffix}')"
        display = f"Join: {how} join on {left_key} = {right_key}"

    # Handle type validation and automatic conversion if type info is provided
    left_key_type = params.get("left_key_type")
    right_key_type = params.get("right_key_type")

    type_conversion_code = ""
    type_info_suffix = ""

    if left_key_type and right_key_type:
        validation = validate_join_key_types(
            left_key_type, right_key_type, left_key, right_key
        )

        if not validation.is_compatible:
            raise ValueError(validation.error_message)

        if validation.needs_conversion and validation.conversion_code:
            type_conversion_code = validation.conversion_code
            type_info_suffix = f" (auto-converted {left_key_type}→{validation.right_type if validation.left_type != validation.right_type else right_key_type})"

    # Map 'outer' to 'full' for narwhals compatibility
    join_how = "full" if how == "outer" else how

    # Generate code based on join type and key configuration
    if how == "cross":
        # Cross join doesn't use join keys - it creates a Cartesian product
        join_code = "df = df.join(right_df, how='cross')"
        display = "Join: cross join (Cartesian product)"
    elif left_key == right_key:
        # Use simplified 'on' parameter when keys are the same
        join_code = f"df = df.join(right_df, on='{left_key}', how='{join_how}', suffix='{right_suffix}')"
        display = f"Join: {how} join on {left_key}{type_info_suffix}"
    else:
        # Use left_on/right_on parameters when keys differ
        join_code = f"df = df.join(right_df, left_on='{left_key}', right_on='{right_key}', how='{join_how}', suffix='{right_suffix}')"
        display = f"Join: {how} join on {left_key} = {right_key}{type_info_suffix}"

    # Combine conversion code with join code if conversion is needed
    if type_conversion_code:
        code = f"{type_conversion_code}\n{join_code}"
    else:
        code = join_code

    # Note: left_suffix is stored in params but not used in the generated code
    # because narwhals only accepts a single 'suffix' parameter for the right table.
    # If different left suffixes are needed, this would require additional post-processing.

    return code, display


def generate_pivot_code(params: dict) -> tuple[str, str]:
    """Generate narwhals pivot table code from parameters.

    Parameters format:
        params: Dictionary containing:
            - index (str|list[str]): Column(s) to use as row dimensions
            - columns (str|list[str]): Column(s) whose values become the new column headers
            - values (list[dict]): List of value configs, each with:
                - column (str): The value column name
                - agg_functions (list[str]): Aggregation functions for this value

    Returns:
        Tuple of (code: str, display: str) where:
            - code: Executable narwhals code string
            - display: Human-readable description

    Raises:
        ValueError: If required parameters are missing or invalid

    Example:
        >>> code, display = generate_pivot_code({
        ...     "index": "category",
        ...     "columns": ["region", "product"],
        ...     "values": [
        ...         {"column": "sales", "agg_functions": ["sum", "mean"]},
        ...         {"column": "quantity", "agg_functions": ["count"]}
        ...     ]
        ... })

    Notes:
        - Narwhals pivot only works on DataFrame (not LazyFrame), so code includes
          .collect() before pivot and .lazy() after
        - Multiple aggregation functions create separate pivots that are joined together
        - Supported aggregation functions: sum, mean, count, min, max, first, last, len
        - The 'median' and 'std' are not supported by narwhals pivot (only by agg)
        - Multiple columns in 'columns' parameter creates hierarchical column names
        - All value columns are cast to Float64 before pivot
        - All result columns (non-index) are Float64
        - Multi-pivot column names normalized to ColA_valA-ColB_valB format
    """
    # Validate required parameters
    if not params:
        raise ValueError("params dictionary is required")

    index = params.get("index")
    if not index:
        raise ValueError("index is required in params")

    columns = params.get("columns")
    if not columns:
        raise ValueError("columns is required in params")

    values = params.get("values")
    if not values:
        raise ValueError("values is required in params")

    # Values must be a list of dicts
    if not isinstance(values, list):
        raise ValueError("values must be a list of dicts with 'column' and 'agg_functions' keys")
    
    if len(values) == 0:
        raise ValueError("values list cannot be empty")
    
    if not isinstance(values[0], dict):
        raise ValueError("Each value must be a dict with 'column' and 'agg_functions' keys")

    return _generate_pivot_code(params, index, columns, values)


def _generate_pivot_code(
    params: dict, index: str | list[str], columns: str | list[str], values: list[dict]
) -> tuple[str, str]:
    """Generate pivot code with per-value aggregations.

    Args:
        params: Full params dict (for validation context)
        index: Index column(s) - row dimensions
        columns: Columns to pivot on - become column headers
        values: List of dicts, each with 'column' and 'agg_functions' keys

    Returns:
        Tuple of (code, display) where code is executable narwhals code
    """
    # Validate aggregation functions
    valid_pivot_funcs = {"sum", "mean", "count", "min", "max", "first", "last", "len"}

    # Validate and collect all value configs
    value_configs = []
    for val_config in values:
        if not isinstance(val_config, dict):
            raise ValueError(
                "Each value must be a dict with 'column' and 'agg_functions' keys"
            )

        column = val_config.get("column")
        if not column:
            raise ValueError("Each value config must have a 'column' key")

        agg_funcs = val_config.get("agg_functions")
        if not agg_funcs or not isinstance(agg_funcs, list):
            raise ValueError(
                f"Value config for '{column}' must have 'agg_functions' as a non-empty list"
            )

        # Validate each aggregation function
        for func in agg_funcs:
            if func not in valid_pivot_funcs:
                raise ValueError(
                    f"Invalid aggregation function '{func}' for pivot. "
                    f"Must be one of: {', '.join(sorted(valid_pivot_funcs))}"
                )

        value_configs.append({"column": column, "agg_functions": agg_funcs})

    if not value_configs:
        raise ValueError("At least one value configuration is required")

    # Format index parameter
    if isinstance(index, list):
        if len(index) == 1:
            index_str = f"'{index[0]}'"
        else:
            index_str = str([col for col in index])
    else:
        index_str = f"'{index}'"

    # Format columns parameter
    if isinstance(columns, list):
        if len(columns) == 1:
            columns_str = f"'{columns[0]}'"
        else:
            columns_str = str([col for col in columns])
    else:
        columns_str = f"'{columns}'"

    # Generate null filter code for pivot columns to prevent duplicate "null" column names
    # This filters out rows where ANY pivot column is null
    columns_list = columns if isinstance(columns, list) else [columns]
    null_filter_conditions = [f"~nw.col('{col}').is_null()" for col in columns_list]
    null_filter = " & ".join(null_filter_conditions)
    filter_line = f"df = df.filter({null_filter})"

    # Helper: get index columns set for comparison
    def get_index_cols_set():
        if isinstance(index, list):
            return str(index)
        else:
            return f"['{index}']"

    index_cols_set = get_index_cols_set()

    # Helper: normalize multi-pivot column names like PClass_1-Sex_male
    def normalize_multi_pivot_names(var_name: str) -> list[str]:
        if isinstance(columns, list) and len(columns) > 1:
            # Generate column list for parsing
            columns_list_str = str(columns)
            lines = [
                f"rename_map_{var_name} = {{}}",
                f"for col in {var_name}.columns:",
                f"    if col in {index_cols_set}:",
                f"        continue",
                f"    try:",
                # Parse composite name: ('1','male') or ('East','Q1') tuple format
                # Narwhals creates tuples for multi-column pivots
                f"        if isinstance(col, tuple):",
                f"            parts = list(col)",
                f"        else:",
                # Fallback: try to parse string representation
                f"            col_str = str(col).strip('()').strip('{{}}')",
                f"            parts = [p.strip().strip('\"').strip(\"'\") for p in col_str.split(',')]",
                f"        name_parts = []",
                f"        for i, c in enumerate({columns_list_str}):",
                f"            if i < len(parts):",
                f"                name_parts.append(c + '_' + str(parts[i]))",
                f"        new_name = '-'.join(name_parts) if name_parts else str(col)",
                f"    except Exception:",
                f"        new_name = str(col)",
                f"    rename_map_{var_name}[col] = new_name",
                f"{var_name} = {var_name}.rename(rename_map_{var_name})",
            ]
            return lines
        return []

    # Build all pivots - one for each value+agg combination
    pivot_dfs = []
    pivot_lines = [filter_line]

    # Enforce numeric-only: cast each value column to Float64 before each pivot
    value_casts = set()

    for val_idx, val_config in enumerate(value_configs):
        column = val_config["column"]
        agg_funcs = val_config["agg_functions"]

        for agg_func in agg_funcs:
            # Create unique variable name
            var_name = f"df_{column}_{agg_func}_{val_idx}"
            pivot_dfs.append(var_name)

            # Enforce numeric-only: cast value column to Float64 before pivot
            if column not in value_casts:
                pivot_lines.append(f"df = df.with_columns(nw.col('{column}').cast(nw.Float64))")
                value_casts.add(column)

            # Generate pivot code
            pivot_code = (
                f"{var_name} = df.collect().pivot("
                f"on={columns_str}, index={index_str}, values='{column}', "
                f"aggregate_function='{agg_func}')"
            )
            pivot_lines.append(pivot_code)

            # Add renaming to include column name in result columns
            # For example: region_East becomes sales_region_East
            # Skip renaming if multiple columns - we'll normalize composite names later
            if not isinstance(columns, list):
                if isinstance(index, list):
                    index_cols_str = str(index)
                    rename_code = (
                        f"rename_map_{var_name} = {{col: f'{column}_' + col "
                        f"for col in {var_name}.columns if col not in {index_cols_str}}}"
                    )
                else:
                    rename_code = (
                        f"rename_map_{var_name} = {{col: f'{column}_' + col "
                        f"for col in {var_name}.columns if col != '{index}'}}"
                    )
                pivot_lines.append(rename_code)
                pivot_lines.append(
                    f"{var_name} = {var_name}.rename(rename_map_{var_name})"
                )
            else:
                # For multi-pivot, normalize names
                pivot_lines.extend(normalize_multi_pivot_names(var_name))

    # Join all pivots together
    if len(pivot_dfs) == 1:
        # Cast result columns to Float64 and convert to lazy
        pivot_lines.append(
            f"cast_cols = [nw.col(c).cast(nw.Float64) for c in {pivot_dfs[0]}.columns if c not in {index_cols_set}]"
        )
        pivot_lines.append(f"df = {pivot_dfs[0]}.with_columns(cast_cols).lazy()")
    else:
        join_on = str(index) if isinstance(index, list) else f"'{index}'"
        join_chain = pivot_dfs[0]

        for i, df_var in enumerate(pivot_dfs[1:], 1):
            suffix = f"_v{i}"
            join_chain = f"{join_chain}.join({df_var}, on={join_on}, suffix='{suffix}')"

        # Cast result columns to Float64 and convert to lazy
        pivot_lines.append(
            f"cast_cols = [nw.col(c).cast(nw.Float64) for c in {join_chain}.columns if c not in {index_cols_set}]"
        )
        pivot_lines.append(f"df = {join_chain}.with_columns(cast_cols).lazy()")

    code = "\n".join(pivot_lines)

    # Generate display string
    if isinstance(index, list):
        index_display = ", ".join(index)
    else:
        index_display = index

    if isinstance(columns, list):
        columns_display = ", ".join(columns)
    else:
        columns_display = columns

    # Format values display: "sales(sum, mean), quantity(count)"
    value_displays = []
    for val_config in value_configs:
        column = val_config["column"]
        agg_funcs = val_config["agg_functions"]
        value_displays.append(f"{column}({', '.join(agg_funcs)})")

    values_display = ", ".join(value_displays)

    display = f"Pivot: {values_display} by {index_display} x {columns_display}"

    return code, display
