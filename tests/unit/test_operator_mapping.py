"""Tests for operator mapping functionality."""

import pytest
from kittiwake.utils.type_colors import map_operator_to_symbol


class TestOperatorMapping:
    """Test operator display name to symbol mapping."""

    def test_numeric_operators(self):
        """Test numeric operator mappings."""
        assert map_operator_to_symbol("equals (=)") == "=="
        assert map_operator_to_symbol("not equals (!=)") == "!="
        assert map_operator_to_symbol("greater than (>)") == ">"
        assert map_operator_to_symbol("less than (<)") == "<"
        assert map_operator_to_symbol("greater than or equal (>=)") == ">="
        assert map_operator_to_symbol("less than or equal (<=)") == "<="

    def test_text_operators(self):
        """Test text operator mappings."""
        assert map_operator_to_symbol("equals") == "=="
        assert map_operator_to_symbol("not equals") == "!="
        assert map_operator_to_symbol("contains") == "contains"
        assert map_operator_to_symbol("not contains") == "not contains"
        assert map_operator_to_symbol("starts with") == "starts with"
        assert map_operator_to_symbol("ends with") == "ends with"

    def test_date_operators(self):
        """Test date operator mappings."""
        assert map_operator_to_symbol("before (<)") == "<"
        assert map_operator_to_symbol("after (>)") == ">"
        assert map_operator_to_symbol("on or before (<=)") == "<="
        assert map_operator_to_symbol("on or after (>=)") == ">="

    def test_boolean_operators(self):
        """Test boolean operator mappings."""
        assert map_operator_to_symbol("is true") == "is true"
        assert map_operator_to_symbol("is false") == "is false"
        assert map_operator_to_symbol("is null") == "is null"
        assert map_operator_to_symbol("is not null") == "is not null"

    def test_unknown_operator_passthrough(self):
        """Test that unknown operators are passed through unchanged."""
        unknown = "some unknown operator"
        assert map_operator_to_symbol(unknown) == unknown

    def test_empty_string(self):
        """Test empty string handling."""
        assert map_operator_to_symbol("") == ""

    def test_case_sensitivity(self):
        """Test that operator mapping is case-sensitive."""
        # Exact match required
        assert map_operator_to_symbol("equals (=)") == "=="
        # Different case should pass through
        assert map_operator_to_symbol("EQUALS (=)") == "EQUALS (=)"
        assert map_operator_to_symbol("Equals (=)") == "Equals (=)"


class TestOperatorMappingEdgeCases:
    """Test edge cases in operator mapping."""

    def test_similar_operators(self):
        """Test that similar-looking operators map correctly."""
        # Numeric vs text "equals"
        assert map_operator_to_symbol("equals (=)") == "=="
        assert map_operator_to_symbol("equals") == "=="

        # Both should map to same symbol but from different display strings
        numeric_equals = map_operator_to_symbol("equals (=)")
        text_equals = map_operator_to_symbol("equals")
        assert numeric_equals == text_equals == "=="

    def test_whitespace_sensitivity(self):
        """Test that whitespace matters in operator strings."""
        # Exact match with spaces
        assert map_operator_to_symbol("is null") == "is null"
        # Extra spaces should not match
        assert map_operator_to_symbol("is  null") == "is  null"  # double space
        assert map_operator_to_symbol(" is null") == " is null"  # leading space
        assert map_operator_to_symbol("is null ") == "is null "  # trailing space

    def test_all_operators_return_string(self):
        """Test that all operators return string type."""
        test_operators = [
            "equals (=)",
            "not equals (!=)",
            "greater than (>)",
            "contains",
            "is true",
            "unknown operator",
        ]
        for op in test_operators:
            result = map_operator_to_symbol(op)
            assert isinstance(result, str)

    def test_idempotency(self):
        """Test that mapping symbols again doesn't change them."""
        # Mapping a symbol should return the symbol itself (passthrough)
        assert map_operator_to_symbol("==") == "=="
        assert map_operator_to_symbol(">") == ">"
        assert map_operator_to_symbol("contains") == "contains"


class TestOperatorMappingIntegration:
    """Test operator mapping in integration scenarios."""

    def test_all_numeric_operators_mapped(self):
        """Test all numeric operators from TYPE_OPERATORS are mappable."""
        numeric_operators = [
            "equals (=)",
            "not equals (!=)",
            "greater than (>)",
            "less than (<)",
            "greater than or equal (>=)",
            "less than or equal (<=)",
        ]
        for op in numeric_operators:
            symbol = map_operator_to_symbol(op)
            assert symbol in ["==", "!=", ">", "<", ">=", "<="]

    def test_all_text_operators_mapped(self):
        """Test all text operators from TYPE_OPERATORS are mappable."""
        text_operators = [
            "equals",
            "not equals",
            "contains",
            "not contains",
            "starts with",
            "ends with",
        ]
        for op in text_operators:
            symbol = map_operator_to_symbol(op)
            assert symbol in [
                "==",
                "!=",
                "contains",
                "not contains",
                "starts with",
                "ends with",
            ]

    def test_all_boolean_operators_mapped(self):
        """Test all boolean operators from TYPE_OPERATORS are mappable."""
        boolean_operators = ["is true", "is false", "is null", "is not null"]
        for op in boolean_operators:
            symbol = map_operator_to_symbol(op)
            assert symbol in ["is true", "is false", "is null", "is not null"]

    def test_round_trip_consistency(self):
        """Test that mapping is consistent across multiple calls."""
        operators = ["equals (=)", "contains", "is true", "greater than (>)"]
        for op in operators:
            result1 = map_operator_to_symbol(op)
            result2 = map_operator_to_symbol(op)
            assert result1 == result2
