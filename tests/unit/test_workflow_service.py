"""Unit tests for workflow service."""

import narwhals as nw
import pytest

from kittiwake.models.dataset import Dataset
from kittiwake.models.operations import Operation
from kittiwake.models.workflow import Workflow
from kittiwake.services.workflow import WorkflowService


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    import polars as pl

    df = pl.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "is_active": [True, False, True],
        }
    )
    return nw.from_native(df).lazy()


@pytest.fixture
def sample_dataset(sample_dataframe):
    """Create a sample dataset for testing."""
    return Dataset(
        name="test_dataset",
        source="test.csv",
        backend="polars",
        frame=sample_dataframe,
        original_frame=sample_dataframe,
        row_count=3,
    )


@pytest.fixture
def sample_operations():
    """Create sample operations for testing."""
    return [
        Operation(
            code='df = df.filter(nw.col("age") > 25)',
            display="Filter age > 25",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 25},
        ),
        Operation(
            code='df = df.select(["name", "age"])',
            display="Select columns",
            operation_type="select",
            params={"columns": ["name", "age"]},
        ),
    ]


@pytest.fixture(autouse=True)
def clear_database():
    """Clear workflow database before each test."""
    from pathlib import Path

    import duckdb

    try:
        db_path = Path.home() / ".kittiwake" / "analyses.db"
        if db_path.exists():
            conn = duckdb.connect(str(db_path))
            try:
                conn.execute("DELETE FROM workflows")
            except Exception:
                pass
            conn.close()
    except Exception:
        pass


@pytest.fixture
def workflow_service():
    """Create workflow service instance."""
    return WorkflowService()


class TestWorkflowService:
    """Tests for WorkflowService class."""

    def test_save_workflow_with_schema(
        self, workflow_service, sample_operations, sample_dataset
    ):
        """Test saving workflow with schema included."""
        schema = workflow_service.extract_schema(sample_dataset)
        workflow_id, versioned_name, error = workflow_service.save_workflow(
            name="test_workflow",
            description="Test workflow",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=schema,
        )

        assert workflow_id is not None
        assert versioned_name is None
        assert error is None

    def test_save_workflow_without_schema(self, workflow_service, sample_operations):
        """Test saving workflow without schema."""
        workflow_id, versioned_name, error = workflow_service.save_workflow(
            name="test_workflow_no_schema",
            description="Test workflow without schema",
            operations=sample_operations,
            include_schema=False,
        )

        assert workflow_id is not None
        assert versioned_name is None
        assert error is None

    def test_save_workflow_duplicate_name(
        self, workflow_service, sample_operations, sample_dataset
    ):
        """Test saving workflow with duplicate name triggers auto-versioning."""
        name = "duplicate_workflow"
        schema = workflow_service.extract_schema(sample_dataset)

        # Save first workflow
        workflow_id1, _, error1 = workflow_service.save_workflow(
            name=name,
            description="First workflow",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=schema,
        )

        assert workflow_id1 is not None
        assert error1 is None

        # Save second workflow with same name
        workflow_id2, versioned_name, error2 = workflow_service.save_workflow(
            name=name,
            description="Second workflow",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=schema,
        )

        assert workflow_id2 is not None
        assert versioned_name is not None
        assert versioned_name.startswith(f"{name}_")
        assert error2 is None

    def test_load_workflow(self, workflow_service, sample_operations, sample_dataset):
        """Test loading workflow by ID."""
        # Save workflow first
        schema = workflow_service.extract_schema(sample_dataset)
        workflow_id, _, _ = workflow_service.save_workflow(
            name="load_test_workflow",
            description="Workflow for loading test",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=schema,
        )

        # Load workflow
        workflow = workflow_service.load_workflow(workflow_id)

        assert workflow is not None
        assert workflow.name == "load_test_workflow"
        assert workflow.description == "Workflow for loading test"
        assert len(workflow.operations) == 2
        assert workflow.required_schema is not None

    def test_load_nonexistent_workflow(self, workflow_service):
        """Test loading non-existent workflow returns None."""
        workflow = workflow_service.load_workflow(99999)
        assert workflow is None

    def test_apply_workflow_success(
        self, workflow_service, sample_operations, sample_dataset
    ):
        """Test applying workflow to dataset successfully."""
        workflow = Workflow(
            name="test_apply",
            operations=sample_operations,
            required_schema=sample_dataset.schema,
        )

        success_count, failed_count, errors = workflow_service.apply_workflow(
            workflow, sample_dataset, validate_schema=True
        )

        assert success_count == 2
        assert failed_count == 0
        assert len(errors) == 0

    def test_apply_workflow_with_schema_validation_failure(
        self, workflow_service, sample_operations, sample_dataset
    ):
        """Test applying workflow when schema doesn't match."""
        workflow = Workflow(
            name="test_schema_fail",
            operations=sample_operations,
            required_schema={"nonexistent_column": "Int64"},
        )

        success_count, failed_count, errors = workflow_service.apply_workflow(
            workflow, sample_dataset, validate_schema=True
        )

        assert success_count == 0
        assert failed_count == 0
        assert len(errors) == 1
        assert errors[0]["operation_index"] == -1
        assert "Missing columns" in errors[0]["error_message"]

    def test_apply_workflow_without_schema_validation(
        self, workflow_service, sample_operations, sample_dataset
    ):
        """Test applying workflow without schema validation."""
        workflow = Workflow(
            name="test_no_validation",
            operations=sample_operations,
            required_schema={"nonexistent_column": "Int64"},
        )

        success_count, failed_count, errors = workflow_service.apply_workflow(
            workflow, sample_dataset, validate_schema=False
        )

        # Operations applied without schema validation
        assert success_count == 2
        assert failed_count == 0
        assert len(errors) == 0

    def test_apply_workflow_with_operation_failure(
        self, workflow_service, sample_dataset
    ):
        """Test applying workflow with a failing operation."""
        invalid_operations = [
            Operation(
                code="df = df.filter(invalid_syntax_here)",
                display="Filter with syntax error",
                operation_type="filter",
                params={"column": "age", "operator": ">", "value": 25},
            ),
        ]

        schema = workflow_service.extract_schema(sample_dataset)
        workflow = Workflow(
            name="test_op_fail",
            operations=invalid_operations,
            required_schema=schema,
        )

        success_count, failed_count, errors = workflow_service.apply_workflow(
            workflow, sample_dataset, validate_schema=False
        )

        assert success_count == 0
        assert failed_count == 1
        assert len(errors) == 1
        assert errors[0]["operation_index"] == 0

    def test_list_workflows(self, workflow_service, sample_operations, sample_dataset):
        """Test listing all workflows."""
        # Save multiple workflows
        workflow_id1, _, _ = workflow_service.save_workflow(
            name="workflow_1",
            description="First workflow",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=sample_dataset.schema,
        )

        workflow_id2, _, _ = workflow_service.save_workflow(
            name="workflow_2",
            description="Second workflow",
            operations=sample_operations,
            include_schema=False,
        )

        # List workflows
        workflows = workflow_service.list_workflows()

        assert len(workflows) >= 2
        workflow_names = [w["name"] for w in workflows]
        assert "workflow_1" in workflow_names
        assert "workflow_2" in workflow_names

    def test_delete_workflow(self, workflow_service, sample_operations, sample_dataset):
        """Test deleting workflow."""
        # Save workflow
        workflow_id, _, _ = workflow_service.save_workflow(
            name="delete_test_workflow",
            description="Workflow to delete",
            operations=sample_operations,
            include_schema=True,
            dataset_schema=sample_dataset.schema,
        )

        # Delete workflow
        success, error = workflow_service.delete_workflow(workflow_id)

        assert success is True
        assert error is None

        # Verify workflow is deleted
        deleted_workflow = workflow_service.load_workflow(workflow_id)
        assert deleted_workflow is None

    def test_delete_nonexistent_workflow(self, workflow_service):
        """Test deleting non-existent workflow."""
        success, error = workflow_service.delete_workflow(99999)
        assert success is False
        assert "not found" in error

    def test_update_workflow(self, workflow_service, sample_operations, sample_dataset):
        """Test updating workflow."""
        schema = workflow_service.extract_schema(sample_dataset)
        # Save initial workflow
        workflow_id, _, _ = workflow_service.save_workflow(
            name="update_test_workflow",
            description="Original description",
            operations=sample_operations[:1],
            include_schema=True,
            dataset_schema=schema,
        )

        # Update workflow
        updated_operations = [
            Operation(
                code='df = df.filter(nw.col("age") < 30)',
                display="Filter age < 30",
                operation_type="filter",
                params={"column": "age", "operator": "<", "value": 30},
            ),
        ]

        success, error = workflow_service.update_workflow(
            workflow_id=workflow_id,
            name="updated_workflow_name",
            description="Updated description",
            operations=updated_operations,
            required_schema=schema,
        )

        assert success is True
        assert error is None

        # Verify workflow was updated
        workflow = workflow_service.load_workflow(workflow_id)
        assert workflow.name == "updated_workflow_name"
        assert workflow.description == "Updated description"
        assert len(workflow.operations) == 1

    def test_update_nonexistent_workflow(self, workflow_service, sample_operations):
        """Test updating non-existent workflow."""
        success, error = workflow_service.update_workflow(
            workflow_id=99999,
            name="nonexistent",
            description="This doesn't exist",
            operations=sample_operations,
        )

        assert success is False
        assert "not found" in error

    def test_extract_schema(self, workflow_service, sample_dataset):
        """Test extracting schema from dataset."""
        schema = workflow_service.extract_schema(sample_dataset)

        assert isinstance(schema, dict)
        assert len(schema) > 0
        assert "id" in schema
        assert "name" in schema
        assert "age" in schema
        assert "is_active" in schema

    def test_extract_schema_from_empty_dataset(self, workflow_service):
        """Test extracting schema from dataset with no frame."""
        empty_dataset = Dataset(name="empty", source="", backend="")
        schema = workflow_service.extract_schema(empty_dataset)

        assert schema == {}

    def test_validate_operation(self, workflow_service, sample_dataset):
        """Test validating operation against dataset."""
        operation = Operation(
            code='df = df.filter(nw.col("age") > 20)',
            display="Filter age > 20",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 20},
        )

        is_valid, error_msg = workflow_service.validate_operation(
            operation, sample_dataset
        )

        assert is_valid is True
        assert error_msg is None

    def test_validate_invalid_operation(self, workflow_service, sample_dataset):
        """Test validating invalid operation against dataset."""
        operation = Operation(
            code="df = df.filter(invalid_syntax_here)",
            display="Filter with syntax error",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 20},
        )

        is_valid, error_msg = workflow_service.validate_operation(
            operation, sample_dataset
        )

        assert is_valid is False
        assert error_msg is not None

    def test_validate_operation_no_dataset(self, workflow_service):
        """Test validating operation against dataset with no frame."""
        empty_dataset = Dataset(name="empty", source="", backend="")

        operation = Operation(
            code='df = df.filter(nw.col("age") > 20)',
            display="Filter age > 20",
            operation_type="filter",
            params={"column": "age", "operator": ">", "value": 20},
        )

        is_valid, error_msg = workflow_service.validate_operation(
            operation, empty_dataset
        )

        assert is_valid is False
        assert "No dataset loaded" in error_msg
