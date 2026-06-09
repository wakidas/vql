import pytest
from textual.app import App

from vql.db.base import Column, QueryResult, Table
from vql.screens.main import MainScreen
from vql.widgets.schema_tree import SchemaTree
from vql.widgets.result_table import ResultTable


class StubAdapter:
    async def get_tables(self, schema: str = "public") -> list[Table]:
        return [
            Table(name="users", schema="public"),
            Table(name="orders", schema="public"),
        ]

    async def get_columns(self, schema: str, table: str) -> list[Column]:
        return [
            Column(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
            Column(name="name", data_type="text", is_nullable=False),
        ]

    async def execute(self, query) -> QueryResult:
        return QueryResult(columns=["id", "name"], rows=[(1, "alice")])


class PreviewTestApp(App[None]):
    def __init__(self) -> None:
        super().__init__()
        self.adapter = StubAdapter()

    def on_mount(self) -> None:
        self.push_screen(MainScreen(adapter=self.adapter))


async def _focus_first_leaf(pilot) -> SchemaTree:
    """Move the tree cursor onto the first table leaf (fires NodeHighlighted)."""
    tree = pilot.app.screen.query_one(SchemaTree)
    tree.focus()
    await pilot.press("j")
    await pilot.pause()
    return tree


@pytest.mark.asyncio
async def test_highlight_loads_preview_without_moving_focus():
    """Moving the tree cursor onto a table auto-loads the preview, keeping focus on the tree."""
    app = PreviewTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = await _focus_first_leaf(pilot)

        result_table = app.screen.query_one("#main", ResultTable)
        assert result_table.row_count == 1
        assert [str(c.label) for c in result_table.columns.values()] == ["id", "name"]
        # Focus stays on the tree, not the result table.
        assert app.screen.focused is tree


@pytest.mark.asyncio
async def test_enter_moves_focus_to_result_table():
    """Pressing Enter on a highlighted table moves focus to the ResultTable preview."""
    app = PreviewTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await _focus_first_leaf(pilot)

        await pilot.press("enter")
        await pilot.pause()

        result_table = app.screen.query_one("#main", ResultTable)
        assert app.screen.focused is result_table


@pytest.mark.asyncio
async def test_highlight_switches_center_tab_to_tables():
    """Highlighting a table while the SQL tab is active switches the center tab to Tables."""
    app = PreviewTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        screen._switch_center_tab("sql")
        assert screen._active_center_tab == "sql"

        await _focus_first_leaf(pilot)

        assert screen._active_center_tab == "tables"
