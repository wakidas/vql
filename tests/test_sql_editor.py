from __future__ import annotations

import pytest
from textual.app import App, ComposeResult

from vql.widgets.sql_editor import SqlEditor


class SqlEditorTestApp(App):
    def compose(self) -> ComposeResult:
        yield SqlEditor(id="sql-editor")


class ExecuteCapture(App):
    def __init__(self) -> None:
        super().__init__()
        self.captured_sql: str | None = None

    def compose(self) -> ComposeResult:
        yield SqlEditor(id="sql-editor")

    def on_sql_editor_execute_requested(self, event: SqlEditor.ExecuteRequested) -> None:
        self.captured_sql = event.sql_text


@pytest.mark.asyncio
async def test_sql_editor_ctrl_r_posts_execute_requested():
    app = ExecuteCapture()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one(SqlEditor)
        editor.focus()
        editor.insert("SELECT 1")
        await pilot.pause()
        await pilot.press("ctrl+r")
        await pilot.pause()
        assert app.captured_sql == "SELECT 1"


@pytest.mark.asyncio
async def test_sql_editor_empty_does_not_post():
    app = ExecuteCapture()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one(SqlEditor)
        editor.focus()
        await pilot.pause()
        await pilot.press("ctrl+r")
        await pilot.pause()
        assert app.captured_sql is None
