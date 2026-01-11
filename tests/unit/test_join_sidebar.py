"""Test JoinSidebar functionality."""

import pytest
from kittiwake.widgets.sidebars import JoinSidebar


def test_join_sidebar_initialization():
    """Test JoinSidebar initializes correctly."""
    left_columns = ["id", "name", "age"]
    available_datasets = [("dataset2.csv", "ds2_id"), ("dataset3.csv", "ds3_id")]
    sidebar = JoinSidebar(
        left_dataset_name="dataset1.csv",
        left_columns=left_columns,
        available_datasets=available_datasets,
    )

    assert sidebar.left_dataset_name == "dataset1.csv"
    assert sidebar.left_columns == left_columns
    assert sidebar.available_datasets == available_datasets
    assert sidebar.right_columns == {}
    assert len(sidebar.JOIN_TYPES) == 4  # inner, left, right, outer


def test_join_sidebar_join_types():
    """Test all join types are available."""
    sidebar = JoinSidebar()

    expected_types = ["inner", "left", "right", "outer"]

    actual_types = [join_id for join_id, _ in sidebar.JOIN_TYPES]

    assert actual_types == expected_types


def test_join_sidebar_update_datasets():
    """Test updating datasets and columns."""
    sidebar = JoinSidebar()

    left_columns = ["col1", "col2", "col3"]
    available_datasets = [("other_dataset.csv", "other_id")]

    sidebar.update_datasets(
        left_dataset_name="my_dataset.csv",
        left_columns=left_columns,
        available_datasets=available_datasets,
    )

    assert sidebar.left_dataset_name == "my_dataset.csv"
    assert sidebar.left_columns == left_columns
    assert sidebar.available_datasets == available_datasets


def test_join_sidebar_update_right_columns():
    """Test updating right dataset columns."""
    sidebar = JoinSidebar()

    right_columns = ["id", "value", "timestamp"]
    dataset_id = "dataset2_id"

    sidebar.update_right_columns(dataset_id, right_columns)

    assert dataset_id in sidebar.right_columns
    assert sidebar.right_columns[dataset_id] == right_columns


def test_join_sidebar_message_structure():
    """Test JoinRequested message structure."""
    message = JoinSidebar.JoinRequested(
        right_dataset="dataset2_id",
        left_key="id",
        right_key="user_id",
        join_type="left",
        left_suffix="_main",
        right_suffix="_joined",
    )

    assert message.right_dataset == "dataset2_id"
    assert message.left_key == "id"
    assert message.right_key == "user_id"
    assert message.join_type == "left"
    assert message.left_suffix == "_main"
    assert message.right_suffix == "_joined"


def test_join_sidebar_empty_datasets():
    """Test sidebar with no datasets available."""
    sidebar = JoinSidebar(
        left_dataset_name="dataset1.csv", left_columns=["id"], available_datasets=[]
    )

    assert sidebar.available_datasets == []
    assert sidebar.left_dataset_name == "dataset1.csv"
    assert sidebar.left_columns == ["id"]


def test_join_sidebar_multiple_right_columns():
    """Test managing columns for multiple right datasets."""
    sidebar = JoinSidebar()

    sidebar.update_right_columns("ds1", ["col1", "col2"])
    sidebar.update_right_columns("ds2", ["colA", "colB", "colC"])
    sidebar.update_right_columns("ds3", ["x", "y"])

    assert len(sidebar.right_columns) == 3
    assert sidebar.right_columns["ds1"] == ["col1", "col2"]
    assert sidebar.right_columns["ds2"] == ["colA", "colB", "colC"]
    assert sidebar.right_columns["ds3"] == ["x", "y"]


if __name__ == "__main__":
    test_join_sidebar_initialization()
    test_join_sidebar_join_types()
    test_join_sidebar_update_datasets()
    test_join_sidebar_update_right_columns()
    test_join_sidebar_message_structure()
    test_join_sidebar_empty_datasets()
    test_join_sidebar_multiple_right_columns()
    print("All tests passed!")
