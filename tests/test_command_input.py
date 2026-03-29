import pytest
from textual.app import App
from textual.widgets import Static

from vql.screens.main import MainScreen


def test_main_screen_has_colon_binding():
    """colon binding should trigger command_input action."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "colon" in bindings
    assert bindings["colon"].action == "command_input"


def test_main_screen_has_no_direct_quit_binding():
    """quit should be available via :q, not direct q binding."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "q" not in bindings


def test_command_mode_uses_status_bar_css():
    """command mode should reuse the status bar instead of a dedicated input."""
    assert "#status" in MainScreen.DEFAULT_CSS
    assert "#command-input" not in MainScreen.DEFAULT_CSS


class CommandModeTestApp(App[None]):
    def on_mount(self) -> None:
        self.push_screen(MainScreen())


@pytest.mark.asyncio
async def test_command_text_is_rendered_in_status_bar():
    app = CommandModeTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        await pilot.press("colon", "w")

        assert screen.query_one("#status", Static).content == ":w"


@pytest.mark.asyncio
async def test_status_bar_does_not_overlap_footer():
    app = CommandModeTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        status = screen.query_one("#status", Static)
        footer = screen.query_one("#footer-bar", Static)

        assert status.region.y < footer.region.y


@pytest.mark.asyncio
async def test_command_mode_disables_screen_bindings():
    app = CommandModeTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen

        await pilot.press("colon", "q")

        assert app.is_running
        assert screen.query_one("#status", Static).content == ":q"


@pytest.mark.asyncio
async def test_colon_q_exits_app():
    app = CommandModeTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        await pilot.press("colon", "q", "enter")

        assert app.is_running is False


@pytest.mark.asyncio
async def test_escape_restores_previous_status_text():
    app = CommandModeTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        screen._set_status_text("Connected")

        await pilot.press("colon", "w", "escape")

        assert screen.query_one("#status", Static).content == "Connected"
