from tui_client.widgets.db_header import DbHeader


def test_db_header_default_text():
    header = DbHeader()
    assert header.db_name == ""


def test_db_header_set_db_name():
    header = DbHeader()
    header.set_db_name("local", "alice@localhost:5432/mydb")
    assert header.db_name == "local (alice@localhost:5432/mydb)"
