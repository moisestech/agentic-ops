from agentic_ops.evals.grounding import evaluate_draft
from agentic_ops.models import Citation, ProposedAction


def test_missing_citation_fails_closed() -> None:
    evaluation = evaluate_draft(
        answer="The lab is open. Citations: missing-doc:1.",
        citations=[],
        proposed_action=None,
        question="What is Open Lab?",
    )
    assert evaluation.grounded is False
    assert "answer_without_citations" in evaluation.unsupported_claims


def test_consequential_action_requires_approval() -> None:
    citation = Citation(
        passage_id="network-readiness:1",
        source_id="network-readiness",
        title="Network",
        quote="Human approval is required.",
        score=1.0,
    )
    action = ProposedAction(
        action_type="draft_partner_followup",
        title="Draft",
        draft="Hello",
        risk="medium",
    )
    evaluation = evaluate_draft(
        answer="Outreach is approval-gated. Citations: network-readiness:1.",
        citations=[citation],
        proposed_action=action,
        question="Draft a partner follow-up",
    )
    assert evaluation.requires_approval is True
    assert evaluation.grounded is True
