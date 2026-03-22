from __future__ import annotations

from textual.widgets import Static


class DbHeader(Static):
    DEFAULT_CSS = """
    DbHeader {
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.db_name = ""

    def set_db_name(self, name: str, detail: str) -> None:
        self.db_name = f"{name} ({detail})"
        self.update(self.db_name)
