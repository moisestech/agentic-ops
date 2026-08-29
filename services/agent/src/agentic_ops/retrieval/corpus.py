from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class Passage:
    id: str
    source_id: str
    title: str
    text: str
    path: str


ORG_CORPORA: dict[str, str] = {
    "dcc": "dcc-public",
    "creative-program": "creative-program",
    "enterprise-intake": "enterprise-intake",
}


def default_data_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "data" / "dcc-public"
        if candidate.is_dir():
            return parent / "data"
    return Path.cwd() / "data"


def default_corpus_dir() -> Path:
    return default_data_root() / "dcc-public"


def corpus_dir_for(org_slug: str) -> Path:
    folder = ORG_CORPORA.get(org_slug, org_slug)
    path = default_data_root() / folder
    return path if path.is_dir() else default_corpus_dir()


def load_markdown_documents(corpus_dir: Path | None = None) -> list[tuple[str, str, str]]:
    """Return (source_id, title, text) for each public markdown file."""
    root = corpus_dir or default_corpus_dir()
    documents: list[tuple[str, str, str]] = []
    for path in sorted(root.glob("*.md")):
        if path.name.startswith("00-"):
            continue
        text = path.read_text(encoding="utf-8").strip()
        title = path.stem.replace("-", " ").title()
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        documents.append((path.stem, title, text))
    return documents


def chunk_documents(
    documents: list[tuple[str, str, str]] | None = None,
    *,
    corpus_dir: Path | None = None,
    chunk_size: int = 700,
    chunk_overlap: int = 80,
) -> list[Passage]:
    root = corpus_dir or default_corpus_dir()
    docs = documents if documents is not None else load_markdown_documents(root)
    rel = root.name
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    passages: list[Passage] = []
    for source_id, title, text in docs:
        chunks = splitter.split_text(text)
        for index, chunk in enumerate(chunks, start=1):
            passages.append(
                Passage(
                    id=f"{source_id}:{index}",
                    source_id=source_id,
                    title=title,
                    text=chunk.strip(),
                    path=f"data/{rel}/{source_id}.md",
                )
            )
    return passages
