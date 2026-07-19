"""Named, read-only data sources used by REST and MCP."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import psycopg
import sqlglot
from psycopg.rows import dict_row
from sqlglot import expressions as exp


class SourceError(ValueError):
    pass


BLOCKED_FUNCTIONS = {
    "dblink",
    "dblink_connect",
    "dblink_connect_u",
    "dblink_exec",
    "getenv",
    "glob",
    "lo_export",
    "lo_import",
    "pg_ls_dir",
    "pg_read_binary_file",
    "pg_read_file",
    "pg_stat_file",
    "query",
    "query_table",
}
BLOCKED_FUNCTION_PREFIXES = (
    "azure_",
    "csv_scan",
    "delta_scan",
    "dblink_",
    "gcs_",
    "http_",
    "iceberg_scan",
    "mysql_",
    "parquet_scan",
    "pg_ls_",
    "pg_read_",
    "postgres_",
    "read_",
    "s3_",
    "sqlite_",
)


def validate_readonly_sql(sql: str, allowed_relations: set[str] | None = None) -> str:
    try:
        statements = sqlglot.parse(sql)
    except sqlglot.errors.ParseError as error:
        raise SourceError(f"Invalid SQL: {error}") from error
    if len(statements) != 1:
        raise SourceError("Exactly one SQL statement is required")
    statement = statements[0]
    if statement is None:
        raise SourceError("Only read-only SELECT/WITH queries are allowed")
    forbidden = tuple(
        expression
        for name in (
            "Insert",
            "Update",
            "Delete",
            "Create",
            "Drop",
            "Alter",
            "Command",
            "Copy",
            "Merge",
            "Transaction",
            "Into",
            "Grant",
            "Revoke",
            "Set",
            "Execute",
        )
        if (expression := getattr(exp, name, None)) is not None
    )
    if any(statement.find(kind) is not None for kind in forbidden):
        raise SourceError("Only read-only SELECT/WITH queries are allowed")
    if statement.find(exp.Select) is None:
        raise SourceError("Only read-only SELECT/WITH queries are allowed")
    for function in statement.find_all(exp.Func):
        name = (function.name or function.sql_name()).casefold()
        if name in BLOCKED_FUNCTIONS or name.startswith(BLOCKED_FUNCTION_PREFIXES):
            raise SourceError(f"Function {name!r} is not available in read-only queries")
    if allowed_relations is not None:
        allowed = {name.casefold() for name in allowed_relations}
        cte_names = {cte.alias_or_name.casefold() for cte in statement.find_all(exp.CTE)}
        for table in statement.find_all(exp.Table):
            if not table.name:
                raise SourceError("Table functions are not available in local read-only sources")
            name = table.name.casefold()
            if table.catalog or table.db or name not in allowed | cte_names:
                raise SourceError(f"Relation {table.sql()!r} is not available in this source")
    return sql.strip().rstrip(";")


@dataclass(frozen=True)
class SourceConfig:
    name: str
    kind: str
    url_env: str | None = None
    root: Path | None = None


class DataSource:
    def list_relations(self) -> list[str]:
        raise NotImplementedError

    def describe(self, relation: str) -> list[dict[str, str]]:
        raise NotImplementedError

    def execute(
        self, sql: str, parameters: dict[str, Any] | None = None, limit: int = 10_000
    ) -> pd.DataFrame:
        raise NotImplementedError

    def fingerprint(self) -> str:
        raise NotImplementedError

    def health(self) -> str:
        try:
            self.list_relations()
        except Exception:
            return "error"
        return "ok"


class PostgresSource(DataSource):
    def __init__(self, url: str) -> None:
        self.url = url

    def list_relations(self) -> list[str]:
        sql = """
        SELECT table_schema || '.' || table_name AS name
        FROM information_schema.tables
        WHERE table_type IN ('BASE TABLE', 'VIEW')
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 1
        """
        return self.execute(sql, limit=2_000)["name"].tolist()

    def describe(self, relation: str) -> list[dict[str, str]]:
        schema, _, table = relation.partition(".")
        if not table:
            schema, table = "public", schema
        sql = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %(schema)s AND table_name = %(table)s
        ORDER BY ordinal_position
        """
        return self.execute(sql, {"schema": schema, "table": table}, limit=1_000).to_dict(
            orient="records"
        )

    def execute(
        self, sql: str, parameters: dict[str, Any] | None = None, limit: int = 10_000
    ) -> pd.DataFrame:
        safe_sql = validate_readonly_sql(sql)
        wrapped = f"SELECT * FROM ({safe_sql}) AS krisk_query LIMIT {int(limit) + 1}"
        with (
            psycopg.connect(self.url, row_factory=dict_row) as connection,
            connection.transaction(),
        ):
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '30s'")
            rows = connection.execute(wrapped, parameters or {}).fetchall()
        if len(rows) > limit:
            raise SourceError(f"Query exceeds the {limit:,}-row result limit; aggregate it first")
        return pd.DataFrame(rows)

    def fingerprint(self) -> str:
        return _fingerprint({"kind": "postgres", "relations": self.list_relations()})


class FileSource(DataSource):
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        if not self.root.exists() or not self.root.is_dir():
            raise SourceError(f"File source directory does not exist: {self.root}")

    def _files(self) -> dict[str, Path]:
        files: dict[str, Path] = {}
        for suffix in ("*.csv", "*.parquet"):
            for path in self.root.glob(suffix):
                resolved = path.resolve()
                if not resolved.is_relative_to(self.root):
                    continue
                files[path.stem] = resolved
        return files

    def _connection(self) -> duckdb.DuckDBPyConnection:
        connection = duckdb.connect(":memory:")
        for name, path in self._files().items():
            escaped = str(path).replace("'", "''")
            identifier = name.replace('"', '""')
            reader = "read_csv_auto" if path.suffix.lower() == ".csv" else "read_parquet"
            connection.execute(
                f"CREATE TABLE \"{identifier}\" AS SELECT * FROM {reader}('{escaped}')"
            )
        connection.execute("SET enable_external_access = false")
        connection.execute("SET lock_configuration = true")
        return connection

    def list_relations(self) -> list[str]:
        return sorted(self._files())

    def describe(self, relation: str) -> list[dict[str, str]]:
        if relation not in self._files():
            raise SourceError(f"Unknown relation: {relation}")
        with self._connection() as connection:
            frame = connection.execute(f'DESCRIBE "{relation}"').fetchdf()
        return frame[["column_name", "column_type", "null"]].to_dict(orient="records")

    def execute(
        self, sql: str, parameters: dict[str, Any] | None = None, limit: int = 10_000
    ) -> pd.DataFrame:
        if parameters:
            raise SourceError("Named SQL parameters are currently supported for PostgreSQL only")
        safe_sql = validate_readonly_sql(sql, set(self._files()))
        with self._connection() as connection:
            frame = _duckdb_frame(
                connection, f"SELECT * FROM ({safe_sql}) AS krisk_query LIMIT {int(limit) + 1}"
            )
        if len(frame) > limit:
            raise SourceError(f"Query exceeds the {limit:,}-row result limit; aggregate it first")
        return frame

    def fingerprint(self) -> str:
        files = self._files()
        return _fingerprint(
            {
                "kind": "files",
                "files": [
                    {
                        "name": name,
                        "size": path.stat().st_size,
                        "modified_ns": path.stat().st_mtime_ns,
                    }
                    for name, path in sorted(files.items())
                ],
            }
        )


class FrameSource(DataSource):
    """In-memory source for tests, demos, and notebook-driven local sessions."""

    def __init__(self, frames: dict[str, pd.DataFrame]) -> None:
        self.frames = {name: frame.copy() for name, frame in frames.items()}

    def list_relations(self) -> list[str]:
        return sorted(self.frames)

    def describe(self, relation: str) -> list[dict[str, str]]:
        frame = self.frames[relation]
        return [
            {"column_name": str(column), "data_type": str(dtype), "is_nullable": "YES"}
            for column, dtype in frame.dtypes.items()
        ]

    def execute(
        self, sql: str, parameters: dict[str, Any] | None = None, limit: int = 10_000
    ) -> pd.DataFrame:
        if parameters:
            raise SourceError("In-memory sources do not accept SQL parameters")
        safe_sql = validate_readonly_sql(sql, set(self.frames))
        with duckdb.connect(":memory:") as connection:
            for name, frame in self.frames.items():
                connection.register(name, frame)
            connection.execute("SET enable_external_access = false")
            connection.execute("SET lock_configuration = true")
            result = _duckdb_frame(
                connection, f"SELECT * FROM ({safe_sql}) AS krisk_query LIMIT {int(limit) + 1}"
            )
        if len(result) > limit:
            raise SourceError(f"Query exceeds the {limit:,}-row result limit; aggregate it first")
        return result

    def fingerprint(self) -> str:
        return _fingerprint(
            {
                "kind": "frames",
                "relations": {
                    name: {
                        "rows": len(frame),
                        "columns": [
                            (str(column), str(dtype)) for column, dtype in frame.dtypes.items()
                        ],
                    }
                    for name, frame in sorted(self.frames.items())
                },
            }
        )


class SourceRegistry:
    def __init__(self, sources: dict[str, DataSource] | None = None) -> None:
        self.sources = sources or {}

    @classmethod
    def from_toml(cls, path: Path) -> SourceRegistry:
        if not path.exists():
            return cls()
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        sources: dict[str, DataSource] = {}
        for name, values in raw.get("sources", {}).items():
            kind = values.get("kind")
            if kind == "postgres":
                env_name = values.get("url_env")
                url = os.environ.get(env_name or "")
                if not url:
                    raise SourceError(f"Source {name!r} requires environment variable {env_name!r}")
                sources[name] = PostgresSource(url)
            elif kind == "files":
                root = Path(values.get("root", "."))
                if not root.is_absolute():
                    root = path.parent / root
                sources[name] = FileSource(root)
            else:
                raise SourceError(f"Unsupported source kind for {name!r}: {kind!r}")
        return cls(sources)

    def register(self, name: str, source: DataSource) -> None:
        self.sources[name] = source

    def get(self, name: str) -> DataSource:
        try:
            return self.sources[name]
        except KeyError as error:
            raise SourceError(f"Unknown source: {name}") from error

    def list_sources(self) -> list[dict[str, str]]:
        result = []
        for name, source in sorted(self.sources.items()):
            status = source.health()
            try:
                fingerprint = source.fingerprint() if status == "ok" else "unavailable"
            except Exception:
                status = "error"
                fingerprint = "unavailable"
            result.append(
                {
                    "name": name,
                    "kind": type(source).__name__,
                    "status": status,
                    "fingerprint": fingerprint,
                }
            )
        return result


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _duckdb_frame(connection: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    timer = threading.Timer(30, connection.interrupt)
    timer.daemon = True
    timer.start()
    try:
        return connection.execute(sql).fetchdf()
    finally:
        timer.cancel()
