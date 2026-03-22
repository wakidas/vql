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


@dataclass
class UpdateResult:
    updated_count: int


@dataclass
class DeleteResult:
    deleted_count: int


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
    async def update(
        self,
        schema: str,
        table: str,
        pk_columns: list[str],
        pk_values: list,
        update_columns: list[str],
        update_values: list,
    ) -> UpdateResult: ...

    @abstractmethod
    async def delete(
        self,
        schema: str,
        table: str,
        pk_columns: list[str],
        pk_values: list,
    ) -> DeleteResult: ...

    @abstractmethod
    async def close(self) -> None: ...
