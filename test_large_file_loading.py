#!/usr/bin/env python3
"""Test script for large file loading with progress indicators."""

import os
import tempfile
from pathlib import Path

import polars as pl


def create_large_csv(path: Path, num_rows: int = 1_000_000):
    """Create a large CSV file for testing.

    Args:
        path: Path to save the CSV
        num_rows: Number of rows to generate
    """
    print(f"Generating {num_rows:,} row CSV file...")

    # Create a DataFrame with multiple columns
    df = pl.DataFrame(
        {
            "id": range(num_rows),
            "name": [f"Person_{i}" for i in range(num_rows)],
            "age": [(i % 80) + 18 for i in range(num_rows)],
            "salary": [(i * 137) % 200000 for i in range(num_rows)],
            "department": [f"Dept_{i % 10}" for i in range(num_rows)],
            "city": [f"City_{i % 50}" for i in range(num_rows)],
        }
    )

    # Write to CSV
    df.write_csv(str(path))

    # Get file size
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Created {path.name}: {size_mb:.1f} MB")

    return path


def test_file_info_detection():
    """Test that DataLoader correctly detects large files."""
    from kittiwake.services.data_loader import DataLoader

    loader = DataLoader()

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test 1: Small file (should not trigger loading modal)
        small_file = tmppath / "small.csv"
        create_large_csv(small_file, num_rows=1000)

        size, rows, is_large = loader.get_file_info(str(small_file))
        print(f"\nSmall file test:")
        print(f"  Size: {size / 1024:.1f} KB")
        print(f"  Est. rows: {rows:,}")
        print(f"  Is large: {is_large}")
        assert not is_large, "Small file should not be detected as large"

        # Test 2: Large file by row count (should trigger loading modal)
        large_file = tmppath / "large.csv"
        create_large_csv(large_file, num_rows=1_500_000)

        size, rows, is_large = loader.get_file_info(str(large_file))
        print(f"\nLarge file test:")
        print(f"  Size: {size / (1024 * 1024):.1f} MB")
        print(f"  Est. rows: {rows:,}")
        print(f"  Is large: {is_large}")
        assert is_large, "Large file should be detected as large"
        assert rows > 1_000_000, "Should estimate >1M rows"

        print("\n✓ File info detection tests passed!")


def test_progress_callback():
    """Test that progress callback is called during loading."""
    from kittiwake.services.data_loader import DataLoader

    loader = DataLoader()
    progress_values = []
    progress_messages = []

    def progress_callback(value: float, message: str):
        progress_values.append(value)
        progress_messages.append(message)
        print(f"  Progress: {value * 100:.0f}% - {message}")

    # Create temp CSV
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        csv_file = tmppath / "test.csv"
        create_large_csv(csv_file, num_rows=10000)

        print("\nTesting progress callback:")

        # Load with progress callback
        import asyncio

        dataset = asyncio.run(
            loader.load_from_source(str(csv_file), progress_callback=progress_callback)
        )

        # Verify progress callback was called
        assert len(progress_values) > 0, "Progress callback should be called"
        assert progress_values[0] == 0.0, "Should start at 0%"
        assert progress_values[-1] == 1.0, "Should end at 100%"
        assert all(0 <= v <= 1 for v in progress_values), "All values should be 0-1"

        # Verify messages
        assert any("Initializing" in msg for msg in progress_messages)
        assert any("Complete" in msg for msg in progress_messages)

        print(f"\n✓ Progress callback test passed!")
        print(f"  Dataset loaded: {dataset.name}")
        print(f"  Rows: {dataset.row_count:,}")
        print(f"  Columns: {len(dataset.schema)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Large File Loading Implementation")
    print("=" * 60)

    try:
        test_file_info_detection()
        test_progress_callback()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
