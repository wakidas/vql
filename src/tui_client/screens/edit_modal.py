from __future__ import annotations

from dataclasses import dataclass
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Checkbox


_SENTINEL = object()


@dataclass
class EditResult:
    value: str | None


class EditCellModal(ModalScreen[EditResult | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    DEFAULT_CSS = """
    EditCellModal {
        align: center middle;
    }
    #edit-dialog {
        width: 60;
        height: auto;
        max-height: 16;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #edit-dialog Label {
        margin-bottom: 1;
    }
    #edit-input {
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        column_name: str,
        current_value: str | None,
    ) -> None:
        super().__init__()
        self.column_name = column_name
        self.current_value = current_value

    def compose(self) -> ComposeResult:
        with Vertical(id="edit-dialog"):
            yield Label(f"Edit: [bold]{self.column_name}[/bold]")
            yield Input(
                value="" if self.current_value is None else str(self.current_value),
                id="edit-input",
                disabled=self.current_value is None,
            )
            yield Checkbox("NULL", value=self.current_value is None, id="null-check")

    def on_mount(self) -> None:
        self.query_one("#edit-input", Input).focus()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        input_widget = self.query_one("#edit-input", Input)
        input_widget.disabled = event.value
        if not event.value:
            input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    def _submit(self) -> None:
        is_null = self.query_one("#null-check", Checkbox).value
        if is_null:
            self.dismiss(EditResult(value=None))
        else:
            text = self.query_one("#edit-input", Input).value
            self.dismiss(EditResult(value=text))

    def action_cancel(self) -> None:
        self.dismiss(None)
