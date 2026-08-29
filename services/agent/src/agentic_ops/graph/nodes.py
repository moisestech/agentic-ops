from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from agentic_ops.evals.grounding import evaluate_draft
from agentic_ops.graph.state import AgentState
from agentic_ops.providers import get_provider
from agentic_ops.retrieval.keyword import retriever_for
from agentic_ops.tools import call_tool, should_use_extra_tools


def _event(node: str, detail: str, **data: Any) -> dict[str, Any]:
    return {"at": datetime.now(UTC).isoformat(), "node": node, "detail": detail, "data": data}


def retrieve_node(state: AgentState) -> dict[str, Any]:
    org = state.get("org_slug") or "dcc"
    hits = retriever_for(org).search(state["question"], k=4)
    passages = [
        {
            "id": passage.id,
            "source_id": passage.source_id,
            "title": passage.title,
            "text": passage.text,
            "path": passage.path,
            "score": score,
        }
        for passage, score in hits
    ]
    return {
        "passages": passages,
        "trace": list(state.get("trace") or [])
        + [_event("retrieve", f"{len(passages)} passages", count=len(passages))],
    }


def tools_node(state: AgentState) -> dict[str, Any]:
    org = state.get("org_slug") or "dcc"
    question = state["question"]
    calls: list[dict[str, Any]] = [
        {
            "name": "search_documents",
            "permission": "READ",
            "arguments": {"query": question, "org_slug": org},
            "result": {"count": len(state.get("passages") or [])},
        }
    ]
    if should_use_extra_tools(question, org):
        for name in ("check_calendar", "calculate_budget"):
            result = call_tool(name, {"org_slug": org})
            calls.append(
                {
                    "name": name,
                    "permission": "READ",
                    "arguments": {"org_slug": org},
                    "result": result,
                }
            )
        write = call_tool(
            "manage_actions",
            {
                "org_slug": org,
                "action": "create",
                "tasks": ["file implementation tasks from the cited plan"],
            },
        )
        calls.append(
            {
                "name": "manage_actions",
                "permission": "WRITE",
                "arguments": {"org_slug": org, "action": "create"},
                "result": write,
            }
        )
    names = ", ".join(item["name"] for item in calls)
    return {
        "tool_calls": calls,
        "trace": list(state.get("trace") or []) + [_event("tools", names, count=len(calls))],
    }


def draft_node(state: AgentState) -> dict[str, Any]:
    from agentic_ops.retrieval.corpus import Passage

    provider = get_provider()
    packed = [
        (
            Passage(
                id=item["id"],
                source_id=item["source_id"],
                title=item["title"],
                text=item["text"],
                path=item.get("path") or f"data/dcc-public/{item['source_id']}.md",
            ),
            float(item["score"]),
        )
        for item in state.get("passages") or []
    ]
    answer, citations, action, usage = provider.draft(
        state["question"],
        packed,
        require_action=bool(state.get("require_action")),
        org_slug=state.get("org_slug") or "dcc",
        tool_calls=state.get("tool_calls") or [],
    )
    return {
        "answer": answer,
        "citations": [item.model_dump() for item in citations],
        "proposed_action": action.model_dump() if action else None,
        "token_usage": usage,
        "trace": list(state.get("trace") or [])
        + [_event("draft", provider.name, citations=len(citations))],
    }


def evaluate_node(state: AgentState) -> dict[str, Any]:
    from agentic_ops.models import Citation, ProposedAction

    citations = [
        item if isinstance(item, Citation) else Citation.model_validate(item)
        for item in state.get("citations") or []
    ]
    raw_action = state.get("proposed_action")
    action = None
    if raw_action:
        action = (
            raw_action
            if isinstance(raw_action, ProposedAction)
            else ProposedAction.model_validate(raw_action)
        )
    evaluation = evaluate_draft(
        answer=state.get("answer") or "",
        citations=citations,
        proposed_action=action,
        question=state["question"],
    )
    return {
        "evaluation": evaluation.model_dump(),
        "trace": list(state.get("trace") or [])
        + [
            _event(
                "evaluate",
                "grounding+policy",
                grounded=evaluation.grounded,
                requires_approval=evaluation.requires_approval,
            )
        ],
    }


def route_after_eval(state: AgentState) -> Literal["await_approval", "respond"]:
    evaluation = state.get("evaluation")
    requires = False
    if isinstance(evaluation, dict):
        requires = bool(evaluation.get("requires_approval"))
    elif evaluation is not None:
        requires = bool(evaluation.requires_approval)
    return "await_approval" if requires else "respond"


def await_approval_node(state: AgentState) -> dict[str, Any]:
    from langgraph.types import interrupt

    def dump(value: Any) -> Any:
        return value.model_dump() if hasattr(value, "model_dump") else value

    decision = interrupt(
        {
            "type": "approval_required",
            "answer": state.get("answer"),
            "proposed_action": dump(state.get("proposed_action")),
            "evaluation": dump(state.get("evaluation")),
            "citations": [dump(item) for item in state.get("citations") or []],
        }
    )
    return {
        "approval": decision,
        "trace": list(state.get("trace") or []) + [_event("await_approval", "interrupt resumed")],
    }


def respond_node(state: AgentState) -> dict[str, Any]:
    return {
        "outcome": "answered",
        "trace": list(state.get("trace") or []) + [_event("respond", "no consequential action")],
    }


def execute_node(state: AgentState) -> dict[str, Any]:
    approval = state.get("approval") or {}
    if isinstance(approval, dict):
        decision = approval.get("decision")
    else:
        decision = getattr(approval, "decision", None)
    if decision != "approved":
        return {
            "outcome": "rejected",
            "trace": list(state.get("trace") or [])
            + [_event("execute", "rejected or missing approval")],
        }
    return {
        "outcome": "executed",
        "trace": list(state.get("trace") or [])
        + [_event("execute", "wrote internal audit record only")],
    }
