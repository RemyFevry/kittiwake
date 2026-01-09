"""Type color and icon configuration for column headers."""

from typing import Literal

# Redefine TypeCategory here to avoid circular imports
TypeCategory = Literal["numeric", "text", "date", "boolean", "unknown"]

# Type category to Textual color variable mapping (for CSS)
# Uses semantic Textual colors that adapt to terminal theme
TYPE_COLORS_CSS: dict[TypeCategory, str] = {
    "numeric": "primary",      # Blue/Cyan - numbers are foundational
    "text": "success",         # Green - text is successful communication
    "date": "warning",         # Orange/Yellow - dates warn of time constraints
    "boolean": "accent",       # Purple/Magenta - booleans accent true/false logic
    "unknown": "text-muted",   # Gray - unknown is muted/undefined
}

# Type category to Rich color names (for Text objects)
# These are actual color names that Rich understands
TYPE_COLORS: dict[TypeCategory, str] = {
    "numeric": "bright_blue",    # Blue - numbers are foundational
    "text": "bright_green",      # Green - text is successful communication  
    "date": "yellow",            # Yellow - dates warn of time constraints
    "boolean": "bright_magenta", # Magenta - booleans accent true/false logic
    "unknown": "bright_black",   # Gray - unknown is muted/undefined
}

# ASCII icons for type categories (work in all terminals)
TYPE_ICONS_ASCII: dict[TypeCategory, str] = {
    "numeric": "#",   # Hash/number symbol
    "text": '"',      # Quote symbol for strings
    "date": "@",      # At symbol (point in time)
    "boolean": "?",   # Question mark (true/false)
    "unknown": "·",   # Middle dot (undefined)
}

# Unicode emoji icons for enhanced terminals (optional fallback)
TYPE_ICONS_UNICODE: dict[TypeCategory, str] = {
    "numeric": "🔢",   # Input numbers emoji
    "text": "📝",      # Memo emoji
    "date": "📅",      # Calendar emoji
    "boolean": "☑",    # Checked box emoji
    "unknown": "❓",   # Question mark emoji
}

# Operator sets by type category
TYPE_OPERATORS: dict[TypeCategory, list[str]] = {
    "numeric": [
        "equals (=)",
        "not equals (!=)",
        "greater than (>)",
        "less than (<)",
        "greater than or equal (>=)",
        "less than or equal (<=)",
    ],
    "text": [
        "equals",
        "not equals",
        "contains",
        "not contains",
        "starts with",
        "ends with",
    ],
    "date": [
        "equals",
        "not equals",
        "before (<)",
        "after (>)",
        "on or before (<=)",
        "on or after (>=)",
    ],
    "boolean": [
        "is true",
        "is false",
        "is null",
        "is not null",
    ],
    "unknown": [
        "is null",
        "is not null",
    ],
}


def get_type_color(type_category: TypeCategory) -> str:
    """Get Rich color name for a type category (for Text objects).
    
    Args:
        type_category: Type category (numeric, text, date, boolean, unknown)
        
    Returns:
        Rich color name (e.g., "bright_blue", "bright_green")
    """
    return TYPE_COLORS.get(type_category, "bright_black")


def get_type_color_css(type_category: TypeCategory) -> str:
    """Get Textual CSS color variable for a type category.
    
    Args:
        type_category: Type category (numeric, text, date, boolean, unknown)
        
    Returns:
        Textual color variable name (e.g., "primary", "success")
    """
    return TYPE_COLORS_CSS.get(type_category, "text-muted")


def get_type_icon(type_category: TypeCategory, use_unicode: bool = False) -> str:
    """Get icon character for a type category.
    
    Args:
        type_category: Type category (numeric, text, date, boolean, unknown)
        use_unicode: If True, use Unicode emoji; if False, use ASCII
        
    Returns:
        Icon character (ASCII or Unicode)
    """
    icons = TYPE_ICONS_UNICODE if use_unicode else TYPE_ICONS_ASCII
    return icons.get(type_category, "·")


def get_operators_for_type(type_category: TypeCategory) -> list[str]:
    """Get available filter operators for a type category.
    
    Args:
        type_category: Type category (numeric, text, date, boolean, unknown)
        
    Returns:
        List of operator strings suitable for this type
    """
    return TYPE_OPERATORS.get(type_category, TYPE_OPERATORS["unknown"])


def terminal_supports_unicode() -> bool:
    """Detect if terminal supports Unicode emoji rendering.
    
    Returns:
        True if Unicode is likely supported, False for ASCII-only fallback
        
    Note:
        This is a heuristic check. Defaults to False (ASCII) for maximum compatibility.
        Can be enhanced with environment variable checks (LANG, LC_ALL) in future.
    """
    # TODO: Implement proper Unicode detection via locale/environment
    # For now, default to ASCII for maximum compatibility
    return False
