"""Unit tests for KittiwakeApp.notify_error() method."""

import pytest
from unittest.mock import MagicMock, patch
from kittiwake.app import KittiwakeApp
from kittiwake.models.dataset_session import DatasetSession


class TestAppNotifyError:
    """Test KittiwakeApp.notify_error() method."""

    @pytest.fixture
    def app(self):
        """Create a KittiwakeApp instance for testing."""
        session = DatasetSession()
        return KittiwakeApp(session)

    def test_notify_error_with_clipboard_success(self, app):
        """Test notify_error copies to clipboard successfully."""
        # Mock the clipboard and notify methods
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        error_msg = "Test error message"
        app.notify_error(error_msg, title="Test Error")

        # Verify clipboard was called
        app.copy_to_clipboard.assert_called_once_with(error_msg)

        # Verify notify was called with the right parameters
        assert app.notify.call_count == 1
        call_args = app.notify.call_args

        # Check the message includes the copied indicator
        assert error_msg in call_args[0][0]
        assert "✓ Copied to clipboard" in call_args[0][0]
        assert "click to dismiss" in call_args[0][0]

        # Check keyword arguments
        assert call_args[1]["severity"] == "error"
        assert call_args[1]["timeout"] == 30
        assert call_args[1]["title"] == "Test Error"
        assert call_args[1]["markup"] is True

    def test_notify_error_clipboard_failure(self, app):
        """Test notify_error handles clipboard failure gracefully."""
        # Mock clipboard to raise an exception
        app.copy_to_clipboard = MagicMock(
            side_effect=Exception("Clipboard unavailable")
        )
        app.notify = MagicMock()

        error_msg = "Test error message"
        app.notify_error(error_msg, title="Test Error")

        # Verify clipboard was attempted
        app.copy_to_clipboard.assert_called_once_with(error_msg)

        # Verify notify was still called but without "copied" indicator
        assert app.notify.call_count == 1
        call_args = app.notify.call_args

        # Check the message does NOT include "copied" indicator
        assert error_msg in call_args[0][0]
        assert "✓ Copied to clipboard" not in call_args[0][0]
        assert "click to dismiss" in call_args[0][0]

    def test_notify_error_without_clipboard(self, app):
        """Test notify_error with copy_to_clipboard=False."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        error_msg = "Test error message"
        app.notify_error(error_msg, title="Test Error", copy_to_clipboard=False)

        # Verify clipboard was NOT called
        app.copy_to_clipboard.assert_not_called()

        # Verify notify was called
        assert app.notify.call_count == 1
        call_args = app.notify.call_args

        # Check the message does not include "copied" indicator
        assert error_msg in call_args[0][0]
        assert "✓ Copied to clipboard" not in call_args[0][0]
        assert "click to dismiss" in call_args[0][0]

    def test_notify_error_default_title(self, app):
        """Test notify_error uses default title 'Error'."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        app.notify_error("Test message")

        # Verify notify was called with default title
        call_args = app.notify.call_args
        assert call_args[1]["title"] == "Error"

    def test_notify_error_custom_title(self, app):
        """Test notify_error accepts custom title."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        app.notify_error("Test message", title="Custom Title")

        # Verify notify was called with custom title
        call_args = app.notify.call_args
        assert call_args[1]["title"] == "Custom Title"

    def test_notify_error_long_message(self, app):
        """Test notify_error with long error message."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        long_msg = "A" * 500  # 500 character error
        app.notify_error(long_msg, title="Long Error")

        # Verify clipboard received the full message
        app.copy_to_clipboard.assert_called_once_with(long_msg)

        # Verify notify was called
        assert app.notify.call_count == 1

    def test_notify_error_with_special_characters(self, app):
        """Test notify_error handles special characters."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        error_msg = "Error: <script>alert('xss')</script>"
        app.notify_error(error_msg, title="XSS Test")

        # Verify clipboard got the raw message
        app.copy_to_clipboard.assert_called_once_with(error_msg)

        # Verify notify was called (markup will handle escaping)
        assert app.notify.call_count == 1
        call_args = app.notify.call_args
        assert error_msg in call_args[0][0]

    def test_notify_error_preserves_timeout(self, app):
        """Test that notify_error always uses 30 second timeout."""
        app.copy_to_clipboard = MagicMock()
        app.notify = MagicMock()

        app.notify_error("Test message")

        call_args = app.notify.call_args
        assert call_args[1]["timeout"] == 30
