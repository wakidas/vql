from __future__ import annotations

from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from tui_client.db.base import QueryResult


class ResultTable(DataTable):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("h", "cursor_left", "Left", show=False),
        Binding("l", "cursor_right", "Right", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
        Binding("y", "copy_cell", "Copy", show=False),
        Binding("i", "edit_cell", "Edit", show=False),
    ]

    DEFAULT_CSS = """
    ResultTable {
        height: 1fr;
    }
    """

    class EditCellRequested(Message):
        def __init__(self, row_idx: int, col_idx: int, column_name: str, current_value) -> None:
            super().__init__()
            self.row_idx = row_idx
            self.col_idx = col_idx
            self.column_name = column_name
            self.current_value = current_value

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "cell"
        self.zebra_stripes = True
        self.pending_changes: dict[tuple[int, int], str | None] = {}

    def action_copy_cell(self) -> None:
        try:
            cell_key = self.coordinate_to_cell_key(self.cursor_coordinate)
            value = self.get_cell(cell_key.row_key, cell_key.column_key)
        except Exception:
            return
        text = str(value)
        import subprocess
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
        self.notify(f"Copied: {text[:50]}", severity="information")

    def action_edit_cell(self) -> None:
        try:
            coord = self.cursor_coordinate
            cell_key = self.coordinate_to_cell_key(coord)
            value = self.get_cell(cell_key.row_key, cell_key.column_key)
            column_name = str(list(self.columns.values())[coord.column].label)
        except Exception:
            return
        self.post_message(
            self.EditCellRequested(coord.row, coord.column, column_name, value)
        )

    def add_pending_change(self, row_idx: int, col_idx: int, value: str | None) -> None:
        self.pending_changes[(row_idx, col_idx)] = value

    def clear_pending_changes(self) -> None:
        self.pending_changes = {}

    def apply_pending_visual(self, row_idx: int, col_idx: int, display_value: str) -> None:
        try:
            cell_key = self.coordinate_to_cell_key((row_idx, col_idx))
            self.update_cell(cell_key.row_key, cell_key.column_key, f"*{display_value}")
        except Exception:
            pass

    def load_result(self, result: QueryResult) -> None:
        self.clear(columns=True)
        self.pending_changes = {}
        if not result.columns:
            return
        self.add_columns(*result.columns)
        self.add_rows(result.rows)
