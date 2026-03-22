from __future__ import annotations

from textual.binding import Binding
from textual.message import Message
from textual.widgets import Tree

from tui_client.db.base import DBAdapter, Table


class SchemaTree(Tree[Table]):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
        Binding("slash", "start_search", "Search", show=False),
    ]

    class SearchModeChanged(Message):
        def __init__(self, active: bool) -> None:
            super().__init__()
            self.active = active

    def __init__(self, **kwargs) -> None:
        super().__init__("Tables", **kwargs)
        self._all_tables: list[Table] = []

    async def load_tables(self, adapter: DBAdapter) -> None:
        self.clear()
        tables = await adapter.get_tables("public")
        self._all_tables = list(tables)
        for table in tables:
            self.root.add_leaf(f"\U0001f5c3 {table.name}", data=table)
        self.root.expand()

    def filter_tables(self, query: str) -> None:
        self.clear()
        query_lower = query.lower()
        for table in self._all_tables:
            if query_lower in table.name.lower():
                self.root.add_leaf(f"\U0001f5c3 {table.name}", data=table)
        self.root.expand()

    def action_start_search(self) -> None:
        self.post_message(self.SearchModeChanged(active=True))
