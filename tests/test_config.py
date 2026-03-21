import tomllib
from pathlib import Path

from tui_client.db.config import ConnectionConfig, load_connections, save_connection


def test_connection_config_fields():
    config = ConnectionConfig(
        name="test",
        driver="postgres",
        host="localhost",
        port=5432,
        database="mydb",
        user="postgres",
        password="secret",
    )
    assert config.host == "localhost"
    assert config.password == "secret"


def test_connection_config_no_password():
    config = ConnectionConfig(
        name="test",
        driver="postgres",
        host="localhost",
        port=5432,
        database="mydb",
        user="postgres",
    )
    assert config.password is None


def test_save_connection_sets_file_permissions(tmp_path: Path):
    import os
    config_file = tmp_path / "connections.toml"
    config = ConnectionConfig(
        name="test", driver="postgres", host="localhost",
        port=5432, database="db", user="u", password="p",
    )
    save_connection(config, config_file)
    mode = os.stat(config_file).st_mode & 0o777
    assert mode == 0o600


def test_load_connections_empty(tmp_path: Path):
    config_file = tmp_path / "connections.toml"
    result = load_connections(config_file)
    assert result == []


def test_load_connections(tmp_path: Path):
    config_file = tmp_path / "connections.toml"
    config_file.write_text("""\
[[connections]]
name = "local"
driver = "postgres"
host = "localhost"
port = 5432
database = "testdb"
user = "postgres"
password = "pass"
""")
    result = load_connections(config_file)
    assert len(result) == 1
    assert result[0].name == "local"
    assert result[0].database == "testdb"


def test_save_connection(tmp_path: Path):
    config_file = tmp_path / "connections.toml"
    config = ConnectionConfig(
        name="new",
        driver="postgres",
        host="localhost",
        port=5432,
        database="newdb",
        user="user",
        password="pw",
    )
    save_connection(config, config_file)

    with open(config_file, "rb") as f:
        data = tomllib.load(f)
    assert len(data["connections"]) == 1
    assert data["connections"][0]["name"] == "new"


def test_save_connection_appends(tmp_path: Path):
    config_file = tmp_path / "connections.toml"
    config_file.write_text("""\
[[connections]]
name = "existing"
driver = "postgres"
host = "localhost"
port = 5432
database = "db1"
user = "u1"
""")
    config = ConnectionConfig(
        name="second",
        driver="postgres",
        host="localhost",
        port=5432,
        database="db2",
        user="u2",
    )
    save_connection(config, config_file)

    result = load_connections(config_file)
    assert len(result) == 2
    assert result[0].name == "existing"
    assert result[1].name == "second"
