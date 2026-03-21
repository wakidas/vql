from __future__ import annotations

from textual.binding import Binding
from textual.widgets import Tree

from tui_client.db.base import DBAdapter, Table


class SchemaTree(Tree[Table]):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__("Tables", **kwargs)
        self.show_root = False

    async def load_tables(self, adapter: DBAdapter) -> None:
        self.clear()
        tables = await adapter.get_tables("public")
        for table in tables:
            self.root.add_leaf(table.name, data=table)
        self.root.expand()
