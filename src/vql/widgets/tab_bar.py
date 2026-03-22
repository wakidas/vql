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

    DEFAULT_TABS = [("1", "Tables", "tables"), ("2", "SQL", "sql")]

    def __init__(self, tabs: list[tuple[str, str, str]] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tabs = tabs or self.DEFAULT_TABS
        self._active = self._tabs[0][2]

    def set_active(self, tab: str) -> None:
        self._active = tab
        self._render_label()

    def on_mount(self) -> None:
        self._render_label()

    def _render_label(self) -> None:
        parts = []
        for key, label, tab_id in self._tabs:
            if tab_id == self._active:
                parts.append(f"[bold][{key}] {label}[/bold]")
            else:
                parts.append(f"[dim][{key}] {label}[/dim]")
        self.update("  |  ".join(parts))
