import pytest
from textual.binding import Binding

from tui_client.screens.main import MainScreen
from tui_client.widgets.schema_tree import SchemaTree
from tui_client.widgets.result_table import ResultTable
from tui_client.widgets.property_panel import PropertyPanel


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


def test_focus_order_is_tree_table_property():
    screen = MainScreen()
    order = screen._focus_order()
    assert order == [SchemaTree, ResultTable, PropertyPanel]
