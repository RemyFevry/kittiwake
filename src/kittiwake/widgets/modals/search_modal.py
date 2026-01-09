"""Search modal for full-text search across all columns."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class SearchModal(ModalScreen):
    """Modal screen for building search operations.

    Features:
    - Text input field for search query
    - Apply and Cancel buttons
    - Keyboard-navigable (Tab, Enter, Esc)
    - Enter key in input field triggers Apply
    - Returns dict with query on Apply

    Keyboard shortcuts:
    - Tab: Navigate between fields
    - Enter: Submit search (Apply)
    - Escape: Cancel and close modal
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, **kwargs):
        """Initialize search modal.

        Args:
            **kwargs: Additional arguments passed to ModalScreen
        """
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Create search modal content."""
        with Container(id="search_dialog"):
            yield Static("Search Data", id="search_title")

            with Container(id="search_content"):
                yield Label("Enter search query (searches across all columns):")
                yield Input(
                    placeholder="Search text...",
                    id="search_query",
                )

            with Horizontal(id="search_buttons"):
                yield Button("Apply", variant="primary", id="apply")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        """Focus input field when modal opens."""
        self.query_one("#search_query", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event
        """
        if event.button.id == "apply":
            self._apply_search()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field to trigger Apply.

        Args:
            event: Input submitted event
        """
        if event.input.id == "search_query":
            self._apply_search()

    def _apply_search(self) -> None:
        """Apply search and return result to parent."""
        query_input = self.query_one("#search_query", Input)
        query_text = query_input.value.strip()

        # Return dict with search query
        result = {
            "query": query_text,
        }

        self.dismiss(result)

    def action_cancel(self) -> None:
        """Cancel search and close modal without returning data."""
        self.dismiss(None)

    def _build_search_operation(
        self, search_dict: dict, columns: list[str], schema: dict[str, str] | None = None
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
            >>> modal._build_search_operation({"query": "male"}, ["name", "city"])
            ('df.filter(nw.col("name").str.contains("male", case_sensitive=False) | '
             'nw.col("city").str.contains("male", case_sensitive=False))',
             "Search: 'male'",
             {"query": "male"})

            >>> modal._build_search_operation({"query": "25"}, ["name", "age"], {"name": "Utf8", "age": "Int64"})
            ('df.filter(nw.col("name").str.contains("25", case_sensitive=False) | '
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

        # Build search conditions based on column types
        if schema:
            # We have schema information - use it for smart searching
            for col in columns:
                dtype = schema.get(col, "").lower()

                # String/text columns: use str.contains
                if any(keyword in dtype for keyword in ["string", "object", "utf"]) or (
                    "str" in dtype and "struct" not in dtype
                ):
                    conditions.append(
                        f'nw.col("{col}").str.contains("{query}", case_sensitive=False)'
                    )
                # Numeric columns: if query is numeric, search for exact match
                elif is_numeric and any(
                    keyword in dtype
                    for keyword in ["int", "float", "decimal", "uint"]
                ):
                    conditions.append(f'nw.col("{col}") == {numeric_value}')
        else:
            # No schema - search all columns as strings (backward compatible)
            conditions = [
                f'nw.col("{col}").str.contains("{query}", case_sensitive=False)'
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

        # Build complete filter expression
        code = f"df.filter({combined_condition})"

        # Human-readable display
        display = f"Search: '{query}'"

        return (code, display, search_dict)


# CSS for search modal
SEARCH_MODAL_CSS = """
SearchModal {
    align: center middle;
}

#search_dialog {
    width: 60;
    height: auto;
    background: $surface;
    border: thick $primary;
    padding: 1;
}

#search_title {
    text-align: center;
    text-style: bold;
    background: $primary;
    color: $text;
    margin-bottom: 1;
    padding: 1;
}

#search_content {
    padding: 1;
    height: auto;
}

#search_content Label {
    margin-bottom: 1;
    color: $text;
}

#search_content Input {
    margin-bottom: 1;
}

#search_buttons {
    height: auto;
    align: center middle;
    padding: 1;
}

#search_buttons Button {
    margin: 0 1;
}
"""
