from __future__ import annotations

from pathlib import Path

from agentic_ops.config import settings


def _migration_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "infra" / "migrations" / "001_ops05a.sql"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "infra" / "migrations" / "001_ops05a.sql"


_MIGRATION = _migration_path()


def connect():
    import psycopg

    return psycopg.connect(settings.database_url, autocommit=True)


def init_schema() -> None:
    sql = _MIGRATION.read_text(encoding="utf-8")
    with connect() as conn:
        conn.execute(sql)


def next_audit_seq(conn, run_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 FROM audit_events WHERE run_id = %s",
        (run_id,),
    ).fetchone()
    return int(row[0]) if row else 1
