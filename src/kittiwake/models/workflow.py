"""Workflow entity for reusable operation sequences."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from .operations import Operation


@dataclass
class Workflow:
    """Represents a reusable workflow (sequence of operations)."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str | None = None
    operations: list[Operation] = field(default_factory=list)
    required_schema: dict[str, str] | None = None  # Optional schema for validation
    created_at: str | None = None
    modified_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize workflow to dict for persistence."""
        return {
            "name": self.name,
            "description": self.description,
            "operations": [op.to_dict() for op in self.operations],
            "required_schema": self.required_schema,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Workflow":
        """Deserialize workflow from dict."""
        operations = [
            Operation.from_dict(op_data) for op_data in data.get("operations", [])
        ]
        return cls(
            name=data["name"],
            description=data.get("description"),
            operations=operations,
            required_schema=data.get("required_schema"),
        )

    def validate_schema(
        self, dataset_schema: dict[str, str]
    ) -> tuple[bool, str | None]:
        """Validate that dataset schema is compatible with workflow requirements.

        Args:
            dataset_schema: Schema of target dataset (column_name -> dtype)

        Returns:
            Tuple of (is_valid, error_message)

        """
        if self.required_schema is None:
            # No schema requirements, always valid
            return True, None

        # Check that all required columns exist in dataset
        missing_cols = []
        type_mismatches = []

        for col_name, required_type in self.required_schema.items():
            if col_name not in dataset_schema:
                missing_cols.append(col_name)
            elif dataset_schema[col_name] != required_type:
                type_mismatches.append(
                    f"{col_name} (expected {required_type}, got {dataset_schema[col_name]})"
                )

        if missing_cols:
            return False, f"Missing columns: {', '.join(missing_cols)}"

        if type_mismatches:
            return False, f"Type mismatches: {', '.join(type_mismatches)}"

        return True, None
