from __future__ import annotations

import json
from pathlib import Path

from agentic_ops.models import RunRecord


def default_demo_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "fixtures" / "demo-run.json"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "fixtures" / "demo-run.json"


def load_demo_run(path: Path | None = None) -> RunRecord:
    payload = json.loads((path or default_demo_path()).read_text(encoding="utf-8"))
    return RunRecord.model_validate(payload)
