from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea

from vql.screens.main import MainScreen


class TabSwitchTestApp(App):
    def compose(self) -> ComposeResult:
        yield MainScreen()


@pytest.mark.asyncio
async def test_initial_tab_is_tables():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        assert screen._active_tab == "tables"


@pytest.mark.asyncio
async def test_press_2_switches_to_sql_mode():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        # Focus on tree (not input)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        assert screen._active_tab == "sql"


@pytest.mark.asyncio
async def test_press_1_switches_back_to_tables():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        # Move focus away from TextArea to allow 1 key to work
        screen.query_one("#sql-result").focus()
        await pilot.pause()
        await pilot.press("1")
        await pilot.pause()
        assert screen._active_tab == "tables"


@pytest.mark.asyncio
async def test_tab_key_ignored_in_input():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#where-input", Input).focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        # Should stay on tables because input is focused
        assert screen._active_tab == "tables"


@pytest.mark.asyncio
async def test_sql_mode_shows_sql_container():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        assert screen.query_one("#sql-container").display is True
        assert screen.query_one("#main-container").display is False


@pytest.mark.asyncio
async def test_tables_mode_shows_main_container():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        assert screen.query_one("#main-container").display is True
        assert screen.query_one("#sql-container").display is False
