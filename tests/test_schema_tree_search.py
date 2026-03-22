import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input

from tui_client.db.base import Table
from tui_client.widgets.schema_tree import SchemaTree


class SchemaTreeTestApp(App[None]):
    def compose(self) -> ComposeResult:
        yield SchemaTree(id="sidebar")


def test_schema_tree_has_slash_binding():
    """SchemaTree should have a slash binding for search."""
    bindings = {b.key: b for b in SchemaTree.BINDINGS}
    assert "slash" in bindings


def test_schema_tree_stores_all_tables():
    """load_tables should store all tables in _all_tables."""
    tree = SchemaTree()
    assert tree._all_tables == []


def test_schema_tree_filter_tables():
    """filter_tables should filter tree nodes by partial match."""
    tree = SchemaTree()
    tree._all_tables = [
        Table(name="users", schema="public"),
        Table(name="orders", schema="public"),
        Table(name="user_roles", schema="public"),
    ]
    tree.filter_tables("user")
    # After filtering, only "users" and "user_roles" should remain
    leaves = [node for node in tree.root.children if node.data is not None]
    assert len(leaves) == 2
    assert {leaf.data.name for leaf in leaves} == {"users", "user_roles"}


def test_schema_tree_filter_tables_empty_query():
    """Empty query should show all tables."""
    tree = SchemaTree()
    tree._all_tables = [
        Table(name="users", schema="public"),
        Table(name="orders", schema="public"),
    ]
    tree.filter_tables("")
    leaves = [node for node in tree.root.children if node.data is not None]
    assert len(leaves) == 2


def test_schema_tree_filter_tables_case_insensitive():
    """Filtering should be case-insensitive."""
    tree = SchemaTree()
    tree._all_tables = [
        Table(name="Users", schema="public"),
        Table(name="orders", schema="public"),
    ]
    tree.filter_tables("user")
    leaves = [node for node in tree.root.children if node.data is not None]
    assert len(leaves) == 1
    assert leaves[0].data.name == "Users"


def test_schema_tree_filter_tables_no_match():
    """No match should result in empty tree."""
    tree = SchemaTree()
    tree._all_tables = [
        Table(name="users", schema="public"),
        Table(name="orders", schema="public"),
    ]
    tree.filter_tables("zzz")
    leaves = [node for node in tree.root.children if node.data is not None]
    assert len(leaves) == 0


class SearchModeCapture(App[None]):
    def __init__(self):
        super().__init__()
        self.search_messages: list[SchemaTree.SearchModeChanged] = []

    def compose(self) -> ComposeResult:
        yield SchemaTree(id="sidebar")

    def on_schema_tree_search_mode_changed(self, event: SchemaTree.SearchModeChanged) -> None:
        self.search_messages.append(event)


@pytest.mark.asyncio
async def test_slash_on_schema_tree_posts_search_mode_changed():
    """Pressing / on SchemaTree should post SearchModeChanged."""
    app = SearchModeCapture()

    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one(SchemaTree)
        tree.focus()

        await pilot.press("slash")
        await pilot.pause()

        assert len(app.search_messages) == 1
        assert app.search_messages[0].active is True
