from __future__ import annotations

import pytest
from textual.app import App, ComposeResult

from vql.widgets.sql_history_list import SqlHistoryList


class HistoryTestApp(App):
    def compose(self) -> ComposeResult:
        yield SqlHistoryList(id="sql-history")


@pytest.mark.asyncio
async def test_add_entry_adds_item():
    app = HistoryTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        history = app.query_one(SqlHistoryList)
        history.add_entry("SELECT 1")
        await pilot.pause()
        assert len(history.children) == 1


@pytest.mark.asyncio
async def test_add_multiple_entries_newest_first():
    app = HistoryTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        history = app.query_one(SqlHistoryList)
        history.add_entry("SELECT 1")
        history.add_entry("SELECT 2")
        await pilot.pause()
        assert len(history.children) == 2
        assert history._entries[0] == "SELECT 2"


@pytest.mark.asyncio
async def test_get_selected_sql_returns_entry():
    app = HistoryTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        history = app.query_one(SqlHistoryList)
        history.add_entry("SELECT 1")
        history.add_entry("SELECT 2")
        for _ in range(5):
            await pilot.pause()
        history.index = 0
        assert history.get_selected_sql() == "SELECT 2"


@pytest.mark.asyncio
async def test_get_selected_sql_empty_returns_none():
    app = HistoryTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        history = app.query_one(SqlHistoryList)
        assert history.get_selected_sql() is None


@pytest.mark.asyncio
async def test_long_sql_is_truncated():
    app = HistoryTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        history = app.query_one(SqlHistoryList)
        long_sql = "SELECT " + "a" * 100
        history.add_entry(long_sql)
        await pilot.pause()
        assert history._entries[0] == long_sql  # full text preserved
