from __future__ import annotations

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static


class PropertyPanel(VerticalScroll):
    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
    ]

    DEFAULT_CSS = """
    PropertyPanel {
        width: 40;
        dock: right;
        border-left: solid $accent;
    }
    PropertyPanel .prop-item {
        height: auto;
        margin: 0;
        padding: 0 1;
        border: solid $accent;
    }
    PropertyPanel .prop-name {
        color: $text-muted;
    }
    PropertyPanel .prop-value {
        color: $success;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.properties: list[tuple[str, str]] = []

    def update_properties(self, columns: list[str], row: tuple) -> None:
        self.properties = [
            (col, "NULL" if val is None else str(val))
            for col, val in zip(columns, row)
        ]
        self._refresh_display()

    def clear_properties(self) -> None:
        self.properties = []
        self._refresh_display()

    def _refresh_display(self) -> None:
        try:
            self.remove_children()
        except Exception:
            return
        for name, value in self.properties:
            item = Static(f"[dim]{name}[/dim]\n{value}", classes="prop-item")
            self.mount(item)
