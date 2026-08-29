from fastapi.testclient import TestClient

from agentic_ops.main import app

client = TestClient(app)


def test_question_without_action_can_answer() -> None:
    response = client.post(
        "/v1/runs",
        json={"question": "What is DCC Open Lab and how does it differ from workshops?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"answered", "needs_approval"}
    assert body["citations"]
    assert "open lab" in body["answer"].lower()


def test_interrupt_then_approve_executes_internal_record_only() -> None:
    created = client.post(
        "/v1/runs",
        json={
            "question": "Draft a partner follow-up after DCC network signup.",
            "require_action": True,
        },
    )
    assert created.status_code == 200
    run = created.json()
    assert run["status"] == "needs_approval"
    assert run["proposed_action"]["destination"] == "internal_record"

    decided = client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "approved", "note": "ok to file internally"},
    )
    assert decided.status_code == 200
    body = decided.json()
    assert body["status"] == "executed"
    assert body["outcome"] == "executed"
    assert body["approval"]["decision"] == "approved"


def test_reject_does_not_execute() -> None:
    created = client.post(
        "/v1/runs",
        json={
            "question": "Invite this partner to a workshop by email.",
            "require_action": True,
        },
    )
    run = created.json()
    decided = client.post(
        f"/v1/runs/{run['id']}/decision",
        json={"decision": "rejected", "note": "hold"},
    )
    assert decided.json()["status"] == "rejected"


def test_unknown_question_does_not_fabricate() -> None:
    response = client.post(
        "/v1/runs",
        json={"question": "Who won the Nobel Prize in Physics at DCC last Tuesday?"},
    )
    body = response.json()
    assert "i do not have approved records" in body["answer"].lower()
    assert "nobel" not in body["answer"].lower()
    assert body["status"] == "answered"
