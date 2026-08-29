from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RunStatus = Literal[
    "queued",
    "retrieving",
    "drafting",
    "evaluating",
    "needs_approval",
    "executing",
    "answered",
    "executed",
    "rejected",
    "failed",
]

ActionType = Literal[
    "none",
    "draft_partner_followup",
    "invite_to_workshop",
    "create_followup_task",
    "ask_for_missing_info",
    "file_program_plan",
    "route_intake_ticket",
]


class ToolCall(BaseModel):
    name: str
    permission: Literal["READ", "WRITE"]
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    passage_id: str
    source_id: str
    title: str
    quote: str
    score: float


class ProposedAction(BaseModel):
    action_type: ActionType
    title: str
    draft: str
    risk: Literal["low", "medium", "high"]
    destination: str = "internal_record"


class Evaluation(BaseModel):
    grounded: bool
    policy_ok: bool
    requires_approval: bool
    reasons: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)


class Approval(BaseModel):
    decision: Literal["approved", "rejected", "edited"]
    note: str | None = None
    edited_draft: str | None = None
    decided_at: datetime | None = None


class TraceEvent(BaseModel):
    at: datetime
    node: str
    detail: str
    data: dict[str, Any] = Field(default_factory=dict)


class RunRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    org_slug: str = "dcc"
    require_action: bool = False


class DecisionRequest(BaseModel):
    decision: Literal["approved", "rejected", "edited"]
    note: str | None = None
    edited_draft: str | None = None


class RunRecord(BaseModel):
    id: str
    status: RunStatus
    question: str
    org_slug: str
    answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    proposed_action: ProposedAction | None = None
    evaluation: Evaluation | None = None
    approval: Approval | None = None
    outcome: str | None = None
    trace: list[TraceEvent] = Field(default_factory=list)
    latency_ms: int | None = None
    token_usage: dict[str, int] = Field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    tool_calls: list[ToolCall] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
