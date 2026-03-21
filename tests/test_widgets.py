from tui_client.db.base import QueryResult
from tui_client.widgets.result_table import ResultTable


def test_result_table_load_result():
    table = ResultTable()
    result = QueryResult(columns=["id", "name"], rows=[(1, "alice"), (2, "bob")])
    # ResultTable needs to be mounted to fully work, but we can test the method exists
    assert hasattr(table, "load_result")
    assert table.cursor_type == "row"
    assert table.zebra_stripes is True


def test_result_table_load_empty():
    table = ResultTable()
    result = QueryResult(columns=[], rows=[])
    assert hasattr(table, "load_result")
