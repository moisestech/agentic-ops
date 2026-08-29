from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

from langgraph.types import Command

from agentic_ops.graph import build_graph
from agentic_ops.models import (
    Approval,
    Citation,
    DecisionRequest,
    Evaluation,
    ProposedAction,
    RunRecord,
    ToolCall,
    TraceEvent,
)
from agentic_ops.store import store

_graph = None


def graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def _config(run_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}


def _as_model(cls, value):
    if value is None:
        return None
    if isinstance(value, cls):
        return value
    if isinstance(value, dict):
        return cls.model_validate(value)
    return value


def _trace(raw: list[dict[str, Any]] | None) -> list[TraceEvent]:
    events: list[TraceEvent] = []
    for item in raw or []:
        payload = dict(item)
        if isinstance(payload.get("at"), str):
            payload["at"] = datetime.fromisoformat(payload["at"])
        events.append(TraceEvent.model_validate(payload))
    return events


def _apply_state(record: RunRecord, values: dict[str, Any], *, interrupted: bool) -> RunRecord:
    outcome = values.get("outcome")
    if interrupted:
        status = "needs_approval"
    elif outcome == "executed":
        status = "executed"
    elif outcome == "rejected":
        status = "rejected"
    elif outcome == "answered":
        status = "answered"
    else:
        status = "failed"

    citations = [_as_model(Citation, item) for item in values.get("citations") or []]
    tool_calls = [_as_model(ToolCall, item) for item in values.get("tool_calls") or []]
    return store.update(
        record.id,
        status=status,
        answer=values.get("answer"),
        citations=citations,
        proposed_action=_as_model(ProposedAction, values.get("proposed_action")),
        evaluation=_as_model(Evaluation, values.get("evaluation")),
        approval=_as_model(Approval, values.get("approval")),
        outcome=outcome,
        trace=_trace(values.get("trace")),
        token_usage=values.get("token_usage") or {},
        estimated_cost_usd=0.0,
        tool_calls=tool_calls,
    )


def run_to_interrupt_or_end(record: RunRecord, *, require_action: bool = False) -> RunRecord:
    started = time.perf_counter()
    store.set_status(record.id, "retrieving")
    try:
        result = graph().invoke(
            {
                "question": record.question,
                "org_slug": record.org_slug,
                "require_action": require_action,
                "trace": [],
            },
            config=_config(record.id),
        )
        snapshot = graph().get_state(_config(record.id))
        interrupted = bool(snapshot.next)
        updated = _apply_state(record, result, interrupted=interrupted)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return store.update(record.id, latency_ms=latency_ms, status=updated.status)
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return store.update(
            record.id,
            status="failed",
            outcome="failed",
            latency_ms=latency_ms,
            answer="The run failed without executing a write. Inspect the trace.",
            trace=_trace(
                [
                    {
                        "at": datetime.now(UTC).isoformat(),
                        "node": "runtime",
                        "detail": "error_contained",
                        "data": {"error": exc.__class__.__name__},
                    }
                ]
            ),
        )


def resume_with_decision(record: RunRecord, decision: DecisionRequest) -> RunRecord:
    approval = Approval(
        decision=decision.decision,
        note=decision.note,
        edited_draft=decision.edited_draft,
        decided_at=datetime.now(UTC),
    )
    started = time.perf_counter()
    try:
        result = graph().invoke(
            Command(resume=approval.model_dump(mode="json")),
            config=_config(record.id),
        )
        snapshot = graph().get_state(_config(record.id))
        interrupted = bool(snapshot.next)
        updated = _apply_state(record, result, interrupted=interrupted)
        prior = record.latency_ms or 0
        return store.update(
            record.id,
            latency_ms=prior + int((time.perf_counter() - started) * 1000),
            approval=approval,
            status=updated.status,
        )
    except Exception as exc:
        return store.update(
            record.id,
            status="failed",
            outcome="failed",
            approval=approval,
            answer="The decision was recorded but execution failed. No write left the system.",
            trace=_trace(
                [
                    {
                        "at": datetime.now(UTC).isoformat(),
                        "node": "runtime",
                        "detail": "resume_error_contained",
                        "data": {"error": exc.__class__.__name__},
                    }
                ]
            ),
        )
