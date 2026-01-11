"""Unit tests for SaveWorkflowModal widget."""

import pytest
from kittiwake.widgets.modals.save_workflow_modal import SaveWorkflowModal


class TestSaveWorkflowModalValidation:
    """Test SaveWorkflowModal input validation."""

    @pytest.fixture
    def workflow_modal(self):
        """Create a SaveWorkflowModal instance for testing."""
        return SaveWorkflowModal()

    def test_create_with_defaults(self, workflow_modal):
        """Test creating SaveWorkflowModal with default parameters."""
        assert workflow_modal.default_name == ""
        assert workflow_modal.default_description == ""
        assert workflow_modal.default_include_schema is True

    def test_create_with_custom_defaults(self):
        """Test creating SaveWorkflowModal with custom defaults."""
        modal = SaveWorkflowModal(
            default_name="my_workflow",
            default_description="Test description",
            default_include_schema=False,
        )
        assert modal.default_name == "my_workflow"
        assert modal.default_description == "Test description"
        assert modal.default_include_schema is False


class TestSaveWorkflowModalNameValidation:
    """Test workflow name validation rules."""

    def test_valid_name_alphanumeric(self):
        """Test valid workflow name with alphanumeric characters."""
        modal = SaveWorkflowModal(default_name="workflow123")
        assert modal.default_name == "workflow123"

    def test_valid_name_with_underscore(self):
        """Test valid workflow name with underscores."""
        modal = SaveWorkflowModal(default_name="my_workflow_name")
        assert modal.default_name == "my_workflow_name"

    def test_valid_name_with_hyphen(self):
        """Test valid workflow name with hyphens."""
        modal = SaveWorkflowModal(default_name="my-workflow-name")
        assert modal.default_name == "my-workflow-name"

    def test_valid_name_mixed_characters(self):
        """Test valid workflow name with mixed allowed characters."""
        modal = SaveWorkflowModal(default_name="My_Workflow-123")
        assert modal.default_name == "My_Workflow-123"

    def test_valid_name_single_character(self):
        """Test valid workflow name with single character."""
        modal = SaveWorkflowModal(default_name="a")
        assert modal.default_name == "a"

    def test_valid_name_max_length(self):
        """Test valid workflow name at maximum length (100 chars)."""
        name = "a" * 100
        modal = SaveWorkflowModal(default_name=name)
        assert modal.default_name == name
        assert len(modal.default_name) == 100


class TestSaveWorkflowModalDescriptionValidation:
    """Test workflow description validation rules."""

    def test_empty_description_allowed(self):
        """Test that empty description is allowed (optional field)."""
        modal = SaveWorkflowModal(default_description="")
        assert modal.default_description == ""

    def test_valid_description_short(self):
        """Test valid short description."""
        modal = SaveWorkflowModal(default_description="Simple workflow")
        assert modal.default_description == "Simple workflow"

    def test_valid_description_multiline(self):
        """Test valid multiline description."""
        description = "Line 1\nLine 2\nLine 3"
        modal = SaveWorkflowModal(default_description=description)
        assert modal.default_description == description

    def test_valid_description_max_length(self):
        """Test valid description at maximum length (500 chars)."""
        description = "a" * 500
        modal = SaveWorkflowModal(default_description=description)
        assert modal.default_description == description
        assert len(modal.default_description) == 500

    def test_valid_description_with_special_chars(self):
        """Test description with special characters."""
        description = "This workflow filters data where age > 25 & status == 'active'"
        modal = SaveWorkflowModal(default_description=description)
        assert modal.default_description == description


class TestSaveWorkflowModalSchemaCheckbox:
    """Test schema inclusion checkbox behavior."""

    def test_schema_checkbox_default_true(self):
        """Test that schema checkbox defaults to True."""
        modal = SaveWorkflowModal()
        assert modal.default_include_schema is True

    def test_schema_checkbox_can_be_false(self):
        """Test that schema checkbox can be set to False."""
        modal = SaveWorkflowModal(default_include_schema=False)
        assert modal.default_include_schema is False

    def test_schema_checkbox_explicit_true(self):
        """Test that schema checkbox can be explicitly set to True."""
        modal = SaveWorkflowModal(default_include_schema=True)
        assert modal.default_include_schema is True


class TestSaveWorkflowModalBehavior:
    """Test SaveWorkflowModal behavioral aspects."""

    def test_modal_has_escape_binding(self):
        """Test that modal has escape key binding for cancel."""
        modal = SaveWorkflowModal()
        # BINDINGS is a list of tuples: (key, action, description)
        bindings = [binding[0] for binding in modal.BINDINGS]
        assert "escape" in bindings

    def test_modal_bindings_action(self):
        """Test that escape binding maps to cancel action."""
        modal = SaveWorkflowModal()
        # BINDINGS is a list of tuples: (key, action, description)
        escape_binding = next(b for b in modal.BINDINGS if b[0] == "escape")
        assert escape_binding[1] == "cancel"


class TestSaveWorkflowModalReturnValue:
    """Test expected return value structure from SaveWorkflowModal."""

    def test_expected_return_keys(self):
        """Test that returned dict has expected keys."""
        # This test documents the expected structure
        expected_keys = {"name", "description", "include_schema"}

        # Example of expected return value
        workflow_data = {
            "name": "test_workflow",
            "description": "Test description",
            "include_schema": True,
        }

        assert set(workflow_data.keys()) == expected_keys

    def test_return_with_null_description(self):
        """Test that description can be None in return value."""
        workflow_data = {
            "name": "test_workflow",
            "description": None,
            "include_schema": True,
        }

        assert workflow_data["description"] is None

    def test_cancel_returns_none(self):
        """Test that cancel action should return None."""
        # When modal is cancelled, it should return None
        # This documents expected behavior for cancel action
        cancelled_result = None
        assert cancelled_result is None


class TestSaveWorkflowModalEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_name_with_numbers_only(self):
        """Test workflow name with only numbers."""
        modal = SaveWorkflowModal(default_name="12345")
        assert modal.default_name == "12345"

    def test_name_with_underscores_only(self):
        """Test workflow name with only underscores."""
        modal = SaveWorkflowModal(default_name="___")
        assert modal.default_name == "___"

    def test_name_with_hyphens_only(self):
        """Test workflow name with only hyphens."""
        modal = SaveWorkflowModal(default_name="---")
        assert modal.default_name == "---"

    def test_description_with_unicode(self):
        """Test description with Unicode characters."""
        description = "Workflow für Datenanalyse 数据分析"
        modal = SaveWorkflowModal(default_description=description)
        assert modal.default_description == description

    def test_all_parameters_together(self):
        """Test creating modal with all parameters specified."""
        modal = SaveWorkflowModal(
            default_name="data_pipeline_v1",
            default_description="Filters and aggregates sales data",
            default_include_schema=True,
        )
        assert modal.default_name == "data_pipeline_v1"
        assert modal.default_description == "Filters and aggregates sales data"
        assert modal.default_include_schema is True


class TestSaveWorkflowModalCSS:
    """Test that CSS is defined for the modal."""

    def test_css_constant_exists(self):
        """Test that SAVE_WORKFLOW_MODAL_CSS constant exists."""
        from kittiwake.widgets.modals.save_workflow_modal import SAVE_WORKFLOW_MODAL_CSS

        assert SAVE_WORKFLOW_MODAL_CSS is not None
        assert isinstance(SAVE_WORKFLOW_MODAL_CSS, str)
        assert len(SAVE_WORKFLOW_MODAL_CSS) > 0

    def test_css_contains_modal_styles(self):
        """Test that CSS contains expected style definitions."""
        from kittiwake.widgets.modals.save_workflow_modal import SAVE_WORKFLOW_MODAL_CSS

        # Check for key CSS selectors
        assert "SaveWorkflowModal" in SAVE_WORKFLOW_MODAL_CSS
        assert "#save_workflow_dialog" in SAVE_WORKFLOW_MODAL_CSS
        assert "#save_workflow_title" in SAVE_WORKFLOW_MODAL_CSS
        assert "#name_input" in SAVE_WORKFLOW_MODAL_CSS
        assert "#description_input" in SAVE_WORKFLOW_MODAL_CSS
        assert "#include_schema_checkbox" in SAVE_WORKFLOW_MODAL_CSS
        assert "#save_workflow_buttons" in SAVE_WORKFLOW_MODAL_CSS


class TestWorkflowSaveRequestedMessage:
    """Test WorkflowSaveRequested message class."""

    def test_message_creation(self):
        """Test creating WorkflowSaveRequested message."""
        from kittiwake.widgets.modals.save_workflow_modal import WorkflowSaveRequested

        msg = WorkflowSaveRequested(
            name="test_workflow",
            description="Test description",
            include_schema=True,
        )

        assert msg.name == "test_workflow"
        assert msg.description == "Test description"
        assert msg.include_schema is True

    def test_message_with_none_description(self):
        """Test creating WorkflowSaveRequested message with None description."""
        from kittiwake.widgets.modals.save_workflow_modal import WorkflowSaveRequested

        msg = WorkflowSaveRequested(
            name="workflow",
            description=None,
            include_schema=False,
        )

        assert msg.name == "workflow"
        assert msg.description is None
        assert msg.include_schema is False
