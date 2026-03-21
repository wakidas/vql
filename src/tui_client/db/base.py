from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Table:
    name: str
    schema: str


@dataclass
class Column:
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple]


class DBAdapter(ABC):
    @abstractmethod
    async def connect(self, **kwargs) -> None: ...

    @abstractmethod
    async def get_tables(self, schema: str = "public") -> list[Table]: ...

    @abstractmethod
    async def get_columns(self, schema: str, table: str) -> list[Column]: ...

    @abstractmethod
    async def execute(self, query) -> QueryResult: ...

    @abstractmethod
    async def close(self) -> None: ...
