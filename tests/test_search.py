import pytest
from textual.app import App
from textual.widgets import Input, Static

from vql.db.base import Table
from vql.screens.main import MainScreen


class SearchTestApp(App[None]):
    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def test_main_screen_has_slash_binding():
    """slash binding should trigger search action."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "slash" in bindings
    assert bindings["slash"].action == "search"


def test_where_input_exists_in_css():
    """WHERE input should be defined in the CSS."""
    assert "#where-input" in MainScreen.DEFAULT_CSS


@pytest.mark.asyncio
async def test_where_input_is_always_visible():
    app = SearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        where_input = screen.query_one("#where-input", Input)
        assert where_input.display is True


@pytest.mark.asyncio
async def test_slash_focuses_where_input():
    """When not on SchemaTree, slash should focus where-input."""
    app = SearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        from vql.widgets.result_table import ResultTable
        screen.query_one(ResultTable).focus()
        screen._current_table = Table(name="users", schema="public")
        await pilot.press("slash")

        where_input = screen.query_one("#where-input", Input)
        assert screen.focused is where_input


@pytest.mark.asyncio
async def test_slash_does_nothing_without_table():
    app = SearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        await pilot.press("slash")

        where_input = screen.query_one("#where-input", Input)
        assert screen.focused is not where_input


@pytest.mark.asyncio
async def test_escape_unfocuses_where_input():
    app = SearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        screen._current_table = Table(name="users", schema="public")
        await pilot.press("slash")
        await pilot.press("escape")

        where_input = screen.query_one("#where-input", Input)
        assert screen.focused is not where_input


@pytest.mark.asyncio
async def test_where_input_placeholder():
    app = SearchTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        where_input = screen.query_one("#where-input", Input)
        assert "WHERE" in where_input.placeholder
