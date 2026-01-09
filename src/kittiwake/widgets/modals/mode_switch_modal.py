"""Mode switch prompt modal for handling lazy→eager transitions."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ModeSwitchPromptModal(ModalScreen[str | None]):
    """Modal for prompting user when switching from lazy→eager mode with queued operations.

    Features:
    - 3 choices: Execute All, Clear All, Cancel
    - Keyboard shortcuts: 1/E for Execute, 2/C for Clear, Esc/3 for Cancel
    - Returns choice string or None on cancel

    Returns:
        "execute" - Execute all queued operations then switch
        "clear" - Clear all queued operations then switch
        None - Cancel mode switch
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("1", "execute", "Execute All"),
        Binding("e", "execute", "Execute All"),
        Binding("2", "clear", "Clear All"),
        Binding("c", "clear", "Clear All"),
        Binding("3", "cancel", "Cancel"),
    ]

    CSS = """
    ModeSwitchPromptModal {
        align: center middle;
    }

    #mode_switch_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $warning;
        padding: 1 2;
    }

    #mode_switch_title {
        text-align: center;
        text-style: bold;
        background: $warning;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    #mode_switch_message {
        text-align: center;
        padding: 1 2;
        margin-bottom: 1;
    }

    .mode-switch-button {
        width: 1fr;
        margin: 0 1;
    }

    #mode_switch_buttons {
        height: auto;
        width: 100%;
        align: center middle;
        padding: 1 0;
    }

    #mode_switch_hint {
        text-align: center;
        color: $text-muted;
        padding: 1;
    }
    """

    def __init__(self, queued_count: int = 0, **kwargs):
        """Initialize mode switch prompt modal.

        Args:
            queued_count: Number of queued operations
        """
        super().__init__(**kwargs)
        self.queued_count = queued_count

    def compose(self) -> ComposeResult:
        """Create mode switch prompt content."""
        with Container(id="mode_switch_dialog"):
            yield Static("Switch to Eager Mode?", id="mode_switch_title")

            with Vertical(id="mode_switch_content"):
                yield Label(
                    f"You have {self.queued_count} queued operation(s).\n"
                    "What would you like to do?",
                    id="mode_switch_message"
                )

                with Vertical(id="mode_switch_buttons"):
                    yield Button(
                        "1. Execute All & Switch",
                        id="execute_button",
                        variant="success",
                        classes="mode-switch-button"
                    )
                    yield Button(
                        "2. Clear All & Switch",
                        id="clear_button",
                        variant="warning",
                        classes="mode-switch-button"
                    )
                    yield Button(
                        "3. Cancel",
                        id="cancel_button",
                        variant="default",
                        classes="mode-switch-button"
                    )

                yield Static(
                    "Shortcuts: 1/E = Execute, 2/C = Clear, 3/Esc = Cancel",
                    id="mode_switch_hint"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "execute_button":
            self.action_execute()
        elif event.button.id == "clear_button":
            self.action_clear()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    def action_execute(self) -> None:
        """Execute all queued operations then switch mode."""
        self.dismiss("execute")

    def action_clear(self) -> None:
        """Clear all queued operations then switch mode."""
        self.dismiss("clear")

    def action_cancel(self) -> None:
        """Cancel mode switch."""
        self.dismiss(None)
