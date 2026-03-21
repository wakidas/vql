from __future__ import annotations

from textual.binding import Binding
from textual.widgets import DataTable

from tui_client.db.base import QueryResult


class ResultTable(DataTable):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("h", "cursor_left", "Left", show=False),
        Binding("l", "cursor_right", "Right", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
    ]

    DEFAULT_CSS = """
    ResultTable {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True

    def load_result(self, result: QueryResult) -> None:
        self.clear(columns=True)
        if not result.columns:
            return
        self.add_columns(*result.columns)
        self.add_rows(result.rows)
