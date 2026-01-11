"""Centralized keyboard shortcuts registry."""


class KeybindingsRegistry:
    """Registry for keyboard shortcuts across screens."""

    # Global shortcuts (available everywhere)
    GLOBAL_BINDINGS = {
        "ctrl+c": "quit",
        "?": "help",
        "q": "quit_screen",
    }

    # Main screen shortcuts
    MAIN_SCREEN_BINDINGS = {
        "f": "filter",
        "a": "aggregate",
        "p": "pivot",
        "s": "sort",
        "c": "select_columns",
        "d": "drop_columns",
        "r": "rename_columns",
        "w": "with_columns",
        "u": "unique",
        "h": "head",
        "t": "tail",
        "m": "sample",
        "j": "join",
        "ctrl+s": "save_analysis",
        "tab": "next_dataset",
        "shift+tab": "prev_dataset",
        "ctrl+z": "undo",
        "ctrl+shift+z": "redo",
        "n+f": "fill_null",
        "n+d": "drop_nulls",
        "d+c": "drop_columns",
        "ctrl+d": "split_pane",
    }

    def get_bindings(self, screen: str = "main") -> dict[str, str]:
        """Get bindings for specific screen."""
        bindings = self.GLOBAL_BINDINGS.copy()

        if screen == "main":
            bindings.update(self.MAIN_SCREEN_BINDINGS)

        return bindings

    def get_help_text(self, screen: str = "main") -> list[tuple[str, str]]:
        """Get help text for screen."""
        bindings = self.get_bindings(screen)

        return [
            (key, action.replace("_", " ").title())
            for key, action in sorted(bindings.items())
        ]

    def format_binding(self, key: str) -> str:
        """Format key for display."""
        # Convert key to human-readable format
        replacements = {
            "ctrl+": "Ctrl+",
            "shift+": "Shift+",
            "tab": "Tab",
            "space": "Space",
            "enter": "Enter",
            "esc": "Escape",
        }

        formatted = key
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)

        return formatted
