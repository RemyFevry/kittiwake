"""Async and worker utilities for Textual."""

import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps


def async_to_worker(func: Callable) -> Callable:
    """Wrap async function for execution in worker thread.

    Args:
        func: Async function to wrap

    Returns:
        Wrapped async function

    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Execute the wrapped async function."""
        # For now, just run the function
        # TODO: Integrate with Textual workers properly
        return await func(*args, **kwargs)

    return wrapper


def run_in_executor(func: Callable, *args, **kwargs) -> Coroutine:
    """Run function in executor (non-blocking)."""
    return asyncio.get_event_loop().run_in_executor(None, lambda: func(*args, **kwargs))


class CancellableProgressTracker:
    """Progress tracker with cancellation support for long-running operations."""

    def __init__(self):
        self._progress = 0.0
        self._message = ""
        self._callbacks = []
        self._cancelled = False

    def set_progress(self, value: float, message: str = ""):
        """Update progress value.

        Args:
            value: Progress value between 0.0 and 1.0
            message: Optional status message
        """
        if self._cancelled:
            return

        self._progress = max(0.0, min(1.0, value))
        if message:
            self._message = message

        # Notify callbacks
        for callback in self._callbacks:
            callback(self._progress, self._message)

    def get_progress(self) -> tuple[float, str]:
        """Get current progress.

        Returns:
            Tuple of (progress, message)
        """
        return self._progress, self._message

    def add_callback(self, callback: Callable[[float, str], None]):
        """Add progress update callback.

        Args:
            callback: Function that takes (progress, message)
        """
        self._callbacks.append(callback)

    def cancel(self):
        """Cancel the operation."""
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled


class ProgressTracker:
    """Simple progress tracker for long-running operations."""

    def __init__(self):
        self._progress = 0.0
        self._message = ""
        self._callbacks = []

    def set_progress(self, value: float, message: str = ""):
        """Update progress value."""
        self._progress = max(0.0, min(1.0, value))
        if message:
            self._message = message

        # Notify callbacks
        for callback in self._callbacks:
            callback(self._progress, self._message)

    def get_progress(self) -> tuple[float, str]:
        """Get current progress."""
        return self._progress, self._message

    def add_callback(self, callback: Callable[[float, str], None]):
        """Add progress update callback."""
        self._callbacks.append(callback)
