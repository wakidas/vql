from __future__ import annotations

from textual.binding import Binding
from textual.message import Message
from textual.widgets import TextArea


class SqlEditor(TextArea):
    BINDINGS = [
        Binding("ctrl+r", "execute_sql", "Run SQL", show=True),
    ]

    DEFAULT_CSS = """
    SqlEditor {
        height: 1fr;
        border: none;
    }
    """

    class ExecuteRequested(Message):
        def __init__(self, sql_text: str) -> None:
            super().__init__()
            self.sql_text = sql_text

    def action_execute_sql(self) -> None:
        text = self.text.strip()
        if text:
            self.post_message(self.ExecuteRequested(text))
