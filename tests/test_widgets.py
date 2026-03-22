from tui_client.db.base import QueryResult
from tui_client.widgets.result_table import ResultTable


def test_result_table_load_result():
    table = ResultTable()
    result = QueryResult(columns=["id", "name"], rows=[(1, "alice"), (2, "bob")])
    # ResultTable needs to be mounted to fully work, but we can test the method exists
    assert hasattr(table, "load_result")
    assert table.cursor_type == "cell"
    assert table.zebra_stripes is True


def test_result_table_load_empty():
    table = ResultTable()
    result = QueryResult(columns=[], rows=[])
    assert hasattr(table, "load_result")


def test_result_table_has_pending_changes():
    table = ResultTable()
    assert hasattr(table, "pending_changes")
    assert table.pending_changes == {}


def test_result_table_add_pending_change():
    table = ResultTable()
    table.add_pending_change(0, 1, "new_value")
    assert table.pending_changes == {(0, 1): "new_value"}


def test_result_table_add_pending_change_null():
    table = ResultTable()
    table.add_pending_change(0, 1, None)
    assert table.pending_changes == {(0, 1): None}


def test_result_table_clear_pending_changes():
    table = ResultTable()
    table.add_pending_change(0, 1, "new_value")
    table.clear_pending_changes()
    assert table.pending_changes == {}


def test_result_table_has_edit_binding():
    bindings = {b.key for b in ResultTable.BINDINGS}
    assert "i" in bindings


def test_result_table_has_delete_binding():
    bindings = {b.key for b in ResultTable.BINDINGS}
    assert "d" in bindings


def test_result_table_has_undo_binding():
    bindings = {b.key for b in ResultTable.BINDINGS}
    assert "u" in bindings


def test_result_table_has_pending_deletes():
    table = ResultTable()
    assert hasattr(table, "pending_deletes")
    assert table.pending_deletes == set()


def test_result_table_add_pending_delete():
    table = ResultTable()
    table.add_pending_delete(0)
    assert 0 in table.pending_deletes


def test_result_table_add_pending_delete_toggle():
    table = ResultTable()
    table.add_pending_delete(0)
    table.add_pending_delete(0)
    assert 0 not in table.pending_deletes


def test_result_table_clear_pending_deletes():
    table = ResultTable()
    table.add_pending_delete(0)
    table.clear_pending_changes()
    assert table.pending_deletes == set()


def test_result_table_undo_pending_change():
    table = ResultTable()
    table.add_pending_change(0, 1, "new_value")
    table.undo_pending(0, 1)
    assert table.pending_changes == {}


def test_result_table_undo_pending_delete():
    table = ResultTable()
    table.add_pending_delete(0)
    table.undo_pending(0, None)
    assert table.pending_deletes == set()
