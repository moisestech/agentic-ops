from __future__ import annotations

from typing import Protocol

from agentic_ops.models import Citation, ProposedAction
from agentic_ops.retrieval.corpus import Passage


class ProviderDraft(Protocol):
    def draft(
        self,
        question: str,
        passages: list[tuple[Passage, float]],
        *,
        require_action: bool = False,
        org_slug: str = "dcc",
        tool_calls: list | None = None,
    ) -> tuple[str, list[Citation], ProposedAction | None, dict[str, int]]: ...
