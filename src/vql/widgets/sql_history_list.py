from __future__ import annotations

from textual.binding import Binding
from textual.widgets import ListView, ListItem, Label


class SqlHistoryList(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    DEFAULT_CSS = """
    SqlHistoryList {
        height: 1fr;
        border: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._entries: list[str] = []

    def add_entry(self, sql_text: str) -> None:
        self._entries.insert(0, sql_text)
        truncated = sql_text.replace("\n", " ")
        if len(truncated) > 60:
            truncated = truncated[:57] + "..."
        self.insert(0, [ListItem(Label(truncated))])

    def get_selected_sql(self) -> str | None:
        idx = self.index
        if idx is not None and idx < len(self._entries):
            return self._entries[idx]
        return None
