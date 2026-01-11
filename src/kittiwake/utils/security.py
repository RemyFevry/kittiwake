"""Security utilities for input validation and sanitization."""

import json
import re
from pathlib import Path
from typing import Any


class SecurityError(Exception):
    """Security validation error."""

    pass


class InputValidator:
    """Validates and sanitizes user input."""

    @staticmethod
    def validate_file_path(
        path: str | Path, allowed_dirs: list[Path] | None = None
    ) -> Path:
        """Validate file path for path traversal vulnerabilities.

        Args:
            path: User-provided file path
            allowed_dirs: Optional list of allowed parent directories

        Returns:
            Resolved Path object if valid

        Raises:
            SecurityError: If path is invalid or contains path traversal

        """
        try:
            path_obj = Path(path)

            # Resolve to absolute path to prevent symlink/.. traversal
            resolved = path_obj.resolve()

            # Check if path contains suspicious patterns
            path_str = str(path_obj)
            if ".." in path_str:
                raise SecurityError(f"Path traversal detected in path: {path}")

            # If allowed_dirs specified, ensure path is within one of them
            if allowed_dirs:
                is_allowed = False
                for allowed_dir in allowed_dirs:
                    allowed_resolved = allowed_dir.resolve()
                    try:
                        # Check if resolved path is relative to allowed dir
                        resolved.relative_to(allowed_resolved)
                        is_allowed = True
                        break
                    except ValueError:
                        continue

                if not is_allowed:
                    raise SecurityError(f"Path is outside allowed directories: {path}")

            return resolved

        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise SecurityError(f"Invalid path: {path} - {e}")

    @staticmethod
    def validate_column_name(column_name: str) -> str:
        """Validate column name to prevent SQL/code injection.

        Args:
            column_name: Column name from user input

        Returns:
            Validated column name

        Raises:
            SecurityError: If column name contains invalid characters

        """
        if not column_name:
            raise SecurityError("Column name cannot be empty")

        # Allow alphanumeric, underscore, hyphen, and spaces
        # This covers most legitimate column names
        if not re.match(r"^[a-zA-Z0-9_\-\s\.]+$", column_name):
            raise SecurityError(
                f"Column name contains invalid characters: {column_name}"
            )

        # Prevent excessively long names
        if len(column_name) > 255:
            raise SecurityError("Column name too long (max 255 characters)")

        return column_name

    @staticmethod
    def validate_sql_identifier(identifier: str) -> str:
        """Validate SQL identifier (table name, column name, etc.).

        Args:
            identifier: SQL identifier from user input

        Returns:
            Validated identifier

        Raises:
            SecurityError: If identifier contains invalid characters

        """
        if not identifier:
            raise SecurityError("SQL identifier cannot be empty")

        # SQL identifiers should only contain alphanumeric, underscore
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            raise SecurityError(
                f"SQL identifier contains invalid characters: {identifier}"
            )

        # Prevent excessively long identifiers
        if len(identifier) > 255:
            raise SecurityError("SQL identifier too long (max 255 characters)")

        return identifier

    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 10000) -> str:
        """Sanitize text input for display/storage.

        Args:
            text: User-provided text
            max_length: Maximum allowed length

        Returns:
            Sanitized text

        Raises:
            SecurityError: If text exceeds max_length

        """
        if len(text) > max_length:
            raise SecurityError(f"Text exceeds maximum length of {max_length}")

        # Remove null bytes
        text = text.replace("\x00", "")

        return text

    @staticmethod
    def escape_string_literal(value: str) -> str:
        """Escape string literal for safe embedding in generated code.

        Args:
            value: String value to escape

        Returns:
            Escaped string safe for embedding in Python code

        """
        # Escape backslashes first, then quotes
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return escaped

    @staticmethod
    def validate_regex_pattern(pattern: str) -> str:
        """Validate regex pattern for safety.

        Args:
            pattern: User-provided regex pattern

        Returns:
            Validated pattern

        Raises:
            SecurityError: If pattern is invalid or could cause ReDoS

        """
        if not pattern:
            return pattern

        # Check pattern length to prevent ReDoS
        if len(pattern) > 1000:
            raise SecurityError("Regex pattern too long (max 1000 characters)")

        # Try to compile to check validity
        try:
            re.compile(pattern)
        except re.error as e:
            raise SecurityError(f"Invalid regex pattern: {e}")

        # Check for nested quantifiers that could cause ReDoS
        # This is a basic check - more sophisticated analysis would be needed
        # for production use
        if re.search(r"(\*|\+|\{[0-9,]+\})\s*(\*|\+|\{[0-9,]+\})", pattern):
            raise SecurityError(
                "Regex pattern contains nested quantifiers (potential ReDoS)"
            )

        return pattern

    @staticmethod
    def validate_numeric_value(value: str) -> float | int:
        """Validate and parse numeric value.

        Args:
            value: String representation of number

        Returns:
            Parsed numeric value (int or float)

        Raises:
            SecurityError: If value is not a valid number

        """
        try:
            # Try int first
            if "." not in value and "e" not in value.lower():
                return int(value)
            return float(value)
        except ValueError as e:
            raise SecurityError(f"Invalid numeric value: {value} - {e}")

    @staticmethod
    def validate_operation_code(code: str) -> str:
        """Validate operation code for safety (basic checks).

        Args:
            code: Operation code to validate

        Returns:
            Validated code

        Raises:
            SecurityError: If code contains suspicious patterns

        """
        if not code:
            raise SecurityError("Operation code cannot be empty")

        # Check length
        if len(code) > 10000:
            raise SecurityError("Operation code too long (max 10000 characters)")

        # Check for suspicious patterns (basic list)
        suspicious_patterns = [
            r"import\s+os",
            r"import\s+sys",
            r"import\s+subprocess",
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"open\s*\(",
            r"file\s*\(",
            r"input\s*\(",
            r"raw_input\s*\(",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(
                    f"Operation code contains suspicious pattern: {pattern}"
                )

        return code

    @staticmethod
    def validate_analysis_name(name: str) -> str:
        """Validate analysis name for saving.

        Args:
            name: Analysis name from user

        Returns:
            Validated name

        Raises:
            SecurityError: If name is invalid

        """
        if not name or not name.strip():
            raise SecurityError("Analysis name cannot be empty")

        name = name.strip()

        # Check length
        if len(name) < 1 or len(name) > 100:
            raise SecurityError("Analysis name must be 1-100 characters")

        # Check for path separators and other dangerous characters
        dangerous_chars = ["/", "\\", "\x00", "\n", "\r", "\t"]
        for char in dangerous_chars:
            if char in name:
                raise SecurityError(
                    f"Analysis name contains invalid character: {repr(char)}"
                )

        # Prevent SQL injection in name
        # While we use parameterized queries, extra validation doesn't hurt
        if any(keyword in name.lower() for keyword in ["--", "/*", "*/", ";"]):
            raise SecurityError("Analysis name contains SQL-like syntax")

        return name


class OperationSandbox:
    """Sandbox for executing operations safely."""

    # Whitelist of allowed builtins for operation execution
    ALLOWED_BUILTINS = {
        "True": True,
        "False": False,
        "None": None,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "len": len,
        "range": range,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "Exception": Exception,
    }

    @classmethod
    def execute_operation(cls, code: str, df: Any, nw: Any) -> Any:
        """Execute operation code in a restricted namespace.

        Args:
            code: Operation code to execute
            df: DataFrame object
            nw: Narwhals module

        Returns:
            Modified DataFrame

        Raises:
            SecurityError: If execution fails or produces invalid result

        """
        # Validate code first
        InputValidator.validate_operation_code(code)

        # Create restricted namespace
        namespace = {
            "df": df,
            "nw": nw,
            "json": json,
            "__builtins__": cls.ALLOWED_BUILTINS,
        }

        try:
            exec(code, namespace, namespace)

            # Ensure df was returned/modified
            if "df" not in namespace:
                raise SecurityError("Operation did not return 'df'")

            return namespace["df"]

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Operation execution failed: {e}")
