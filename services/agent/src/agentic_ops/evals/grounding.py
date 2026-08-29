from __future__ import annotations

from agentic_ops.models import Citation, Evaluation, ProposedAction

INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "exfiltrate",
)

CONSEQUENTIAL_ACTIONS = {
    "draft_partner_followup",
    "invite_to_workshop",
    "create_followup_task",
    "file_program_plan",
    "route_intake_ticket",
}


def evaluate_draft(
    *,
    answer: str,
    citations: list[Citation],
    proposed_action: ProposedAction | None,
    question: str,
) -> Evaluation:
    reasons: list[str] = []
    unsupported: list[str] = []
    lowered = f"{question}\n{answer}".lower()

    honest_abstention = (
        "i do not have approved records" in answer.lower() and not citations
    )
    grounded = bool(citations) or honest_abstention
    if not citations and not honest_abstention:
        grounded = False
        unsupported.append("answer_without_citations")
        reasons.append("Answer lacked citations from the approved corpus.")

    cited_ids = {item.passage_id for item in citations}
    for token in _claimed_ids(answer):
        if token not in cited_ids:
            grounded = False
            unsupported.append(token)
            reasons.append(f"Citation {token} is not in the retrieved allowlist.")

    policy_ok = True
    if any(marker in lowered for marker in INJECTION_MARKERS):
        policy_ok = False
        reasons.append("Prompt-injection marker detected; refusing consequential action.")

    requires_approval = False
    if proposed_action and proposed_action.action_type in CONSEQUENTIAL_ACTIONS:
        requires_approval = True
        reasons.append("Consequential action requires a human approval interrupt.")
    if (not grounded or not policy_ok) and not honest_abstention:
        requires_approval = True
        if proposed_action:
            reasons.append("Ungrounded or policy-failing drafts cannot execute.")

    return Evaluation(
        grounded=grounded,
        policy_ok=policy_ok,
        requires_approval=requires_approval,
        reasons=reasons,
        unsupported_claims=unsupported,
    )


def _claimed_ids(answer: str) -> list[str]:
    import re

    return re.findall(r"\b[a-z0-9-]+:\d+\b", answer.lower())
