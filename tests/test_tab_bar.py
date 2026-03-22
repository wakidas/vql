from __future__ import annotations

import pytest
from textual.app import App, ComposeResult

from vql.widgets.tab_bar import TabBar


class TabBarTestApp(App):
    def compose(self) -> ComposeResult:
        yield TabBar(id="tab-bar")


@pytest.mark.asyncio
async def test_tab_bar_initial_active_is_tables():
    app = TabBarTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        tab_bar = app.query_one(TabBar)
        assert tab_bar._active == "tables"


@pytest.mark.asyncio
async def test_tab_bar_set_active_sql():
    app = TabBarTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        tab_bar = app.query_one(TabBar)
        tab_bar.set_active("sql")
        assert tab_bar._active == "sql"


@pytest.mark.asyncio
async def test_tab_bar_set_active_tables():
    app = TabBarTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        tab_bar = app.query_one(TabBar)
        tab_bar.set_active("sql")
        tab_bar.set_active("tables")
        assert tab_bar._active == "tables"
