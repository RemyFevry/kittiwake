"""Workflow service for managing reusable operation sequences."""

from typing import Any

import narwhals as nw

from ..models.dataset import Dataset
from ..models.operations import Operation, OperationError
from ..models.workflow import Workflow
from .persistence import WorkflowRepository


class WorkflowService:
    """Service for managing workflows."""

    def __init__(self, repository: WorkflowRepository | None = None):
        """Initialize workflow service.

        Args:
            repository: WorkflowRepository instance (created if None)

        """
        self.repository = repository or WorkflowRepository()

    def save_workflow(
        self,
        name: str,
        description: str | None,
        operations: list[Operation],
        include_schema: bool,
        dataset_schema: dict[str, str] | None = None,
    ) -> tuple[int | None, str | None, str | None]:
        """Save workflow to database.

        Args:
            name: Workflow name
            description: Optional workflow description
            operations: List of operations to save
            include_schema: Whether to include dataset schema for validation
            dataset_schema: Dataset schema (column_name -> dtype)

        Returns:
            Tuple of (workflow_id, versioned_name_if_changed, error_message)
            - workflow_id: The ID of the saved workflow
            - versioned_name_if_changed: The auto-versioned name if original was duplicate
            - error_message: Error message if save failed, None otherwise

        """
        try:
            required_schema = None
            if include_schema and dataset_schema:
                required_schema = dataset_schema

            workflow_data = {
                "name": name,
                "description": description,
                "operation_count": len(operations),
                "operations": [op.to_dict() for op in operations],
                "required_schema": required_schema,
            }

            workflow_id, versioned_name = self.repository.save(workflow_data)
            return (workflow_id, versioned_name, None)

        except Exception as e:
            return (None, None, f"Failed to save workflow: {e}")

    def load_workflow(self, workflow_id: int) -> Workflow | None:
        """Load workflow from database.

        Args:
            workflow_id: ID of the workflow to load

        Returns:
            Workflow instance or None if not found

        """
        try:
            workflow_data = self.repository.load_by_id(workflow_id)
            if workflow_data is None:
                return None

            operations = [
                Operation.from_dict(op_data) for op_data in workflow_data["operations"]
            ]

            return Workflow(
                name=workflow_data["name"],
                description=workflow_data.get("description"),
                operations=operations,
                required_schema=workflow_data.get("required_schema"),
                created_at=str(workflow_data["created_at"]),
                modified_at=str(workflow_data["modified_at"]),
            )

        except Exception:
            return None

    def apply_workflow(
        self,
        workflow: Workflow,
        dataset: Dataset,
        validate_schema: bool = True,
    ) -> tuple[int, int, list[dict[str, Any]]]:
        """Apply workflow operations to dataset.

        Args:
            workflow: Workflow to apply
            dataset: Target dataset
            validate_schema: Whether to validate schema before applying

        Returns:
            Tuple of (success_count, failed_count, errors)
            - success_count: Number of operations applied successfully
            - failed_count: Number of operations that failed
            - errors: List of error dicts with operation index and message

        """
        success_count = 0
        failed_count = 0
        errors = []

        if validate_schema and workflow.required_schema:
            is_valid, error_msg = workflow.validate_schema(dataset.schema)
            if not is_valid:
                errors.append(
                    {
                        "operation_index": -1,
                        "operation_display": "Schema validation",
                        "error_message": error_msg,
                    }
                )
                return (0, 0, errors)

        # Apply operations in sequence
        for idx, operation in enumerate(workflow.operations):
            try:
                # Validate operation against dataset
                frame = dataset.current_frame or dataset.original_frame or dataset.frame
                if frame is None:
                    raise OperationError("No dataset loaded")

                # Create lazy sample for validation
                sample = frame.head(10).collect()
                lazy_sample = nw.from_native(sample).lazy()
                is_valid, validation_error = operation.validate(lazy_sample)

                if not is_valid:
                    errors.append(
                        {
                            "operation_index": idx,
                            "operation_display": operation.display,
                            "error_message": validation_error or "Validation failed",
                        }
                    )
                    failed_count += 1
                    continue

                # Apply operation
                dataset._execute_operation(operation)
                success_count += 1

            except Exception as e:
                error_msg = str(e)
                errors.append(
                    {
                        "operation_index": idx,
                        "operation_display": operation.display,
                        "error_message": error_msg,
                    }
                )
                failed_count += 1

        return (success_count, failed_count, errors)

    def list_workflows(self) -> list[dict[str, Any]]:
        """List all saved workflows.

        Returns:
            List of workflow metadata dicts

        """
        try:
            return self.repository.list_all()
        except Exception:
            return []

    def delete_workflow(self, workflow_id: int) -> tuple[bool, str | None]:
        """Delete workflow by ID.

        Args:
            workflow_id: ID of workflow to delete

        Returns:
            Tuple of (success, error_message)

        """
        try:
            success = self.repository.delete(workflow_id)
            return (success, None if success else "Workflow not found")
        except Exception as e:
            return (False, f"Failed to delete workflow: {e}")

    def update_workflow(
        self,
        workflow_id: int,
        name: str,
        description: str | None,
        operations: list[Operation],
        required_schema: dict[str, str] | None = None,
    ) -> tuple[bool, str | None]:
        """Update workflow.

        Args:
            workflow_id: ID of workflow to update
            name: New workflow name
            description: New workflow description
            operations: Updated list of operations
            required_schema: Updated required schema

        Returns:
            Tuple of (success, error_message)

        """
        try:
            workflow_data = {
                "name": name,
                "description": description,
                "operation_count": len(operations),
                "operations": [op.to_dict() for op in operations],
                "required_schema": required_schema,
            }

            success = self.repository.update(workflow_id, workflow_data)
            return (success, None if success else "Workflow not found")

        except Exception as e:
            return (False, f"Failed to update workflow: {e}")

    @staticmethod
    def extract_schema(dataset: Dataset) -> dict[str, str]:
        """Extract schema from dataset.

        Args:
            dataset: Dataset to extract schema from

        Returns:
            Schema dict mapping column names to dtype strings

        """
        schema = {}

        try:
            frame = dataset.original_frame or dataset.frame
            if frame is None:
                return schema

            collected = frame.collect()
            schema = {col: str(dtype) for col, dtype in collected.schema.items()}
        except Exception:
            pass

        return schema

    @staticmethod
    def validate_operation(
        operation: Operation, dataset: Dataset
    ) -> tuple[bool, str | None]:
        """Validate operation against dataset schema.

        Args:
            operation: Operation to validate
            dataset: Target dataset

        Returns:
            Tuple of (is_valid, error_message)

        """
        try:
            frame = dataset.current_frame or dataset.original_frame or dataset.frame
            if frame is None:
                return False, "No dataset loaded"

            # Try on sample data
            sample = frame.head(10).collect()
            lazy_sample = nw.from_native(sample).lazy()
            return operation.validate(lazy_sample)
        except Exception as e:
            return False, str(e)
