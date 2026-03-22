from __future__ import annotations

from textual.widgets import Static


class TabBar(Static):
    DEFAULT_CSS = """
    TabBar {
        height: 1;
        background: $surface;
        padding: 0 1;
        color: $text-muted;
    }
    """

    TABS = [("1", "Tables", "tables"), ("2", "SQL", "sql")]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active = "tables"

    def set_active(self, tab: str) -> None:
        self._active = tab
        self._render_label()

    def on_mount(self) -> None:
        self._render_label()

    def _render_label(self) -> None:
        parts = []
        for key, label, tab_id in self.TABS:
            if tab_id == self._active:
                parts.append(f"[bold]{key} {label}[/bold]")
            else:
                parts.append(f"[dim]{key} {label}[/dim]")
        self.update("  |  ".join(parts))
