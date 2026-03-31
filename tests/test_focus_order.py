import pytest
from textual.binding import Binding

from vql.screens.main import MainScreen


def test_main_screen_has_tab_binding():
    """Tab binding should call screen-level focus_next, not app-level."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "tab" in bindings
    assert bindings["tab"].action == "focus_next"


def test_main_screen_has_shift_tab_binding():
    """Shift+Tab binding should call screen-level focus_previous, not app-level."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "shift+tab" in bindings
    assert bindings["shift+tab"].action == "focus_previous"


def test_focus_order_is_left_and_center_only():
    screen = MainScreen()
    order = screen._focus_order()
    assert order == ["left", "center"]
