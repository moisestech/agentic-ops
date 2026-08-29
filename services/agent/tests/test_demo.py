from fastapi.testclient import TestClient

from agentic_ops.demo import load_demo_run
from agentic_ops.main import app

client = TestClient(app)


def test_demo_fixture_is_a_complete_executed_run() -> None:
    record = load_demo_run()
    assert record.id.startswith("demo-")
    assert record.status == "executed"
    assert record.approval and record.approval.decision == "approved"
    assert len(record.tool_calls) >= 3
    assert record.citations


def test_demo_replay_endpoint_needs_no_provider_key() -> None:
    response = client.post("/v1/demo/replay")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    fetched = client.get(f"/v1/runs/{body['id']}")
    assert fetched.status_code == 200
