"""Service for building filter and search operations."""

from ..utils.security import InputValidator


class OperationBuilder:
    """Builder for creating filter and search operations."""

    @staticmethod
    def build_filter_operation(filter_dict: dict) -> tuple[str, str, dict]:
        """Generate narwhals filter operation code from filter dict.

        Args:
            filter_dict: Dict with keys 'column', 'operator', 'value'

        Returns:
            Tuple of (code_string, display_string, params_dict)
            - code: Executable narwhals expression (e.g., 'df.filter(nw.col("age") > 25)')
            - display: Human-readable string (e.g., "Filter: age > 25")
            - params: Original filter_dict for editing later

        """
        column = filter_dict["column"]
        operator = filter_dict["operator"]
        value = filter_dict.get("value", "")

        # Validate column name to prevent injection
        column = InputValidator.validate_column_name(column)

        # Generate code string based on operator
        if operator == "contains":
            # String contains operation - case-insensitive
            value_lower = value.lower()
            # Escape the value for safe embedding in code
            escaped_value = InputValidator.escape_string_literal(value_lower)
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.contains("{escaped_value}"))'
            display = f"Filter: {column} contains {value}"

        elif operator == "not contains":
            # String not contains operation - case-insensitive
            value_lower = value.lower()
            escaped_value = InputValidator.escape_string_literal(value_lower)
            code = f'df = df.filter(~nw.col("{column}").str.to_lowercase().str.contains("{escaped_value}"))'
            display = f"Filter: {column} not contains {value}"

        elif operator == "starts with":
            # String starts with operation - case-insensitive
            value_lower = value.lower()
            escaped_value = InputValidator.escape_string_literal(value_lower)
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.starts_with("{escaped_value}"))'
            display = f"Filter: {column} starts with {value}"

        elif operator == "ends with":
            # String ends with operation - case-insensitive
            value_lower = value.lower()
            escaped_value = InputValidator.escape_string_literal(value_lower)
            code = f'df = df.filter(nw.col("{column}").str.to_lowercase().str.ends_with("{escaped_value}"))'
            display = f"Filter: {column} ends with {value}"

        elif operator == "is true":
            # Boolean true check
            code = f'df = df.filter(nw.col("{column}") == True)'
            display = f"Filter: {column} is true"

        elif operator == "is false":
            # Boolean false check
            code = f'df = df.filter(nw.col("{column}") == False)'
            display = f"Filter: {column} is false"

        elif operator == "is null":
            # Null check
            code = f'df = df.filter(nw.col("{column}").is_null())'
            display = f"Filter: {column} is null"

        elif operator == "is not null":
            # Not null check
            code = f'df = df.filter(~nw.col("{column}").is_null())'
            display = f"Filter: {column} is not null"

        else:
            # Comparison operators (==, !=, >, <, >=, <=)
            # Try to detect numeric values
            try:
                numeric_value = InputValidator.validate_numeric_value(value)
                # Always format as float for consistency
                numeric_value = float(numeric_value)
                # Use numeric value without quotes
                code = f'df = df.filter(nw.col("{column}") {operator} {numeric_value})'
            except Exception:
                # String value - use quotes and escape any existing quotes
                escaped_value = InputValidator.escape_string_literal(value)
                code = (
                    f'df = df.filter(nw.col("{column}") {operator} "{escaped_value}")'
                )

            # Display string
            display = f"Filter: {column} {operator} {value}"

        # Return params for potential editing later
        params = filter_dict.copy()

        return (code, display, params)

    @staticmethod
    def build_search_operation(
        search_dict: dict, columns: list[str], schema: dict[str, str] | None = None
    ) -> tuple[str, str, dict]:
        """Build narwhals search operation code from search dict.

        Generates code that searches across string columns using case-insensitive
        search with OR logic. If the query is numeric, also searches numeric columns
        for exact matches.

        Args:
            search_dict: Dict with "query" key containing search text
            columns: List of all column names from the dataset
            schema: Optional dict mapping column names to types for smart numeric search

        Returns:
            Tuple of (code_string, display_string, params_dict):
            - code: narwhals expression string to execute
            - display: human-readable description
            - params: original search_dict for editing later

        Example:
            >>> builder = OperationBuilder()
            >>> builder.build_search_operation({"query": "male"}, ["name", "city"])
            ('df.filter(nw.col("name").str.to_lowercase().str.contains("male") | '
             'nw.col("city").str.to_lowercase().str.contains("male"))',
             "Search: 'male'",
             {"query": "male"})

            >>> builder.build_search_operation({"query": "25"}, ["name", "age"], {"name": "Utf8", "age": "Int64"})
            ('df.filter(nw.col("name").str.to_lowercase().str.contains("25") | '
             'nw.col("age") == 25)',
             "Search: '25'",
             {"query": "25"})

        """
        query = search_dict.get("query", "")

        # If no query provided, return no-op
        if not query:
            return (
                "df",  # No filtering, return dataframe as-is
                "Search: (empty query)",
                search_dict,
            )

        if not columns:
            # No columns available - return no-op
            return (
                "df",
                f"Search: '{query}' (no columns available)",
                search_dict,
            )

        # Check if query is numeric
        is_numeric = False
        numeric_value = None
        try:
            numeric_value = float(query)
            is_numeric = True
        except ValueError:
            pass

        conditions = []

        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()

        # Build search conditions based on column types
        if schema:
            # We have schema information - use it for smart searching
            for col in columns:
                dtype = schema.get(col, "").lower()

                # String/text columns: use str.contains with lowercase conversion
                if any(keyword in dtype for keyword in ["string", "object", "utf"]) or (
                    "str" in dtype and "struct" not in dtype
                ):
                    conditions.append(
                        f'nw.col("{col}").str.to_lowercase().str.contains("{query_lower}")'
                    )
                # Numeric columns: if query is numeric, search for exact match
                elif is_numeric and any(
                    keyword in dtype for keyword in ["int", "float", "decimal", "uint"]
                ):
                    conditions.append(f'nw.col("{col}") == {numeric_value}')
        else:
            # No schema - search all columns as strings (backward compatible)
            conditions = [
                f'nw.col("{col}").str.to_lowercase().str.contains("{query_lower}")'
                for col in columns
            ]

        if not conditions:
            return (
                "df",
                f"Search: '{query}' (no searchable columns)",
                search_dict,
            )

        # Combine with OR operator (|)
        combined_condition = " | ".join(conditions)

        # Build complete filter expression (assignment needed for exec())
        code = f"df = df.filter({combined_condition})"

        # Human-readable display
        display = f"Search: '{query}'"

        return (code, display, search_dict)
