from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import DataTable, Header, Input, Static, TextArea, Tree
from psycopg import sql

from vql.db.base import Column, DBAdapter, Table
from vql.widgets.schema_tree import SchemaTree
from vql.widgets.result_table import ResultTable
from vql.widgets.property_panel import PropertyPanel
from vql.widgets.db_header import DbHeader
from vql.widgets.tab_bar import TabBar
from vql.widgets.sql_editor import SqlEditor
from vql.widgets.sql_history_list import SqlHistoryList
from vql.screens.edit_modal import EditCellModal, EditResult
from vql.screens.confirm_modal import ConfirmModal


class MainScreen(Screen):
    BINDINGS = [
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
        Binding("h", "focus_tree", "Tree", show=True),
        Binding("l", "focus_table", "Table", show=True),
        Binding("semicolon", "focus_property", "Property", show=True),
        Binding("c", "connect", "Connect", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("colon", "command_input", "Command", show=False),
        Binding("slash", "search", "Search", show=False),
    ]

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }
    #content {
        height: 1fr;
        layout: horizontal;
    }
    #bottom-bar {
        height: 2;
    }
    #sidebar-container {
        width: 30;
        border-right: solid $accent;
    }
    #sidebar {
        width: 1fr;
    }
    #tree-search-container {
        height: 1;
        layout: horizontal;
        background: $surface;
        padding: 0 1;
    }
    #tree-search-label {
        width: auto;
        color: $text-muted;
    }
    #tree-search-label.active {
        color: $success;
    }
    #tree-search-input {
        height: 1;
        background: $surface;
        border: none;
        padding: 0;
    }
    #center-panel {
        width: 1fr;
    }
    #main-container {
        width: 1fr;
    }
    #main {
        width: 1fr;
    }
    #where-input {
        height: 1;
        background: $surface;
        border: none;
        padding: 0 1;
    }
    #status {
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    #footer-bar {
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 1;
    }
    #tables-tab {
        height: 1fr;
    }
    #history-tab {
        height: 1fr;
    }
    #sql-container {
        width: 1fr;
    }
    #sql-result {
        width: 1fr;
    }
    """

    def __init__(self, adapter: DBAdapter | None = None) -> None:
        super().__init__()
        self.adapter = adapter
        self._current_table: Table | None = None
        self._current_columns: list[Column] = []
        self._original_rows: list[tuple] = []
        self._status_text = "No connection"
        self._command_mode = False
        self._command_buffer = ""
        self._footer_text = "; Property   c Connect   r Refresh   q Quit"
        self._current_where: str = ""
        self._active_sidebar_tab: str = "tables"
        self._active_center_tab: str = "tables"
        self._sql_history: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="content"):
            with Vertical(id="sidebar-container"):
                yield DbHeader(id="db-header")
                yield TabBar(
                    tabs=[("1", "Tables", "tables"), ("2", "History", "history")],
                    id="tab-bar",
                )
                with Vertical(id="tables-tab"):
                    with Horizontal(id="tree-search-container"):
                        yield Static("Search: ", id="tree-search-label")
                        search_input = Input(id="tree-search-input")
                        search_input.can_focus = False
                        yield search_input
                    yield SchemaTree(id="sidebar")
                history_tab = Vertical(id="history-tab")
                history_tab.display = False
                with history_tab:
                    yield SqlHistoryList(id="sql-history")
            with Vertical(id="center-panel"):
                yield TabBar(id="center-tab-bar")
                with Vertical(id="main-container"):
                    yield Input(
                        placeholder="WHERE Enter a WHERE clause to filter the results",
                        id="where-input",
                    )
                    yield ResultTable(id="main")
                sql_container = Vertical(id="sql-container")
                sql_container.display = False
                with sql_container:
                    yield SqlEditor(id="sql-editor")
                    yield ResultTable(id="sql-result")
            yield PropertyPanel(id="property")
        with Vertical(id="bottom-bar"):
            yield Static(self._status_text, id="status")
            yield Static(self._footer_text, id="footer-bar")

    async def on_mount(self) -> None:
        if self.adapter:
            await self._load_schema()

    def _status_widget(self) -> Static:
        return self.query_one("#status", Static)

    def _set_status_text(self, text: str) -> None:
        self._status_text = text
        if not self._command_mode:
            self._status_widget().update(text)

    def _render_command_line(self) -> None:
        self._status_widget().update(f":{self._command_buffer}")

    def _enter_command_mode(self) -> None:
        if self._command_mode:
            return
        self._command_mode = True
        self._command_buffer = ""
        self._render_command_line()

    def _exit_command_mode(self) -> None:
        if not self._command_mode:
            return
        self._command_mode = False
        self._command_buffer = ""
        self._status_widget().update(self._status_text)

    def _build_select_query(self) -> sql.Composable:
        base = sql.SQL("SELECT * FROM {}.{}").format(
            sql.Identifier(self._current_table.schema),
            sql.Identifier(self._current_table.name),
        )
        if self._current_where:
            base = sql.SQL("{} WHERE {}").format(base, sql.SQL(self._current_where))
        return sql.SQL("{} LIMIT 100").format(base)

    async def _load_schema(self) -> None:
        tree = self.query_one(SchemaTree)
        await tree.load_tables(self.adapter)
        self._set_status_text("Connected")

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        table = event.node.data
        if table is None or self.adapter is None:
            return
        self._current_table = table
        self._current_where = ""
        self.query_one("#where-input", Input).value = ""
        try:
            self._current_columns = await self.adapter.get_columns(table.schema, table.name)
        except Exception:
            self._current_columns = []
        query = self._build_select_query()
        try:
            result = await self.adapter.execute(query)
        except Exception as e:
            self.notify(f"Query failed: {e}", severity="error")
            return
        self._original_rows = list(result.rows)
        self.query_one("#main", ResultTable).load_result(result)

    def _active_result_table(self) -> ResultTable:
        if self._active_center_tab == "sql":
            return self.query_one("#sql-result", ResultTable)
        return self.query_one("#main", ResultTable)

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        table = self._active_result_table()
        if event.data_table is not table:
            return
        panel = self.query_one(PropertyPanel)
        row_idx = event.coordinate.row
        if row_idx < 0 or not table.columns:
            panel.clear_properties()
            return
        columns = [str(col.label) for col in table.columns.values()]
        row_data = tuple(
            table.get_cell_at((row_idx, col_idx))
            for col_idx in range(len(columns))
        )
        panel.update_properties(columns, row_data)

    def on_result_table_edit_cell_requested(self, event: ResultTable.EditCellRequested) -> None:
        pk_cols = [c for c in self._current_columns if c.is_primary_key]
        if not pk_cols:
            self.notify("Cannot edit: table has no primary key", severity="error")
            return
        self.app.push_screen(
            EditCellModal(column_name=event.column_name, current_value=event.current_value),
            callback=lambda result: self._on_edit_result(result, event.row_idx, event.col_idx),
        )

    def _on_edit_result(self, result: EditResult | None, row_idx: int, col_idx: int) -> None:
        if result is None:
            return
        table = self.query_one("#main", ResultTable)
        table.add_pending_change(row_idx, col_idx, result.value)
        display = "NULL" if result.value is None else result.value
        table.apply_pending_visual(row_idx, col_idx, display)
        self._set_status_text("Unsaved changes (*)")

    def _restore_row(self, table: ResultTable, row_idx: int) -> None:
        if row_idx >= len(self._original_rows):
            return
        original_row = self._original_rows[row_idx]
        table.restore_row_visual(row_idx, original_row)
        for col_idx in range(len(table.columns)):
            if (row_idx, col_idx) in table.pending_changes:
                value = table.pending_changes[(row_idx, col_idx)]
                display = "NULL" if value is None else value
                table.apply_pending_visual(row_idx, col_idx, display)

    def _update_status(self, table: ResultTable) -> None:
        if not table.pending_changes and not table.pending_deletes:
            self._set_status_text("Connected")
        else:
            self._set_status_text("Unsaved changes (*)")

    def on_result_table_delete_row_requested(self, event: ResultTable.DeleteRowRequested) -> None:
        pk_cols = [c for c in self._current_columns if c.is_primary_key]
        if not pk_cols:
            self.notify("Cannot delete: table has no primary key", severity="error")
            return
        if event.row_idx >= len(self._original_rows):
            return
        table = self.query_one("#main", ResultTable)
        table.add_pending_delete(event.row_idx)
        if event.row_idx in table.pending_deletes:
            table.apply_delete_visual(event.row_idx)
        else:
            self._restore_row(table, event.row_idx)
        self._update_status(table)

    def on_result_table_undo_requested(self, event: ResultTable.UndoRequested) -> None:
        table = self.query_one("#main", ResultTable)
        row_idx = event.row_idx
        col_idx = event.col_idx
        if row_idx >= len(self._original_rows):
            return
        if row_idx in table.pending_deletes:
            table.undo_pending(row_idx, None)
            self._restore_row(table, row_idx)
        elif col_idx is not None and (row_idx, col_idx) in table.pending_changes:
            table.undo_pending(row_idx, col_idx)
            original_value = self._original_rows[row_idx][col_idx]
            try:
                cell_key = table.coordinate_to_cell_key((row_idx, col_idx))
                table.update_cell(cell_key.row_key, cell_key.column_key, original_value)
            except Exception:
                pass
        else:
            return
        self._update_status(table)

    def _update_search_label(self, *, searching: bool = False) -> None:
        label = self.query_one("#tree-search-label", Static)
        search_input = self.query_one("#tree-search-input", Input)
        if searching or search_input.value:
            label.add_class("active")
        else:
            label.remove_class("active")

    def on_schema_tree_search_mode_changed(self, event: SchemaTree.SearchModeChanged) -> None:
        if event.active:
            search_input = self.query_one("#tree-search-input", Input)
            search_input.can_focus = True
            search_input.focus()
            self._update_search_label(searching=True)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "tree-search-input":
            self.query_one(SchemaTree).filter_tables(event.value)
            self._update_search_label()

    def action_search(self) -> None:
        if self._current_table is None:
            return
        self.query_one("#where-input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "where-input":
            return
        if self._current_table is None or self.adapter is None:
            return
        where_clause = event.value.strip()
        if ";" in where_clause:
            self.notify("Semicolons are not allowed in WHERE clause", severity="error")
            return
        self._current_where = where_clause
        query = self._build_select_query()
        try:
            result = await self.adapter.execute(query)
        except Exception as e:
            self.notify(f"Query failed: {e}", severity="error")
            return
        self._original_rows = list(result.rows)
        self.query_one("#main", ResultTable).load_result(result)
        self.query_one("#main", ResultTable).focus()

    def action_command_input(self) -> None:
        self._enter_command_mode()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if self._command_mode:
            return False
        return super().check_action(action, parameters)

    def _switch_sidebar_tab(self, tab: str) -> None:
        if self._active_sidebar_tab == tab:
            return
        self._active_sidebar_tab = tab
        self.query_one("#tab-bar", TabBar).set_active(tab)
        is_tables = tab == "tables"
        self.query_one("#tables-tab").display = is_tables
        self.query_one("#history-tab").display = not is_tables
        if is_tables:
            self.query_one(SchemaTree).focus()
        else:
            self.query_one(SqlHistoryList).focus()

    def _switch_center_tab(self, tab: str) -> None:
        if self._active_center_tab == tab:
            return
        self._active_center_tab = tab
        self.query_one("#center-tab-bar", TabBar).set_active(tab)
        is_tables = tab == "tables"
        self.query_one("#main-container").display = is_tables
        self.query_one("#sql-container").display = not is_tables

    async def on_key(self, event: Key) -> None:
        if event.key == "ctrl+1":
            self._switch_center_tab("tables")
            event.prevent_default()
            event.stop()
            return
        elif event.key == "ctrl+2":
            self._switch_center_tab("sql")
            event.prevent_default()
            event.stop()
            return

        if not isinstance(self.focused, (Input, TextArea)) and not self._command_mode:
            if event.key == "1":
                self._switch_sidebar_tab("tables")
                event.prevent_default()
                event.stop()
                return
            elif event.key == "2":
                self._switch_sidebar_tab("history")
                event.prevent_default()
                event.stop()
                return

        if isinstance(self.focused, TextArea) and self.focused.id == "sql-editor":
            if event.key == "escape":
                self.query_one("#sql-result", ResultTable).focus()
                event.prevent_default()
                event.stop()
            return

        if isinstance(self.focused, Input) and self.focused.id == "tree-search-input":
            if event.key == "escape":
                search_input = self.query_one("#tree-search-input", Input)
                search_input.value = ""
                search_input.can_focus = False
                self.query_one(SchemaTree).filter_tables("")
                self.query_one(SchemaTree).focus()
                self._update_search_label()
                event.prevent_default()
                event.stop()
            elif event.key == "enter":
                search_input = self.query_one("#tree-search-input", Input)
                search_input.can_focus = False
                tree = self.query_one(SchemaTree)
                tree.focus()
                leaves = [n for n in tree.root.children if n.data is not None]
                if leaves:
                    tree.select_node(leaves[0])
                    tree.scroll_to_node(leaves[0])
                self._update_search_label()
                event.prevent_default()
                event.stop()
            return

        if isinstance(self.focused, Input) and self.focused.id == "where-input":
            if event.key == "escape":
                self.query_one("#main", ResultTable).focus()
                event.prevent_default()
                event.stop()
            return

        if not self._command_mode:
            return

        if event.key == "escape":
            self._exit_command_mode()
        elif event.key == "enter":
            cmd = self._command_buffer.strip()
            self._exit_command_mode()
            if cmd == "w":
                await self._save_changes()
        elif event.key == "backspace":
            self._command_buffer = self._command_buffer[:-1]
            self._render_command_line()
        elif event.character and event.character.isprintable():
            self._command_buffer += event.character
            self._render_command_line()

        event.prevent_default()
        event.stop()

    async def _save_changes(self) -> None:
        table_widget = self.query_one("#main", ResultTable)
        if not table_widget.pending_changes and not table_widget.pending_deletes:
            self.notify("No changes to save", severity="information")
            return
        if self._current_table is None or self.adapter is None:
            return
        pk_cols = [c for c in self._current_columns if c.is_primary_key]
        if not pk_cols:
            self.notify("Cannot save: no primary key", severity="error")
            return
        if table_widget.pending_deletes:
            delete_count = len(table_widget.pending_deletes)
            self.app.push_screen(
                ConfirmModal(message=f"{delete_count}行削除します。よろしいですか？"),
                callback=lambda confirmed: self._on_confirm_save(confirmed),
            )
        else:
            await self._execute_save()

    def _on_confirm_save(self, confirmed: bool) -> None:
        if confirmed:
            self.run_worker(self._execute_save(), exclusive=True)

    def on_worker_state_changed(self, event) -> None:
        if event.worker.state.name == "ERROR":
            self.notify(f"Save failed: {event.worker.error}", severity="error")

    async def _execute_save(self) -> None:
        table_widget = self.query_one("#main", ResultTable)
        if self._current_table is None or self.adapter is None:
            return
        pk_cols = [c for c in self._current_columns if c.is_primary_key]
        col_names = [str(col.label) for col in table_widget.columns.values()]
        total_deleted = 0
        delete_targets = sorted(table_widget.pending_deletes, reverse=True)
        for row_idx in delete_targets:
            if row_idx >= len(self._original_rows):
                continue
            original_row = self._original_rows[row_idx]
            pk_values = [original_row[col_names.index(pk.name)] for pk in pk_cols]
            try:
                result = await self.adapter.delete(
                    schema=self._current_table.schema,
                    table=self._current_table.name,
                    pk_columns=[pk.name for pk in pk_cols],
                    pk_values=pk_values,
                )
                total_deleted += result.deleted_count
                table_widget.pending_deletes.discard(row_idx)
            except Exception as e:
                self.notify(f"Delete failed: {e}", severity="error")
                return
        changes_without_deleted = {
            (r, c): v for (r, c), v in table_widget.pending_changes.items()
            if r not in table_widget.pending_deletes
        }
        total_updated = 0
        changes_by_row: dict[int, dict[int, str | None]] = {}
        for (row_idx, col_idx), value in changes_without_deleted.items():
            changes_by_row.setdefault(row_idx, {})[col_idx] = value
        for row_idx, col_changes in changes_by_row.items():
            original_row = self._original_rows[row_idx]
            pk_values = [original_row[col_names.index(pk.name)] for pk in pk_cols]
            update_columns = [col_names[ci] for ci in col_changes]
            update_values = list(col_changes.values())
            try:
                result = await self.adapter.update(
                    schema=self._current_table.schema,
                    table=self._current_table.name,
                    pk_columns=[pk.name for pk in pk_cols],
                    pk_values=pk_values,
                    update_columns=update_columns,
                    update_values=update_values,
                )
                total_updated += result.updated_count
            except Exception as e:
                self.notify(f"Update failed: {e}", severity="error")
                return
        table_widget.clear_pending_changes()
        query = self._build_select_query()
        try:
            qr = await self.adapter.execute(query)
            self._original_rows = list(qr.rows)
            table_widget.load_result(qr)
        except Exception:
            pass
        parts = []
        if total_deleted:
            parts.append(f"Deleted {total_deleted} row(s)")
        if total_updated:
            parts.append(f"Updated {total_updated} row(s)")
        self.notify(", ".join(parts) if parts else "Saved", severity="information")
        self._set_status_text("Connected")

    async def on_sql_editor_execute_requested(self, event: SqlEditor.ExecuteRequested) -> None:
        if self.adapter is None:
            self.notify("Not connected", severity="error")
            return
        try:
            result = await self.adapter.execute(event.sql_text)
        except Exception as e:
            self.notify(f"Query failed: {e}", severity="error")
            return
        self._sql_history.append(event.sql_text)
        self.query_one(SqlHistoryList).add_entry(event.sql_text)
        self.query_one("#sql-result", ResultTable).load_result(result)
        self._set_status_text(f"Rows: {len(result.rows)}")

    def on_sql_history_list_selected(self, event: SqlHistoryList.Selected) -> None:
        history = self.query_one(SqlHistoryList)
        sql_text = history.get_selected_sql()
        if sql_text is not None:
            editor = self.query_one(SqlEditor)
            editor.clear()
            editor.insert(sql_text)
            editor.focus()

    def action_focus_tree(self) -> None:
        if self._active_sidebar_tab == "tables":
            self.query_one(SchemaTree).focus()
        else:
            self.query_one(SqlHistoryList).focus()

    def action_focus_table(self) -> None:
        self._active_result_table().focus()

    def action_focus_property(self) -> None:
        self.query_one(PropertyPanel).focus()

    def _focus_order(self) -> list[type]:
        return [SchemaTree, ResultTable, PropertyPanel]

    def action_focus_next(self) -> None:
        order = self._focus_order()
        try:
            idx = next(i for i, cls in enumerate(order) if isinstance(self.focused, cls))
            next_idx = (idx + 1) % len(order)
        except (StopIteration, TypeError):
            next_idx = 0
        self.query_one(order[next_idx]).focus()

    def action_focus_previous(self) -> None:
        order = self._focus_order()
        try:
            idx = next(i for i, cls in enumerate(order) if isinstance(self.focused, cls))
            prev_idx = (idx - 1) % len(order)
        except (StopIteration, TypeError):
            prev_idx = 0
        self.query_one(order[prev_idx]).focus()

    def action_connect(self) -> None:
        from vql.screens.connect import ConnectionList
        self.app.push_screen(ConnectionList(), self._on_connect)

    def _on_connect(self, config) -> None:
        if config is not None:
            self.app.connect_to_db(config)

    async def action_refresh(self) -> None:
        if self.adapter:
            await self._load_schema()

    def action_quit(self) -> None:
        self.app.exit()
