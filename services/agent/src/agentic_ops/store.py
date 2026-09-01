from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from agentic_ops.config import settings
from agentic_ops.models import AuditEvent, DecisionRequest, InternalTask, RunRecord, RunStatus

DecisionOutcome = Literal["created", "same", "conflict"]


def utcnow() -> datetime:
    return datetime.now(UTC)


class MemoryRunStore:
    """Process-local store used when AGENT_PERSISTENCE=memory."""

    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}
        self._decisions: dict[str, DecisionRequest] = {}
        self._tasks: dict[str, InternalTask] = {}
        self._tasks_by_run: dict[str, str] = {}
        self._audit: dict[str, list[AuditEvent]] = {}

    def close(self) -> None:
        return

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
        self.append_audit(record.id, "run_created", "queued", {"org_slug": org_slug})
        return record

    def get(self, run_id: str, org_slug: str | None = None) -> RunRecord | None:
        record = self._runs.get(run_id)
        if record is None:
            return None
        if org_slug and record.org_slug != org_slug:
            return None
        return self.hydrate(record)

    def list(self, org_slug: str | None = None) -> list[RunRecord]:
        records = [
            self.hydrate(item)
            for item in self._runs.values()
            if org_slug is None or item.org_slug == org_slug
        ]
        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def update(self, run_id: str, **fields: Any) -> RunRecord:
        record = self._runs[run_id]
        payload = record.model_dump()
        payload.update(fields)
        payload["updated_at"] = utcnow()
        updated = RunRecord.model_validate(payload)
        self._runs[run_id] = updated
        return self.hydrate(updated)

    def set_status(self, run_id: str, status: RunStatus) -> RunRecord:
        return self.update(run_id, status=status)

    def insert(self, record: RunRecord) -> RunRecord:
        self._runs[record.id] = record
        return self.hydrate(record)

    def record_decision(self, run_id: str, request: DecisionRequest) -> DecisionOutcome:
        existing = self._decisions.get(run_id)
        if existing is not None:
            if (
                existing.decision == request.decision
                and (existing.edited_draft or None) == (request.edited_draft or None)
            ):
                return "same"
            return "conflict"
        self._decisions[run_id] = request
        self.append_audit(
            run_id,
            "decision",
            request.decision,
            {"note": request.note, "edited": bool(request.edited_draft)},
        )
        return "created"

    def get_decision(self, run_id: str) -> DecisionRequest | None:
        return self._decisions.get(run_id)

    def create_internal_task(
        self,
        *,
        run: RunRecord,
        title: str,
        body: str,
        risk: str,
        citation_ids: list[str],
        reviewer_decision: str,
        reviewer_note: str | None,
    ) -> InternalTask:
        existing_id = self._tasks_by_run.get(run.id)
        if existing_id:
            return self._tasks[existing_id]
        task = InternalTask(
            id=str(uuid4()),
            originating_run_id=run.id,
            title=title,
            body=body,
            status="open",
            risk=risk,  # type: ignore[arg-type]
            org_slug=run.org_slug,
            citation_ids=citation_ids,
            reviewer_decision=reviewer_decision,  # type: ignore[arg-type]
            reviewer_note=reviewer_note,
            created_at=utcnow(),
            idempotency_key=f"task:{run.id}",
        )
        self._tasks[task.id] = task
        self._tasks_by_run[run.id] = task.id
        self.append_audit(run.id, "internal_task", "open", {"task_id": task.id})
        return task

    def get_internal_task(self, run_id: str, org_slug: str | None = None) -> InternalTask | None:
        task_id = self._tasks_by_run.get(run_id)
        if not task_id:
            return None
        task = self._tasks[task_id]
        if org_slug and task.org_slug != org_slug:
            return None
        return task

    def append_audit(
        self,
        run_id: str,
        kind: str,
        detail: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        events = self._audit.setdefault(run_id, [])
        event = AuditEvent(
            run_id=run_id,
            seq=len(events) + 1,
            at=utcnow(),
            kind=kind,
            detail=detail,
            data=data or {},
        )
        events.append(event)
        return event

    def list_audit(self, run_id: str) -> list[AuditEvent]:
        return list(self._audit.get(run_id, []))

    def hydrate(self, record: RunRecord) -> RunRecord:
        task = self.get_internal_task(record.id)
        return record.model_copy(
            update={
                "internal_task": task,
                "internal_task_id": task.id if task else record.internal_task_id,
                "audit_events": self.list_audit(record.id),
            }
        )


class PostgresRunStore:
    def __init__(self) -> None:
        from agentic_ops.db import init_schema

        init_schema()

    def close(self) -> None:
        return

    def _conn(self):
        from agentic_ops.db import connect

        return connect()

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
        self._upsert(record)
        self.append_audit(record.id, "run_created", "queued", {"org_slug": org_slug})
        return self.hydrate(record)

    def get(self, run_id: str, org_slug: str | None = None) -> RunRecord | None:
        with self._conn() as conn:
            if org_slug:
                row = conn.execute(
                    "SELECT payload FROM runs WHERE id = %s AND org_slug = %s",
                    (run_id, org_slug),
                ).fetchone()
            else:
                row = conn.execute("SELECT payload FROM runs WHERE id = %s", (run_id,)).fetchone()
        if row is None:
            return None
        return self.hydrate(RunRecord.model_validate(row[0]))

    def list(self, org_slug: str | None = None) -> list[RunRecord]:
        with self._conn() as conn:
            if org_slug:
                rows = conn.execute(
                    "SELECT payload FROM runs WHERE org_slug = %s ORDER BY created_at DESC",
                    (org_slug,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT payload FROM runs ORDER BY created_at DESC").fetchall()
        return [self.hydrate(RunRecord.model_validate(row[0])) for row in rows]

    def update(self, run_id: str, **fields: Any) -> RunRecord:
        record = self.get(run_id)
        if record is None:
            raise KeyError(run_id)
        payload = record.model_dump()
        payload.update(fields)
        payload["updated_at"] = utcnow()
        updated = RunRecord.model_validate(payload)
        self._upsert(updated)
        return self.hydrate(updated)

    def set_status(self, run_id: str, status: RunStatus) -> RunRecord:
        return self.update(run_id, status=status)

    def insert(self, record: RunRecord) -> RunRecord:
        self._upsert(record)
        return self.hydrate(record)

    def _upsert(self, record: RunRecord) -> None:
        slim = record.model_copy(update={"internal_task": None, "audit_events": []})
        payload = slim.model_dump(mode="json")
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO runs (id, org_slug, status, payload, created_at, updated_at)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    org_slug = EXCLUDED.org_slug,
                    status = EXCLUDED.status,
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    record.id,
                    record.org_slug,
                    record.status,
                    __import__("json").dumps(payload),
                    record.created_at,
                    record.updated_at,
                ),
            )

    def record_decision(self, run_id: str, request: DecisionRequest) -> DecisionOutcome:
        record = self.get(run_id)
        if record is None:
            raise KeyError(run_id)
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT decision, edited_draft FROM decisions WHERE run_id = %s",
                (run_id,),
            ).fetchone()
            if existing is not None:
                same_edit = (existing[1] or None) == (request.edited_draft or None)
                if existing[0] == request.decision and same_edit:
                    return "same"
                return "conflict"
            conn.execute(
                """
                INSERT INTO decisions (run_id, org_slug, decision, note, edited_draft, decided_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    record.org_slug,
                    request.decision,
                    request.note,
                    request.edited_draft,
                    utcnow(),
                ),
            )
        self.append_audit(
            run_id,
            "decision",
            request.decision,
            {"note": request.note, "edited": bool(request.edited_draft)},
        )
        return "created"

    def get_decision(self, run_id: str) -> DecisionRequest | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT decision, note, edited_draft FROM decisions WHERE run_id = %s",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return DecisionRequest(decision=row[0], note=row[1], edited_draft=row[2])

    def create_internal_task(
        self,
        *,
        run: RunRecord,
        title: str,
        body: str,
        risk: str,
        citation_ids: list[str],
        reviewer_decision: str,
        reviewer_note: str | None,
    ) -> InternalTask:
        existing = self.get_internal_task(run.id)
        if existing:
            return existing
        import json

        task = InternalTask(
            id=str(uuid4()),
            originating_run_id=run.id,
            title=title,
            body=body,
            status="open",
            risk=risk,  # type: ignore[arg-type]
            org_slug=run.org_slug,
            citation_ids=citation_ids,
            reviewer_decision=reviewer_decision,  # type: ignore[arg-type]
            reviewer_note=reviewer_note,
            created_at=utcnow(),
            idempotency_key=f"task:{run.id}",
        )
        with self._conn() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO internal_tasks (
                        id, originating_run_id, org_slug, title, body, status, risk,
                        citation_ids, reviewer_decision, reviewer_note, created_at, idempotency_key
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
                    """,
                    (
                        task.id,
                        task.originating_run_id,
                        task.org_slug,
                        task.title,
                        task.body,
                        task.status,
                        task.risk,
                        json.dumps(task.citation_ids),
                        task.reviewer_decision,
                        task.reviewer_note,
                        task.created_at,
                        task.idempotency_key,
                    ),
                )
            except Exception as exc:
                if "unique" in str(exc).lower() or getattr(exc, "sqlstate", "") == "23505":
                    found = self.get_internal_task(run.id)
                    if found:
                        return found
                raise
        self.append_audit(run.id, "internal_task", "open", {"task_id": task.id})
        return task

    def get_internal_task(self, run_id: str, org_slug: str | None = None) -> InternalTask | None:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT id, originating_run_id, org_slug, title, body, status, risk,
                       citation_ids, reviewer_decision, reviewer_note, created_at, idempotency_key
                FROM internal_tasks WHERE originating_run_id = %s
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        task = InternalTask(
            id=row[0],
            originating_run_id=row[1],
            org_slug=row[2],
            title=row[3],
            body=row[4],
            status=row[5],
            risk=row[6],
            citation_ids=list(row[7] or []),
            reviewer_decision=row[8],
            reviewer_note=row[9],
            created_at=row[10],
            idempotency_key=row[11],
        )
        if org_slug and task.org_slug != org_slug:
            return None
        return task

    def append_audit(
        self,
        run_id: str,
        kind: str,
        detail: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        import json

        from agentic_ops.db import next_audit_seq

        at = utcnow()
        with self._conn() as conn:
            seq = next_audit_seq(conn, run_id)
            conn.execute(
                """
                INSERT INTO audit_events (run_id, seq, at, kind, detail, data)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                """,
                (run_id, seq, at, kind, detail, json.dumps(data or {})),
            )
        return AuditEvent(run_id=run_id, seq=seq, at=at, kind=kind, detail=detail, data=data or {})

    def list_audit(self, run_id: str) -> list[AuditEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT run_id, seq, at, kind, detail, data
                FROM audit_events WHERE run_id = %s ORDER BY seq
                """,
                (run_id,),
            ).fetchall()
        return [
            AuditEvent(
                run_id=row[0],
                seq=row[1],
                at=row[2],
                kind=row[3],
                detail=row[4],
                data=dict(row[5] or {}),
            )
            for row in rows
        ]

    def hydrate(self, record: RunRecord) -> RunRecord:
        task = self.get_internal_task(record.id)
        return record.model_copy(
            update={
                "internal_task": task,
                "internal_task_id": task.id if task else record.internal_task_id,
                "audit_events": self.list_audit(record.id),
            }
        )


_store: MemoryRunStore | PostgresRunStore | None = None


def _make_store() -> MemoryRunStore | PostgresRunStore:
    if settings.use_postgres:
        return PostgresRunStore()
    return MemoryRunStore()


def get_store() -> MemoryRunStore | PostgresRunStore:
    global _store
    if _store is None:
        _store = _make_store()
    return _store


def reset_store() -> None:
    global _store
    if _store is not None:
        _store.close()
    _store = None


class _StoreProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_store(), name)


store = _StoreProxy()
