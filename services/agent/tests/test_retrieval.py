from agentic_ops.retrieval import retriever


def test_keyword_retrieval_finds_governance_passage() -> None:
    hits = retriever.search("How does DCC handle privacy and AI use?", k=4)
    assert hits
    joined = " ".join(passage.text.lower() for passage, _ in hits)
    assert "approved" in joined or "do not use" in joined


def test_keyword_retrieval_finds_open_lab() -> None:
    hits = retriever.search("What is DCC Open Lab and how does it differ from workshops?", k=4)
    assert any("open lab" in passage.text.lower() for passage, _ in hits)
