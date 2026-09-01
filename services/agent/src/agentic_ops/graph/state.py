from __future__ import annotations

from typing import Any, Literal, TypedDict

from agentic_ops.models import Approval, Citation, Evaluation, ProposedAction


class AgentState(TypedDict, total=False):
    run_id: str
    question: str
    org_slug: str
    require_action: bool
    passages: list[dict[str, Any]]
    answer: str
    citations: list[Citation]
    proposed_action: ProposedAction | None
    evaluation: Evaluation | None
    approval: Approval | None
    outcome: Literal["answered", "executed", "rejected", "failed"]
    token_usage: dict[str, int]
    tool_calls: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    internal_task_id: str | None
