from __future__ import annotations

from dataclasses import dataclass
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Checkbox, Input, Label, TextArea


_SENTINEL = object()

# これ以上の文字数、または改行を含む場合は複数行の TextArea で編集する。
MULTILINE_THRESHOLD = 80


class EditCellTextArea(TextArea):
    """複数行セル編集用。保存キーを TextArea の改行処理より先に扱う。"""

    async def _on_key(self, event: events.Key) -> None:
        # 多くのターミナル（特に macOS）では Ctrl+Enter が Enter と同一に届くため、
        # モーダルの Binding だけでは保存できない。ここで明示的に拾う。
        if event.key in ("ctrl+enter", "ctrl+s"):
            event.stop()
            event.prevent_default()
            await self.app.run_action("submit_edit", self.screen)
            return
        await super()._on_key(event)


@dataclass
class EditResult:
    value: str | None


class EditCellModal(ModalScreen[EditResult | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("ctrl+s", "submit_edit", "Save", show=True, priority=True),
        Binding("ctrl+enter", "submit_edit", "Save", show=False, priority=True),
    ]

    DEFAULT_CSS = """
    EditCellModal {
        align: center middle;
    }
    #edit-dialog {
        width: 60;
        height: auto;
        max-height: 16;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #edit-dialog.multiline {
        width: 80;
        max-height: 28;
    }
    #edit-dialog Label {
        margin-bottom: 1;
    }
    #edit-input {
        margin-bottom: 1;
    }
    TextArea#edit-input {
        height: 12;
        min-height: 6;
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

    def _is_multiline(self) -> bool:
        if self.current_value is None:
            return False
        s = str(self.current_value)
        return len(s) >= MULTILINE_THRESHOLD or "\n" in s

    def compose(self) -> ComposeResult:
        multiline = self._is_multiline()
        label = f"Edit: [bold]{self.column_name}[/bold]"
        if multiline:
            label += "  [dim](Ctrl+S で保存 / Enter で改行)[/dim]"
        with Vertical(id="edit-dialog", classes="multiline" if multiline else ""):
            yield Label(label)
            if multiline:
                yield EditCellTextArea(
                    text="" if self.current_value is None else str(self.current_value),
                    id="edit-input",
                    disabled=self.current_value is None,
                )
            else:
                yield Input(
                    value="" if self.current_value is None else str(self.current_value),
                    id="edit-input",
                    disabled=self.current_value is None,
                )
            yield Checkbox("NULL", value=self.current_value is None, id="null-check")

    def on_mount(self) -> None:
        self.query_one("#edit-input").focus()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        w = self.query_one("#edit-input")
        w.disabled = event.value
        if not event.value:
            w.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    def _submit(self) -> None:
        is_null = self.query_one("#null-check", Checkbox).value
        if is_null:
            self.dismiss(EditResult(value=None))
        else:
            w = self.query_one("#edit-input")
            text = w.text if isinstance(w, TextArea) else w.value
            self.dismiss(EditResult(value=text))

    def action_submit_edit(self) -> None:
        self._submit()

    def action_cancel(self) -> None:
        self.dismiss(None)
