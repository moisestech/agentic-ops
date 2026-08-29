from __future__ import annotations

import re
from collections import Counter

from agentic_ops.retrieval.corpus import Passage, chunk_documents, corpus_dir_for

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in _TOKEN.findall(text.lower())
        if token not in _STOP and len(token) > 1
    ]


def score_passage(query_tokens: list[str], passage: Passage) -> float:
    if not query_tokens:
        return 0.0
    counts = Counter(tokenize(passage.text + " " + passage.title))
    overlap = sum(counts[token] for token in query_tokens)
    unique = sum(1 for token in set(query_tokens) if counts[token] > 0)
    if unique < 2:
        return 0.0
    return unique / len(set(query_tokens)) + 0.05 * overlap


class KeywordRetriever:
    def __init__(self, passages: list[Passage] | None = None) -> None:
        self.passages = passages if passages is not None else chunk_documents()

    def search(self, query: str, *, k: int = 4) -> list[tuple[Passage, float]]:
        tokens = tokenize(query)
        ranked = [(passage, score_passage(tokens, passage)) for passage in self.passages]
        ranked = [item for item in ranked if item[1] > 0]
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:k]


retriever = KeywordRetriever()
_BY_ORG: dict[str, KeywordRetriever] = {"dcc": retriever}


def retriever_for(org_slug: str) -> KeywordRetriever:
    slug = org_slug or "dcc"
    if slug not in _BY_ORG:
        _BY_ORG[slug] = KeywordRetriever(chunk_documents(corpus_dir=corpus_dir_for(slug)))
    return _BY_ORG[slug]
