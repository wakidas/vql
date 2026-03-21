import pytest

from tui_client.db.base import DBAdapter, Column, Table, QueryResult


def test_db_adapter_is_abstract():
    with pytest.raises(TypeError):
        DBAdapter()


def test_table_dataclass():
    t = Table(name="users", schema="public")
    assert t.name == "users"
    assert t.schema == "public"


def test_column_dataclass():
    c = Column(name="id", data_type="integer", is_nullable=False, is_primary_key=True)
    assert c.name == "id"
    assert c.is_primary_key is True


def test_query_result():
    result = QueryResult(columns=["id", "name"], rows=[(1, "alice"), (2, "bob")])
    assert len(result.rows) == 2
    assert result.columns == ["id", "name"]
