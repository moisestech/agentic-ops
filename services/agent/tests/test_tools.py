from fastapi.testclient import TestClient

from agentic_ops.main import app
from agentic_ops.tools import call_tool, list_tools

client = TestClient(app)


def test_tool_catalog_lists_four_permissioned_tools() -> None:
    names = {item["name"] for item in list_tools()}
    assert names == {
        "search_documents",
        "check_calendar",
        "calculate_budget",
        "manage_actions",
    }


def test_search_documents_returns_sources() -> None:
    result = call_tool(
        "search_documents",
        {"query": "six-week creative technology program", "org_slug": "creative-program"},
    )
    assert result["count"] >= 1
    assert result["passages"][0]["id"]


def test_write_tool_stays_pending_without_approval() -> None:
    result = call_tool("manage_actions", {"org_slug": "creative-program", "tasks": ["file plan"]})
    assert result["status"] == "pending_approval"


def test_http_tools_surface() -> None:
    listed = client.get("/v1/tools")
    assert listed.status_code == 200
    assert len(listed.json()["tools"]) == 4
    budget = client.post("/v1/tools/calculate_budget", json={"org_slug": "creative-program"})
    assert budget.status_code == 200
    assert budget.json()["result"]["within_cap"] is True


def test_program_launch_uses_multiple_tools_and_pauses() -> None:
    response = client.post(
        "/v1/runs",
        json={
            "question": (
                "Prepare a six-week creative technology program launch: "
                "schedule, budget, equipment, and staff capacity."
            ),
            "org_slug": "creative-program",
            "require_action": True,
        },
    )
    body = response.json()
    assert response.status_code == 200
    names = [item["name"] for item in body["tool_calls"]]
    assert "search_documents" in names
    assert "check_calendar" in names
    assert "calculate_budget" in names
    assert "manage_actions" in names
    assert body["status"] == "needs_approval"
    assert body["citations"]
