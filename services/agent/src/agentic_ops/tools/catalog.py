from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from agentic_ops.retrieval.keyword import retriever_for

Permission = Literal["READ", "WRITE"]

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_documents",
        "description": "Retrieve approved organizational records with source ids.",
        "permission": "READ",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "org_slug": {"type": "string"},
                "top_k": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_calendar",
        "description": "Read staff capacity and scheduling constraints for a scenario.",
        "permission": "READ",
        "inputSchema": {
            "type": "object",
            "properties": {"org_slug": {"type": "string"}, "weeks": {"type": "integer"}},
        },
    },
    {
        "name": "calculate_budget",
        "description": "Sum line items and compare them to the approved budget cap.",
        "permission": "READ",
        "inputSchema": {
            "type": "object",
            "properties": {"org_slug": {"type": "string"}, "max_budget": {"type": "number"}},
        },
    },
    {
        "name": "manage_actions",
        "description": "Propose implementation tasks. Writes stay pending until a human approves.",
        "permission": "WRITE",
        "inputSchema": {
            "type": "object",
            "properties": {
                "org_slug": {"type": "string"},
                "action": {"type": "string"},
                "tasks": {"type": "array", "items": {"type": "string"}},
                "approved": {"type": "boolean"},
            },
        },
    },
]

_EXTRA_HINTS = (
    "program",
    "launch",
    "budget",
    "calendar",
    "schedule",
    "six-week",
    "six week",
    "intake",
    "ticket",
    "capacity",
    "equipment",
)


def list_tools() -> list[dict[str, Any]]:
    return TOOLS


def should_use_extra_tools(question: str, org_slug: str) -> bool:
    if org_slug in {"creative-program", "enterprise-intake"}:
        return True
    lowered = question.lower()
    return any(hint in lowered for hint in _EXTRA_HINTS)


def _scenarios_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "scenarios"
        if candidate.is_dir():
            return candidate
    return Path.cwd() / "scenarios"


def _load_fixture(org_slug: str, name: str) -> dict[str, Any]:
    path = _scenarios_root() / org_slug / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def search_documents(
    query: str, *, org_slug: str = "dcc", top_k: int = 4
) -> dict[str, Any]:
    hits = retriever_for(org_slug).search(query, k=top_k)
    passages = [
        {
            "id": passage.id,
            "source_id": passage.source_id,
            "title": passage.title,
            "text": passage.text,
            "score": round(score, 4),
            "path": passage.path,
        }
        for passage, score in hits
    ]
    return {"passages": passages, "count": len(passages)}


def check_calendar(*, org_slug: str = "dcc", weeks: int = 6) -> dict[str, Any]:
    payload = _load_fixture(org_slug, "calendar.json")
    if not payload:
        return {
            "available": True,
            "weeks": weeks,
            "note": "No calendar fixture for this org; treat as unconstrained.",
        }
    payload.setdefault("weeks", weeks)
    return payload


def calculate_budget(*, org_slug: str = "dcc", max_budget: float | None = None) -> dict[str, Any]:
    payload = _load_fixture(org_slug, "budget.json")
    items = payload.get("line_items") or []
    total = sum(float(item.get("amount", 0)) for item in items)
    cap = float(max_budget if max_budget is not None else payload.get("cap", total))
    return {
        "line_items": items,
        "total": total,
        "cap": cap,
        "within_cap": total <= cap,
        "currency": payload.get("currency", "USD"),
    }


def manage_actions(
    *,
    org_slug: str = "dcc",
    action: str = "create",
    tasks: list[str] | None = None,
    approved: bool = False,
) -> dict[str, Any]:
    proposed = tasks or ["file internal implementation tasks"]
    if not approved:
        return {
            "status": "pending_approval",
            "permission": "WRITE",
            "action": action,
            "org_slug": org_slug,
            "tasks": proposed,
            "note": "WRITE tools do not execute until a human approval is recorded.",
        }
    return {
        "status": "recorded",
        "permission": "WRITE",
        "action": action,
        "org_slug": org_slug,
        "tasks": proposed,
        "destination": "internal_record",
    }


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments or {}
    if name == "search_documents":
        return search_documents(
            str(args.get("query", "")),
            org_slug=str(args.get("org_slug", "dcc")),
            top_k=int(args.get("top_k", 4)),
        )
    if name == "check_calendar":
        return check_calendar(
            org_slug=str(args.get("org_slug", "dcc")),
            weeks=int(args.get("weeks", 6)),
        )
    if name == "calculate_budget":
        cap = args.get("max_budget")
        return calculate_budget(
            org_slug=str(args.get("org_slug", "dcc")),
            max_budget=float(cap) if cap is not None else None,
        )
    if name == "manage_actions":
        return manage_actions(
            org_slug=str(args.get("org_slug", "dcc")),
            action=str(args.get("action", "create")),
            tasks=list(args.get("tasks") or []),
            approved=bool(args.get("approved", False)),
        )
    raise KeyError(f"unknown_tool:{name}")
