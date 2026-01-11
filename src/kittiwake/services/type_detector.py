"""Type detection service for mapping narwhals dtypes to visual categories."""

from typing import Literal

TypeCategory = Literal["numeric", "text", "date", "boolean", "list", "dict", "unknown"]


def detect_column_type_category(dtype_str: str) -> TypeCategory:
    """Map narwhals dtype string to visual category.

    Args:
        dtype_str: Narwhals dtype as string (e.g., "Int64", "String", "Boolean", "List(Int64)", "Struct(...)")

    Returns:
        Type category: "numeric", "text", "date", "boolean", "list", "dict", or "unknown"

    Examples:
        >>> detect_column_type_category("Int64")
        'numeric'
        >>> detect_column_type_category("String")
        'text'
        >>> detect_column_type_category("Boolean")
        'boolean'
        >>> detect_column_type_category("Datetime")
        'date'
        >>> detect_column_type_category("List(Int64)")
        'list'
        >>> detect_column_type_category("Struct({'a': Int64})")
        'dict'
        >>> detect_column_type_category("Unknown")
        'unknown'

    """
    dtype_lower = dtype_str.lower()

    # List types (check before numeric since "list(int64)" contains "int")
    if dtype_lower.startswith("list"):
        return "list"

    # Dict/Struct types
    if dtype_lower.startswith("struct"):
        return "dict"

    # Numeric types
    if any(num_type in dtype_lower for num_type in ["int", "float", "decimal", "uint"]):
        return "numeric"

    # Text types
    if any(
        text_type in dtype_lower
        for text_type in ["string", "str", "categorical", "enum", "object"]
    ):
        return "text"

    # Date/time types
    if any(date_type in dtype_lower for date_type in ["date", "time", "duration"]):
        return "date"

    # Boolean types
    if "bool" in dtype_lower:
        return "boolean"

    # Unknown/unsupported
    return "unknown"
