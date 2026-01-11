"""Session management for multiple datasets."""

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from .dataset import Dataset


class DatasetAddResult(Enum):
    """Result status when adding a dataset."""

    SUCCESS = "success"
    WARNING_8_DATASETS = "warning_8"
    WARNING_9_DATASETS = "warning_9"
    ERROR_AT_LIMIT = "error_limit"


@dataclass
class DatasetSession:
    """Manages collection of loaded datasets."""

    datasets: list[Dataset] = field(default_factory=list)
    active_dataset_id: UUID | None = None
    max_datasets: int = 10
    split_pane_enabled: bool = False
    split_pane_datasets: tuple[UUID, UUID] | None = None

    def add_dataset(self, dataset: Dataset) -> DatasetAddResult:
        """Add dataset to session with limit enforcement.

        Args:
            dataset: Dataset to add

        Returns:
            DatasetAddResult indicating success, warning, or error status

        """
        current_count = len(self.datasets)

        # Reject if at max capacity
        if current_count >= self.max_datasets:
            return DatasetAddResult.ERROR_AT_LIMIT

        # Check for name conflicts
        names = [d.name for d in self.datasets]
        if dataset.name in names:
            # Generate unique name
            counter = 1
            while f"{dataset.name}_{counter}" in names:
                counter += 1
            dataset.name = f"{dataset.name}_{counter}"

        self.datasets.append(dataset)

        # Make first dataset active
        if self.active_dataset_id is None:
            self.set_active_dataset(dataset.id)

        # Return status based on new count
        new_count = len(self.datasets)
        if new_count == 8:
            return DatasetAddResult.WARNING_8_DATASETS
        elif new_count == 9:
            return DatasetAddResult.WARNING_9_DATASETS
        else:
            return DatasetAddResult.SUCCESS

    def remove_dataset(self, dataset_id: UUID) -> None:
        """Remove dataset from session."""
        self.datasets = [d for d in self.datasets if d.id != dataset_id]

        # Handle active dataset change
        if self.active_dataset_id == dataset_id:
            if self.datasets:
                self.set_active_dataset(self.datasets[0].id)
            else:
                self.active_dataset_id = None

        # Handle split pane
        if self.split_pane_datasets and dataset_id in self.split_pane_datasets:
            self.split_pane_enabled = False
            self.split_pane_datasets = None

    def set_active_dataset(self, dataset_id: UUID) -> None:
        """Set active dataset."""
        # Clear all active flags
        for dataset in self.datasets:
            dataset.is_active = False

        # Set new active dataset
        for dataset in self.datasets:
            if dataset.id == dataset_id:
                dataset.is_active = True
                self.active_dataset_id = dataset_id
                return

        raise KeyError(f"Dataset {dataset_id} not found in session")

    def get_active_dataset(self) -> Dataset | None:
        """Get currently active dataset."""
        for dataset in self.datasets:
            if dataset.is_active:
                return dataset
        return None

    def get_dataset_by_id(self, dataset_id: UUID) -> Dataset | None:
        """Get dataset by ID."""
        for dataset in self.datasets:
            if dataset.id == dataset_id:
                return dataset
        return None

    def enable_split_pane(self, dataset_id_1: UUID, dataset_id_2: UUID) -> None:
        """Enable split pane mode."""
        if dataset_id_1 == dataset_id_2:
            raise ValueError("Cannot use same dataset for split pane")

        # Verify datasets exist
        ds1 = self.get_dataset_by_id(dataset_id_1)
        ds2 = self.get_dataset_by_id(dataset_id_2)

        if not ds1 or not ds2:
            raise ValueError("Both datasets must exist for split pane")

        self.split_pane_enabled = True
        self.split_pane_datasets = (dataset_id_1, dataset_id_2)

    def disable_split_pane(self) -> None:
        """Disable split pane mode."""
        self.split_pane_enabled = False
        self.split_pane_datasets = None
