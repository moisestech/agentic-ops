from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from agentic_ops.models import RunRecord, RunStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


class RunStore:
    """In-memory run store. Postgres persistence is the next slice."""

    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}

    def create(self, question: str, org_slug: str) -> RunRecord:
        now = utcnow()
        record = RunRecord(
            id=str(uuid4()),
            status="queued",
            question=question,
            org_slug=org_slug,
            created_at=now,
            updated_at=now,
        )
        self._runs[record.id] = record
        return record

    def get(self, run_id: str) -> RunRecord | None:
        return self._runs.get(run_id)

    def list(self) -> list[RunRecord]:
        return sorted(self._runs.values(), key=lambda item: item.created_at, reverse=True)

    def update(self, run_id: str, **fields: Any) -> RunRecord:
        record = self._runs[run_id]
        payload = record.model_dump()
        payload.update(fields)
        payload["updated_at"] = utcnow()
        updated = RunRecord.model_validate(payload)
        self._runs[run_id] = updated
        return updated

    def set_status(self, run_id: str, status: RunStatus) -> RunRecord:
        return self.update(run_id, status=status)

    def insert(self, record: RunRecord) -> RunRecord:
        self._runs[record.id] = record
        return record


store = RunStore()
