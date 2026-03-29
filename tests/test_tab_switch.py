from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea

from vql.screens.main import MainScreen
from vql.widgets.tab_bar import TabBar


class TabSwitchTestApp(App):
    def compose(self) -> ComposeResult:
        yield MainScreen()


@pytest.mark.asyncio
async def test_initial_tab_is_tables():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        assert screen._active_sidebar_tab == "tables"


@pytest.mark.asyncio
async def test_press_2_switches_sidebar_to_history():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        # Focus on tree (not input)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        assert screen._active_sidebar_tab == "history"


@pytest.mark.asyncio
async def test_press_1_switches_sidebar_back_to_tables():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        await pilot.press("1")
        await pilot.pause()
        assert screen._active_sidebar_tab == "tables"


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
        assert screen._active_sidebar_tab == "tables"


@pytest.mark.asyncio
async def test_center_tab_shortcuts_are_ignored_in_input():
    """Inputにフォーカスがある間は中央タブ切り替えを奪わないこと"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#where-input", Input).focus()
        await pilot.pause()
        await pilot.press("]")
        await pilot.pause()
        assert screen._active_center_tab == "tables"


@pytest.mark.asyncio
async def test_right_bracket_shows_sql_container():
    """] で中央パネルがSQL表示に切り替わること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("]")
        await pilot.pause()
        assert screen._active_center_tab == "sql"
        assert screen.query_one("#sql-container").display is True
        assert screen.query_one("#main-container").display is False


@pytest.mark.asyncio
async def test_left_bracket_returns_to_tables_after_right_bracket():
    """] でSQLへ移動した後、[ でTablesへ戻れること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("]")
        await pilot.pause()
        await pilot.press("[")
        await pilot.pause()
        assert screen._active_center_tab == "tables"
        assert screen.query_one("#main-container").display is True
        assert screen.query_one("#sql-container").display is False


@pytest.mark.asyncio
async def test_right_bracket_is_ignored_in_sql_editor():
    """SQL editorでは ] を入力に使えるよう中央タブ切り替えを奪わないこと"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen._switch_center_tab("sql")
        await pilot.pause()
        screen.query_one("#sql-editor", TextArea).focus()
        await pilot.pause()
        await pilot.press("]")
        await pilot.pause()
        assert screen._active_center_tab == "sql"
        assert screen.focused is screen.query_one("#sql-editor", TextArea)


@pytest.mark.asyncio
async def test_left_bracket_works_from_sql_result():
    """SQL resultにフォーカスがあるときは [ でTables表示へ戻れること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen._switch_center_tab("sql")
        await pilot.pause()
        screen.query_one("#sql-result").focus()
        await pilot.pause()
        await pilot.press("[")
        await pilot.pause()
        assert screen._active_center_tab == "tables"
        assert screen.query_one("#main-container").display is True
        assert screen.query_one("#sql-container").display is False


@pytest.mark.asyncio
async def test_switching_center_tabs_moves_focus_to_visible_result_widget():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#main").focus()
        await pilot.pause()
        screen._switch_center_tab("sql")
        await pilot.pause()
        assert screen.focused is screen.query_one("#sql-editor", TextArea)
        screen.query_one("#sql-result").focus()
        await pilot.pause()
        screen._switch_center_tab("tables")
        await pilot.pause()
        assert screen.focused is screen.query_one("#main")


@pytest.mark.asyncio
async def test_consecutive_tab_switch_2_then_1():
    """2→1と連続で押下してタブ切り替えができること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        screen.query_one("#sidebar").focus()
        await pilot.pause()
        await pilot.press("2")
        await pilot.pause()
        assert screen._active_sidebar_tab == "history"
        # Should be able to press 1 immediately without manual focus change
        await pilot.press("1")
        await pilot.pause()
        assert screen._active_sidebar_tab == "tables"


@pytest.mark.asyncio
async def test_center_tab_bar_exists():
    """中央パネルにTabBarが存在すること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        center_tab_bar = screen.query_one("#center-tab-bar", TabBar)
        assert center_tab_bar is not None


@pytest.mark.asyncio
async def test_left_tab_bar_still_exists():
    """左パネルにもTabBarが残っていること"""
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        left_tab_bar = screen.query_one("#tab-bar", TabBar)
        assert left_tab_bar is not None


@pytest.mark.asyncio
async def test_tables_mode_shows_main_container():
    app = TabSwitchTestApp()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        screen = app.query_one(MainScreen)
        assert screen.query_one("#main-container").display is True
        assert screen.query_one("#sql-container").display is False
