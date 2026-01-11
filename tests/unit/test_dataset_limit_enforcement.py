"""Tests for 10-dataset limit enforcement with warnings."""

import pytest
from uuid import uuid4

from kittiwake.models.dataset import Dataset
from kittiwake.models.dataset_session import DatasetAddResult, DatasetSession


def create_test_dataset(name: str = "test") -> Dataset:
    """Create a minimal test dataset.

    Args:
        name: Name for the dataset

    Returns:
        Dataset instance

    """
    dataset = Dataset(
        id=uuid4(),
        name=name,
        source="test.csv",
        original_frame=None,  # Not needed for limit tests
        current_frame=None,
        schema={},
    )
    return dataset


class TestDatasetLimitEnforcement:
    """Test dataset limit enforcement with warnings at 8/9 datasets."""

    def test_add_first_dataset_success(self):
        """Test adding first dataset returns SUCCESS."""
        session = DatasetSession()
        dataset = create_test_dataset("dataset_1")

        result = session.add_dataset(dataset)

        assert result == DatasetAddResult.SUCCESS
        assert len(session.datasets) == 1
        assert session.active_dataset_id == dataset.id

    def test_add_datasets_1_to_7_success(self):
        """Test adding datasets 1-7 returns SUCCESS."""
        session = DatasetSession()

        for i in range(1, 8):
            dataset = create_test_dataset(f"dataset_{i}")
            result = session.add_dataset(dataset)

            assert result == DatasetAddResult.SUCCESS
            assert len(session.datasets) == i

    def test_add_8th_dataset_warning(self):
        """Test adding 8th dataset returns WARNING_8_DATASETS."""
        session = DatasetSession()

        # Add 7 datasets
        for i in range(1, 8):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Add 8th dataset - should warn
        dataset_8 = create_test_dataset("dataset_8")
        result = session.add_dataset(dataset_8)

        assert result == DatasetAddResult.WARNING_8_DATASETS
        assert len(session.datasets) == 8

    def test_add_9th_dataset_warning(self):
        """Test adding 9th dataset returns WARNING_9_DATASETS."""
        session = DatasetSession()

        # Add 8 datasets
        for i in range(1, 9):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Add 9th dataset - should warn
        dataset_9 = create_test_dataset("dataset_9")
        result = session.add_dataset(dataset_9)

        assert result == DatasetAddResult.WARNING_9_DATASETS
        assert len(session.datasets) == 9

    def test_add_10th_dataset_success(self):
        """Test adding 10th dataset returns SUCCESS (at limit but not over)."""
        session = DatasetSession()

        # Add 9 datasets
        for i in range(1, 10):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Add 10th dataset - should succeed without warning
        dataset_10 = create_test_dataset("dataset_10")
        result = session.add_dataset(dataset_10)

        assert result == DatasetAddResult.SUCCESS
        assert len(session.datasets) == 10

    def test_add_11th_dataset_error(self):
        """Test adding 11th dataset returns ERROR_AT_LIMIT."""
        session = DatasetSession()

        # Add 10 datasets
        for i in range(1, 11):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Try to add 11th dataset - should be rejected
        dataset_11 = create_test_dataset("dataset_11")
        result = session.add_dataset(dataset_11)

        assert result == DatasetAddResult.ERROR_AT_LIMIT
        assert len(session.datasets) == 10  # Still at limit

    def test_add_12th_dataset_error(self):
        """Test adding 12th dataset also returns ERROR_AT_LIMIT."""
        session = DatasetSession()

        # Add 10 datasets
        for i in range(1, 11):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Try to add 11th and 12th datasets - both should be rejected
        dataset_11 = create_test_dataset("dataset_11")
        result_11 = session.add_dataset(dataset_11)

        dataset_12 = create_test_dataset("dataset_12")
        result_12 = session.add_dataset(dataset_12)

        assert result_11 == DatasetAddResult.ERROR_AT_LIMIT
        assert result_12 == DatasetAddResult.ERROR_AT_LIMIT
        assert len(session.datasets) == 10

    def test_name_conflict_handling_preserves_limit(self):
        """Test that name conflict resolution doesn't bypass limit checks."""
        session = DatasetSession()

        # Add 10 datasets
        for i in range(1, 11):
            session.add_dataset(create_test_dataset(f"dataset_{i}"))

        # Try to add duplicate name at limit
        duplicate = create_test_dataset("dataset_1")
        result = session.add_dataset(duplicate)

        assert result == DatasetAddResult.ERROR_AT_LIMIT
        assert len(session.datasets) == 10

    def test_remove_and_add_after_limit(self):
        """Test that removing a dataset allows adding another."""
        session = DatasetSession()

        # Add 10 datasets
        datasets = []
        for i in range(1, 11):
            ds = create_test_dataset(f"dataset_{i}")
            session.add_dataset(ds)
            datasets.append(ds)

        # Remove one dataset
        session.remove_dataset(datasets[0].id)
        assert len(session.datasets) == 9

        # Now we can add another
        new_dataset = create_test_dataset("new_dataset")
        result = session.add_dataset(new_dataset)

        assert result == DatasetAddResult.SUCCESS
        assert len(session.datasets) == 10

    def test_warning_sequence_8_9_10(self):
        """Test warning sequence: 8 (warn), 9 (warn), 10 (success), 11 (error)."""
        session = DatasetSession()

        # Add 7 datasets - all SUCCESS
        for i in range(1, 8):
            result = session.add_dataset(create_test_dataset(f"ds_{i}"))
            assert result == DatasetAddResult.SUCCESS

        # 8th: WARNING_8_DATASETS
        result_8 = session.add_dataset(create_test_dataset("ds_8"))
        assert result_8 == DatasetAddResult.WARNING_8_DATASETS

        # 9th: WARNING_9_DATASETS
        result_9 = session.add_dataset(create_test_dataset("ds_9"))
        assert result_9 == DatasetAddResult.WARNING_9_DATASETS

        # 10th: SUCCESS (at limit, no warning)
        result_10 = session.add_dataset(create_test_dataset("ds_10"))
        assert result_10 == DatasetAddResult.SUCCESS

        # 11th: ERROR_AT_LIMIT
        result_11 = session.add_dataset(create_test_dataset("ds_11"))
        assert result_11 == DatasetAddResult.ERROR_AT_LIMIT

        assert len(session.datasets) == 10
