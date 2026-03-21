from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Tree
from psycopg import sql

from tui_client.db.base import DBAdapter
from tui_client.widgets.schema_tree import SchemaTree
from tui_client.widgets.result_table import ResultTable


class MainScreen(Screen):
    BINDINGS = [
        Binding("h", "focus_tree", "Tree", show=True),
        Binding("l", "focus_table", "Table", show=True),
        Binding("c", "connect", "Connect", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    MainScreen {
        layout: horizontal;
    }
    #sidebar {
        width: 30;
        dock: left;
        border-right: thick $accent;
    }
    #main {
        width: 1fr;
    }
    #status {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, adapter: DBAdapter | None = None) -> None:
        super().__init__()
        self.adapter = adapter

    def compose(self) -> ComposeResult:
        yield Header()
        yield SchemaTree(id="sidebar")
        yield ResultTable(id="main")
        yield Static("No connection", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        if self.adapter:
            await self._load_schema()

    async def _load_schema(self) -> None:
        tree = self.query_one(SchemaTree)
        await tree.load_tables(self.adapter)
        self.query_one("#status", Static).update(f"Connected")

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        table = event.node.data
        if table is None or self.adapter is None:
            return
        query = sql.SQL("SELECT * FROM {}.{} LIMIT 100").format(
            sql.Identifier(table.schema),
            sql.Identifier(table.name),
        )
        try:
            result = await self.adapter.execute(query)
        except Exception as e:
            self.notify(f"Query failed: {e}", severity="error")
            return
        self.query_one(ResultTable).load_result(result)

    def action_focus_tree(self) -> None:
        self.query_one(SchemaTree).focus()

    def action_focus_table(self) -> None:
        self.query_one(ResultTable).focus()

    def action_connect(self) -> None:
        from tui_client.screens.connect import ConnectionList
        self.app.push_screen(ConnectionList(), self._on_connect)

    def _on_connect(self, config) -> None:
        if config is not None:
            self.app.connect_to_db(config)

    async def action_refresh(self) -> None:
        if self.adapter:
            await self._load_schema()

    def action_quit(self) -> None:
        self.app.exit()
