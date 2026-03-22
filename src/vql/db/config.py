from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "vql" / "connections.toml"


@dataclass
class ConnectionConfig:
    name: str
    driver: str
    host: str
    port: int
    database: str
    user: str
    password: str | None = None


def load_connections(path: Path = DEFAULT_CONFIG_PATH) -> list[ConnectionConfig]:
    if not path.exists():
        return []
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return [ConnectionConfig(**conn) for conn in data.get("connections", [])]


def save_connection(config: ConnectionConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    existing = load_connections(path)
    existing.append(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for conn in existing:
        lines.append("[[connections]]")
        d = asdict(conn)
        for k, v in d.items():
            if v is None:
                continue
            if isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, int):
                lines.append(f"{k} = {v}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n")
    os.chmod(path, 0o600)
