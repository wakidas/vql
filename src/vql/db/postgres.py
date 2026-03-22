from __future__ import annotations

import psycopg
from psycopg import sql

from .base import DBAdapter, Column, Table, QueryResult, UpdateResult, DeleteResult


class PostgresAdapter(DBAdapter):
    def __init__(self) -> None:
        self._conn: psycopg.AsyncConnection | None = None

    async def connect(self, *, host: str, port: int, dbname: str, user: str, password: str | None = None) -> None:
        kwargs: dict = dict(host=host, port=port, dbname=dbname, user=user, autocommit=True)
        if password:
            kwargs["password"] = password
        self._conn = await psycopg.AsyncConnection.connect(**kwargs)

    @property
    def conn(self) -> psycopg.AsyncConnection:
        if self._conn is None:
            raise RuntimeError("Not connected")
        return self._conn

    async def get_tables(self, schema: str = "public") -> list[Table]:
        cur = await self.conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = 'BASE TABLE' "
            "ORDER BY table_name",
            (schema,),
        )
        rows = await cur.fetchall()
        return [Table(name=row[0], schema=schema) for row in rows]

    async def get_columns(self, schema: str, table: str) -> list[Column]:
        cur = await self.conn.execute(
            "SELECT c.column_name, c.data_type, c.is_nullable, "
            "  CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN true ELSE false END as is_pk "
            "FROM information_schema.columns c "
            "LEFT JOIN information_schema.key_column_usage kcu "
            "  ON c.table_schema = kcu.table_schema "
            "  AND c.table_name = kcu.table_name "
            "  AND c.column_name = kcu.column_name "
            "LEFT JOIN information_schema.table_constraints tc "
            "  ON kcu.constraint_name = tc.constraint_name "
            "  AND tc.constraint_type = 'PRIMARY KEY' "
            "WHERE c.table_schema = %s AND c.table_name = %s "
            "ORDER BY c.ordinal_position",
            (schema, table),
        )
        rows = await cur.fetchall()
        return [
            Column(
                name=row[0],
                data_type=row[1],
                is_nullable=row[2] == "YES",
                is_primary_key=row[3],
            )
            for row in rows
        ]

    async def execute(self, query: str | sql.Composable) -> QueryResult:
        cur = await self.conn.execute(query)
        if cur.description is None:
            return QueryResult(columns=[], rows=[])
        columns = [desc[0] for desc in cur.description]
        rows = await cur.fetchall()
        return QueryResult(columns=columns, rows=[tuple(row) for row in rows])

    async def update(
        self,
        schema: str,
        table: str,
        pk_columns: list[str],
        pk_values: list,
        update_columns: list[str],
        update_values: list,
    ) -> UpdateResult:
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in update_columns
        )
        where_clause = sql.SQL(" AND ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in pk_columns
        )
        query = sql.SQL("UPDATE {}.{} SET {} WHERE {}").format(
            sql.Identifier(schema),
            sql.Identifier(table),
            set_clause,
            where_clause,
        )
        params = list(update_values) + list(pk_values)
        cur = await self.conn.execute(query, params)
        return UpdateResult(updated_count=cur.rowcount)

    async def delete(
        self,
        schema: str,
        table: str,
        pk_columns: list[str],
        pk_values: list,
    ) -> DeleteResult:
        where_clause = sql.SQL(" AND ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in pk_columns
        )
        query = sql.SQL("DELETE FROM {}.{} WHERE {}").format(
            sql.Identifier(schema),
            sql.Identifier(table),
            where_clause,
        )
        cur = await self.conn.execute(query, pk_values)
        return DeleteResult(deleted_count=cur.rowcount)

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
