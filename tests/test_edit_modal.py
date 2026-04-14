import pytest
from textual.app import App
from textual.widgets import Input, TextArea

from vql.screens.edit_modal import MULTILINE_THRESHOLD, EditCellModal, EditResult


class _EditModalApp(App[None]):
    def __init__(self, current_value: str | None) -> None:
        super().__init__()
        self._current_value = current_value

    def on_mount(self) -> None:
        self.push_screen(EditCellModal(column_name="body", current_value=self._current_value))


def test_edit_cell_modal_exists():
    modal = EditCellModal(column_name="name", current_value="alice")
    assert modal.column_name == "name"
    assert modal.current_value == "alice"


def test_edit_cell_modal_null_value():
    modal = EditCellModal(column_name="name", current_value=None)
    assert modal.current_value is None


@pytest.mark.asyncio
async def test_edit_modal_short_value_uses_single_line_input():
    app = _EditModalApp("hello")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.screen.query_one("#edit-input", Input)


@pytest.mark.asyncio
async def test_edit_modal_long_value_uses_multiline_textarea():
    long_text = "x" * MULTILINE_THRESHOLD
    app = _EditModalApp(long_text)
    async with app.run_test() as pilot:
        await pilot.pause()
        ta = app.screen.query_one("#edit-input", TextArea)
        assert ta.text == long_text


@pytest.mark.asyncio
async def test_edit_modal_newline_uses_multiline_textarea():
    app = _EditModalApp("a\nb")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.screen.query_one("#edit-input", TextArea)


@pytest.mark.asyncio
async def test_edit_modal_ctrl_s_saves_and_dismisses():
    long_text = "x" * MULTILINE_THRESHOLD
    dismissed: list = []

    class _App(App[None]):
        def on_mount(self) -> None:
            self.push_screen(
                EditCellModal(column_name="c", current_value=long_text),
                callback=lambda r: dismissed.append(r),
            )

    app = _App()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()

    assert dismissed == [EditResult(value=long_text)]
