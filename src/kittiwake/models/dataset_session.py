"""Session management for multiple datasets."""

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from .dataset import Dataset


@dataclass
class DatasetSession:
    """Manages collection of loaded datasets."""

    datasets: List[Dataset] = field(default_factory=list)
    active_dataset_id: Optional[UUID] = None
    max_datasets: int = 10
    split_pane_enabled: bool = False
    split_pane_datasets: Optional[tuple[UUID, UUID]] = None

    def add_dataset(self, dataset: Dataset) -> bool:
        """Add dataset to session."""
        if len(self.datasets) >= self.max_datasets:
            return False

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

        return True

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

    def get_active_dataset(self) -> Optional[Dataset]:
        """Get currently active dataset."""
        for dataset in self.datasets:
            if dataset.is_active:
                return dataset
        return None

    def get_dataset_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
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
