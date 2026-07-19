"""Metadata repositories and immutable content-addressed snapshots."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Protocol

import pandas as pd
import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
from psycopg.types.json import Jsonb


class Repository(Protocol):
    def save(self, kind: str, record_id: str, payload: dict[str, Any]) -> None: ...

    def get(self, kind: str, record_id: str) -> dict[str, Any] | None: ...

    def list(self, kind: str) -> list[dict[str, Any]]: ...


class MemoryRepository:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], dict[str, Any]] = {}

    def save(self, kind: str, record_id: str, payload: dict[str, Any]) -> None:
        self.records[(kind, record_id)] = json.loads(json.dumps(payload, default=str))

    def get(self, kind: str, record_id: str) -> dict[str, Any] | None:
        value = self.records.get((kind, record_id))
        return None if value is None else json.loads(json.dumps(value))

    def list(self, kind: str) -> list[dict[str, Any]]:
        return [value for (record_kind, _), value in self.records.items() if record_kind == kind]


class SQLiteRepository:
    """Durable zero-configuration metadata storage for local Krisk usage."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def migrate(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS krisk_records (
                    kind TEXT NOT NULL,
                    id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (kind, id)
                )
                """
            )

    def save(self, kind: str, record_id: str, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, default=str)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO krisk_records (kind, id, payload)
                VALUES (?, ?, ?)
                ON CONFLICT (kind, id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (kind, record_id, encoded),
            )

    def get(self, kind: str, record_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM krisk_records WHERE kind = ? AND id = ?",
                (kind, record_id),
            ).fetchone()
        return None if row is None else json.loads(row[0])

    def list(self, kind: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM krisk_records WHERE kind = ? ORDER BY updated_at DESC, id",
                (kind,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]


class PostgresRepository:
    def __init__(self, url: str) -> None:
        self.url = url
        self.migrate()

    def migrate(self) -> None:
        with psycopg.connect(self.url) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS krisk_records (
                    kind text NOT NULL,
                    id uuid NOT NULL,
                    payload jsonb NOT NULL,
                    updated_at timestamptz NOT NULL DEFAULT now(),
                    PRIMARY KEY (kind, id)
                )
                """
            )

    def save(self, kind: str, record_id: str, payload: dict[str, Any]) -> None:
        with psycopg.connect(self.url) as connection:
            connection.execute(
                """
                INSERT INTO krisk_records (kind, id, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (kind, id) DO UPDATE
                SET payload = EXCLUDED.payload, updated_at = now()
                """,
                (kind, record_id, Jsonb(payload)),
            )

    def get(self, kind: str, record_id: str) -> dict[str, Any] | None:
        with psycopg.connect(self.url) as connection:
            row = connection.execute(
                "SELECT payload FROM krisk_records WHERE kind = %s AND id = %s",
                (kind, record_id),
            ).fetchone()
        return None if row is None else row[0]

    def list(self, kind: str) -> list[dict[str, Any]]:
        with psycopg.connect(self.url) as connection:
            rows = connection.execute(
                "SELECT payload FROM krisk_records WHERE kind = %s ORDER BY updated_at DESC",
                (kind,),
            ).fetchall()
        return [row[0] for row in rows]


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_frame(
        self,
        frame: pd.DataFrame,
        max_bytes: int | None = None,
    ) -> tuple[str, Path, int]:
        table = pa.Table.from_pandas(frame, preserve_index=False)
        sink = pa.BufferOutputStream()
        pq.write_table(table, sink, compression="zstd")
        data = sink.getvalue().to_pybytes()
        if max_bytes is not None and len(data) > max_bytes:
            raise ValueError(
                f"Chart snapshot exceeds {max_bytes / (1024 * 1024):g} MiB; "
                "aggregate or downsample the query"
            )
        digest = hashlib.sha256(data).hexdigest()
        target = self.root / f"{digest}.parquet"
        if not target.exists():
            descriptor, temp_name = tempfile.mkstemp(prefix=".krisk-", dir=self.root)
            try:
                with os.fdopen(descriptor, "wb") as file:
                    file.write(data)
                    file.flush()
                    os.fsync(file.fileno())
                Path(temp_name).replace(target)
            finally:
                Path(temp_name).unlink(missing_ok=True)
        return digest, target, len(data)

    def load_frame(self, path: str | Path) -> pd.DataFrame:
        resolved = Path(path).resolve()
        if not resolved.is_relative_to(self.root.resolve()):
            raise ValueError("Snapshot path escapes the artifact directory")
        return pd.read_parquet(resolved)


def default_repository() -> Repository:
    url = os.environ.get("DATABASE_URL")
    if url:
        return PostgresRepository(url)
    data_dir = Path(os.environ.get("KRISK_DATA_DIR", "var/krisk"))
    database_path = Path(os.environ.get("KRISK_DATABASE_PATH", data_dir / "krisk.db"))
    return SQLiteRepository(database_path)
