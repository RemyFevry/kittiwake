#!/usr/bin/env python3
"""Visual test for type-based column coloring in DatasetTable.

This script creates a sample dataset with various column types including
list and dict columns, then displays it in a minimal Textual app to verify
that column headers are colored correctly.
"""

import polars as pl
import narwhals as nw
from textual.app import App, ComposeResult

from src.kittiwake.models.dataset import Dataset
from src.kittiwake.widgets.dataset_table import DatasetTable


class TestApp(App):
    """Minimal app to test column coloring."""

    def compose(self) -> ComposeResult:
        # Create test dataframe with diverse column types
        df = pl.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 28],
                "salary": [50000.50, 60000.75, 55000.25],
                "is_active": [True, False, True],
                "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "tags": [["python", "rust"], ["go", "java"], ["c++"]],
                "metadata": [
                    {"city": "NYC", "level": 3},
                    {"city": "LA", "level": 5},
                    {"city": "SF", "level": 4},
                ],
            }
        )

        # Convert dates and create lazy frame
        df = df.with_columns(pl.col("created_at").str.to_date())
        lazy_df = df.lazy()

        # Create Dataset
        nw_df = nw.from_native(lazy_df)
        dataset = Dataset(name="test_data", frame=nw_df)

        # Create and yield table
        yield DatasetTable(dataset=dataset)


if __name__ == "__main__":
    app = TestApp()
    app.run()
