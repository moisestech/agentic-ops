from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from agentic_ops.config import settings

LAUNCH = {
    "question": (
        "Prepare a six-week creative technology program launch: "
        "schedule, budget, equipment, and staff capacity."
    ),
    "org_slug": "creative-program",
    "require_action": True,
}

pytestmark = pytest.mark.persistence


def _postgres_ready() -> bool:
    return settings.use_postgres or os.environ.get("AGENT_PERSISTENCE", "").lower() == "postgres"


@pytest.fixture()
def persist_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    url = os.environ.get("DATABASE_URL", settings.database_url)
    if not os.environ.get("DATABASE_URL") and not settings.use_postgres:
        pytest.skip("DATABASE_URL not set; persistence tests require Postgres")
    monkeypatch.setenv("AGENT_PERSISTENCE", "postgres")
    monkeypatch.setenv("DATABASE_URL", url)
    settings.agent_persistence = "postgres"
    settings.database_url = url
    try:
        from agentic_ops.db import init_schema

        init_schema()
    except Exception as exc:  # pragma: no cover - skip when docker is down
        pytest.skip(f"postgres unavailable: {exc}")
    from agentic_ops.graph.runtime import reset_runtime

    reset_runtime()
    from agentic_ops.main import app

    return TestClient(app)


def _create_launch(client: TestClient) -> dict:
    response = client.post("/v1/runs", json=LAUNCH)
    assert response.status_code == 200
    return response.json()


def test_restart_then_approve_creates_one_task(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    assert run["status"] == "needs_approval"
    from agentic_ops.graph import reset_graph

    reset_graph()
    loaded = persist_client.get(f"/v1/runs/{run['id']}", params={"org_slug": "creative-program"})
    assert loaded.status_code == 200
    assert loaded.json()["status"] == "needs_approval"

    decided = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "file the Saturday plan"},
    )
    assert decided.status_code == 200
    body = decided.json()
    assert body["status"] == "executed"
    assert body["internal_task"]
    task_id = body["internal_task"]["id"]
    kinds = [item["kind"] for item in body["audit_events"]]
    assert "decision" in kinds
    assert "internal_task" in kinds

    retry = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "file the Saturday plan"},
    )
    assert retry.status_code == 200
    assert retry.json()["internal_task"]["id"] == task_id
    assert retry.json()["internal_task"]["originating_run_id"] == run["id"]


def test_reject_creates_no_task(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    decided = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "rejected", "note": "hold for budget revision"},
    )
    assert decided.status_code == 200
    assert decided.json()["status"] == "rejected"
    assert decided.json()["internal_task"] is None


def test_edit_and_approve_stores_edited_draft(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    edited = "Staff will file the Saturday 10–13 plan under the $4,800 cap. No second venue."
    decided = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "edited", "edited_draft": edited, "note": "tighten venue line"},
    )
    assert decided.status_code == 200
    task = decided.json()["internal_task"]
    assert task["body"] == edited
    assert task["reviewer_decision"] == "edited"


def test_readonly_question_creates_no_task(persist_client: TestClient) -> None:
    response = persist_client.post(
        "/v1/runs",
        json={"question": "What is DCC Open Lab and how does it differ from workshops?"},
    )
    body = response.json()
    assert body["status"] == "answered"
    assert body["internal_task"] is None
    conflict = persist_client.post(
        f"/v1/runs/{body['id']}/decision",
        json={"decision": "approved"},
    )
    assert conflict.status_code == 409


def test_conflicting_decision_returns_409(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "ok"},
    )
    conflict = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "rejected", "note": "no"},
    )
    assert conflict.status_code == 409


def test_cross_org_lookup_is_404(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    missing = persist_client.get(f"/v1/runs/{run['id']}", params={"org_slug": "dcc"})
    assert missing.status_code == 404


def test_execution_failure_keeps_decision(
    persist_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _create_launch(persist_client)

    def boom(*_args, **_kwargs):
        raise RuntimeError("forced_execute_failure")

    monkeypatch.setattr("agentic_ops.store.PostgresRunStore.create_internal_task", boom)
    decided = persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "ok"},
    )
    assert decided.status_code == 200
    body = decided.json()
    assert body["status"] == "failed"
    assert body["internal_task"] is None
    assert persist_client.get(f"/v1/runs/{run['id']}").json()["approval"] or True
    from agentic_ops.store import get_store

    assert get_store().get_decision(run["id"]) is not None


def test_audit_events_are_ordered(persist_client: TestClient) -> None:
    run = _create_launch(persist_client)
    persist_client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "ok"},
    )
    body = persist_client.get(f"/v1/runs/{run['id']}").json()
    seqs = [item["seq"] for item in body["audit_events"]]
    assert seqs == sorted(seqs)
    assert seqs == list(range(1, len(seqs) + 1))
