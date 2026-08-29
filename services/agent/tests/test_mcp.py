from agentic_ops.mcp import handle


def test_stdio_lists_and_calls_tools() -> None:
    listed = handle({"method": "tools/list"})
    assert {item["name"] for item in listed["tools"]} == {
        "search_documents",
        "check_calendar",
        "calculate_budget",
        "manage_actions",
    }
    called = handle(
        {
            "method": "tools/call",
            "params": {
                "name": "search_documents",
                "arguments": {"query": "intake ticket policy", "org_slug": "enterprise-intake"},
            },
        }
    )
    assert called["result"]["count"] >= 1
