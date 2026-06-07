import pytest
from textual.app import App
from textual.widgets import Input

from vql.app import TuiClientApp
from vql.screens.main import MainScreen


class MainScreenApp(App[None]):
    """Show MainScreen alone, reusing the real App.on_key under test."""

    on_key = TuiClientApp.on_key

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


@pytest.mark.asyncio
async def test_q_exits_from_main_screen():
    """q should exit the app when focus is not on a text input."""
    app = MainScreenApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        await pilot.press("q")

        assert app.is_running is False


@pytest.mark.asyncio
async def test_q_does_not_exit_while_typing_in_input():
    """q should be typed as text (not exit) when an Input is focused."""
    app = MainScreenApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        where_input = app.screen.query_one("#where-input", Input)
        where_input.focus()
        await pilot.pause()

        await pilot.press("q")

        assert app.is_running is True
        assert where_input.value == "q"


@pytest.mark.asyncio
async def test_q_exits_from_connection_modal():
    """q should exit even when a modal (no text input focused) is on top."""
    app = TuiClientApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        await pilot.press("q")

        assert app.is_running is False
