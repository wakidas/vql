import pytest
from textual.app import App
from textual.widgets import Input, Static

from vql.db.base import Table
from vql.screens.main import MainScreen
from vql.widgets.schema_tree import SchemaTree
from vql.widgets.result_table import ResultTable


class TreeSearchTestApp(App[None]):
    def on_mount(self) -> None:
        self.push_screen(MainScreen())


@pytest.mark.asyncio
async def test_tree_search_input_always_visible():
    """tree-search-input should be visible by default."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        search_input = app.screen.query_one("#tree-search-input", Input)
        assert search_input.display is True


@pytest.mark.asyncio
async def test_slash_on_schema_tree_focuses_search_input():
    """Pressing / while SchemaTree is focused should focus tree-search-input."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        search_input = app.screen.query_one("#tree-search-input", Input)
        assert app.screen.focused is search_input


@pytest.mark.asyncio
async def test_search_label_active_when_focused():
    """Search label should have 'active' class when input is focused."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        label = app.screen.query_one("#tree-search-label", Static)
        assert label.has_class("active")


@pytest.mark.asyncio
async def test_search_label_active_with_text_after_enter():
    """Search label should stay 'active' after Enter when text remains."""
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
        await pilot.press("u", "s", "e", "r")
        await pilot.press("enter")
        await pilot.pause()

        label = app.screen.query_one("#tree-search-label", Static)
        search_input = app.screen.query_one("#tree-search-input", Input)
        assert label.has_class("active")
        assert search_input.value == "user"


@pytest.mark.asyncio
async def test_search_label_inactive_after_escape():
    """Search label should lose 'active' class after Escape clears text."""
    app = TreeSearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.screen.query_one(SchemaTree)
        tree._all_tables = [
            Table(name="users", schema="public"),
        ]
        tree.filter_tables("")
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()
        await pilot.press("u")
        await pilot.press("escape")
        await pilot.pause()

        label = app.screen.query_one("#tree-search-label", Static)
        search_input = app.screen.query_one("#tree-search-input", Input)
        assert not label.has_class("active")
        assert search_input.value == ""


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
async def test_escape_clears_and_restores_tree():
    """Escape during tree search should clear input and restore all tables."""
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
        await pilot.press("u")
        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen.focused, SchemaTree)
        leaves = [n for n in tree.root.children if n.data is not None]
        assert len(leaves) == 2


@pytest.mark.asyncio
async def test_enter_confirms_search_and_selects_first_node():
    """Enter during tree search should focus tree and cursor on first leaf."""
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

        assert isinstance(app.screen.focused, SchemaTree)
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
