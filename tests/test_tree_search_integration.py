import pytest
from textual.app import App
from textual.widgets import Input

from tui_client.db.base import Table
from tui_client.screens.main import MainScreen
from tui_client.widgets.schema_tree import SchemaTree
from tui_client.widgets.result_table import ResultTable


class TreeSearchTestApp(App[None]):
    def on_mount(self) -> None:
        self.push_screen(MainScreen())


@pytest.mark.asyncio
async def test_tree_search_input_hidden_by_default():
    """tree-search-input should be hidden initially."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        search_input = app.screen.query_one("#tree-search-input", Input)
        assert search_input.display is False


@pytest.mark.asyncio
async def test_slash_on_schema_tree_shows_search_input():
    """Pressing / while SchemaTree is focused should show tree-search-input."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        search_input = app.screen.query_one("#tree-search-input", Input)
        assert search_input.display is True
        assert app.screen.focused is search_input


@pytest.mark.asyncio
async def test_slash_on_result_table_focuses_where_input():
    """Pressing / while ResultTable is focused should focus where-input (existing behavior)."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        screen._current_table = Table(name="users", schema="public")

        result_table = screen.query_one(ResultTable)
        result_table.focus()

        await pilot.press("slash")
        await pilot.pause()

        where_input = screen.query_one("#where-input", Input)
        assert screen.focused is where_input


@pytest.mark.asyncio
async def test_escape_hides_search_input_and_restores_tree():
    """Escape during tree search should hide input and restore all tables."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree._all_tables = [
            Table(name="users", schema="public"),
            Table(name="orders", schema="public"),
        ]
        tree.filter_tables("")
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        await pilot.press("escape")
        await pilot.pause()

        search_input = app.screen.query_one("#tree-search-input", Input)
        assert search_input.display is False
        assert isinstance(app.screen.focused, SchemaTree)
        leaves = [n for n in tree.root.children if n.data is not None]
        assert len(leaves) == 2


@pytest.mark.asyncio
async def test_enter_confirms_search_and_selects_first_node():
    """Enter during tree search should hide input, focus tree, and cursor on first leaf."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree._all_tables = [
            Table(name="users", schema="public"),
            Table(name="orders", schema="public"),
        ]
        tree.filter_tables("")
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        search_input = app.screen.query_one("#tree-search-input", Input)
        assert search_input.display is False
        assert isinstance(app.screen.focused, SchemaTree)
        # Cursor should be on the first leaf node
        assert tree.cursor_node is not None
        assert tree.cursor_node.data is not None
        assert tree.cursor_node.data.name == "users"


@pytest.mark.asyncio
async def test_typing_filters_tree_realtime():
    """Typing in tree search should filter the tree in real time."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree._all_tables = [
            Table(name="users", schema="public"),
            Table(name="orders", schema="public"),
            Table(name="user_roles", schema="public"),
        ]
        tree.filter_tables("")
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        await pilot.press("u", "s", "e", "r")
        await pilot.pause()

        leaves = [n for n in tree.root.children if n.data is not None]
        assert len(leaves) == 2
        assert {leaf.data.name for leaf in leaves} == {"users", "user_roles"}
