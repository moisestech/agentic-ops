from __future__ import annotations

import re

from agentic_ops.models import Citation, ProposedAction
from agentic_ops.retrieval.corpus import Passage

_ACTION_HINTS = (
    "outreach",
    "follow up",
    "follow-up",
    "invite",
    "email",
    "partner",
    "approval",
    "draft",
)


class FakeProvider:
    """Deterministic provider for CI and local demos. No network, no credentials."""

    name = "fake"

    def draft(
        self,
        question: str,
        passages: list[tuple[Passage, float]],
        *,
        require_action: bool = False,
        org_slug: str = "dcc",
        tool_calls: list | None = None,
    ) -> tuple[str, list[Citation], ProposedAction | None, dict[str, int]]:
        if not passages:
            answer = (
                "I do not have approved records for that question. "
                "No operational action is proposed."
            )
            return answer, [], None, {"prompt_tokens": 0, "completion_tokens": 24}

        citations = [
            Citation(
                passage_id=passage.id,
                source_id=passage.source_id,
                title=passage.title,
                quote=_quote(passage.text),
                score=round(score, 4),
            )
            for passage, score in passages[:3]
        ]
        sentences = _grounded_sentences(question, [passage for passage, _ in passages])
        excerpt = re.sub(r"\s+", " ", passages[0][0].text).strip()[:320]
        answer = " ".join([*sentences, excerpt]).strip()
        if not answer.endswith("."):
            answer += "."
        answer += " Citations: " + ", ".join(item.passage_id for item in citations) + "."

        action = None
        lowered = question.lower()
        if require_action or any(hint in lowered for hint in _ACTION_HINTS):
            action = _action_for(org_slug, question)
        if tool_calls:
            names = [str(item.get("name")) for item in tool_calls if item.get("name")]
            if names:
                answer += " Tools used: " + ", ".join(names) + "."
        usage = {
            "prompt_tokens": 80 + 20 * len(passages),
            "completion_tokens": 40 + 8 * len(citations),
        }
        return answer, citations, action, usage


def _sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _grounded_sentences(question: str, passages: list[Passage], *, limit: int = 3) -> list[str]:
    from agentic_ops.retrieval.keyword import tokenize

    query = set(tokenize(question))
    scored: list[tuple[int, str]] = []
    for passage in passages:
        for sentence in _sentences(passage.text):
            overlap = len(query.intersection(tokenize(sentence)))
            if overlap:
                scored.append((overlap, sentence[:280]))
    scored.sort(key=lambda item: item[0], reverse=True)
    unique: list[str] = []
    seen: set[str] = set()
    for _, sentence in scored:
        if sentence in seen:
            continue
        seen.add(sentence)
        unique.append(sentence)
        if len(unique) >= limit:
            break
    if unique:
        return unique
    return [_sentences(passages[0].text)[0][:280]] if passages else []


def _action_for(org_slug: str, question: str) -> ProposedAction:
    if org_slug == "creative-program" or "program" in question.lower():
        return ProposedAction(
            action_type="file_program_plan",
            title="File six-week program plan (internal record)",
            draft=(
                "File the six-week creative technology program plan for staff: "
                "Saturday 10:00–13:00 window, week-3 instructor A blocked, "
                "budget at or under the $4,800 cap, no second venue without a new hire. "
                "This stays an internal task until a reviewer approves it. Nothing is emailed."
            ),
            risk="medium",
            destination="internal_record",
        )
    if org_slug == "enterprise-intake" or "intake" in question.lower():
        return ProposedAction(
            action_type="route_intake_ticket",
            title="Route intake ticket to human review",
            draft=(
                "Cited policy and ticket fields. Edge cases stay with a reviewer. "
                "This draft stays internal until a human approves it."
            ),
            risk="medium",
            destination="internal_record",
        )
    return ProposedAction(
        action_type="draft_partner_followup",
        title="Draft partner follow-up (not sent)",
        draft=(
            "Sharing a cited summary of DCC network onboarding. "
            "This draft stays internal until a human approves it."
        ),
        risk="medium",
        destination="internal_record",
    )


def _quote(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:180]
