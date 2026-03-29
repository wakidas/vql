from psycopg.types.json import Json, Jsonb

from vql.db.base import Column
from vql.screens.main import MainScreen


def test_prepare_update_value_wraps_json_column():
    screen = MainScreen()
    screen._current_columns = [Column(name="detail_json", data_type="json", is_nullable=True)]

    value = screen._prepare_update_value("detail_json", '{"name": "alice"}')

    assert isinstance(value, Json)
    assert value.obj == {"name": "alice"}


def test_prepare_update_value_wraps_jsonb_column():
    screen = MainScreen()
    screen._current_columns = [Column(name="detail_json", data_type="jsonb", is_nullable=True)]

    value = screen._prepare_update_value("detail_json", '{"name": "alice"}')

    assert isinstance(value, Jsonb)
    assert value.obj == {"name": "alice"}


def test_prepare_update_value_rejects_invalid_json():
    screen = MainScreen()
    screen._current_columns = [Column(name="detail_json", data_type="jsonb", is_nullable=True)]

    try:
        screen._prepare_update_value("detail_json", "{'name': 'alice'}")
    except ValueError as error:
        assert "detail_json must be valid JSON" in str(error)
    else:
        raise AssertionError("Expected ValueError for invalid JSON input")
