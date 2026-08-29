"""Stdio MCP-shaped tool server. No extra SDK required."""

from __future__ import annotations

import json
import sys
from typing import Any

from agentic_ops.tools import call_tool, list_tools


def handle(message: dict[str, Any]) -> dict[str, Any]:
    method = message.get("method")
    params = message.get("params") or {}
    if method == "tools/list":
        return {"tools": list_tools()}
    if method == "tools/call":
        name = params.get("name")
        if not name:
            return {"error": "missing_tool_name"}
        try:
            return {"name": name, "result": call_tool(name, params.get("arguments") or {})}
        except KeyError as exc:
            return {"error": str(exc)}
    return {"error": f"unknown_method:{method}"}


def main() -> None:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": f"invalid_json:{exc}"}), flush=True)
            continue
        print(json.dumps(handle(message)), flush=True)


if __name__ == "__main__":
    main()
