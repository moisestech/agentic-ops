from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from agentic_ops.graph.runtime import run_to_interrupt_or_end
from agentic_ops.store import store


def default_golden_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "packages" / "evals" / "golden-set.json"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "packages" / "evals" / "golden-set.json"


def run_harness(golden_path: Path | None = None) -> dict:
    payload = json.loads((golden_path or default_golden_path()).read_text(encoding="utf-8"))
    cases = payload["cases"]
    results = []
    passed = 0
    for case in cases:
        record = store.create(case["question"], case.get("org_slug", "dcc"))
        record = run_to_interrupt_or_end(
            record,
            require_action=case.get("require_action", False),
        )
        answer = (record.answer or "").lower()
        failures: list[str] = []
        for needle in case.get("answer_must_match", []):
            if needle.lower() not in answer:
                failures.append(f"missing:{needle}")
        for needle in case.get("must_not_include", []):
            if needle.lower() in answer:
                failures.append(f"forbidden:{needle}")
        if case.get("expect_no_records") and "i do not have approved records" not in answer:
            failures.append("expected_no_records")
        if case.get("expect_approval") and record.status != "needs_approval":
            failures.append(f"expected_approval_got_{record.status}")
        if case.get("expect_citations", True) and not case.get("expect_no_records"):
            if not record.citations:
                failures.append("missing_citations")
        ok = not failures
        passed += int(ok)
        results.append(
            {
                "id": case["id"],
                "ok": ok,
                "status": record.status,
                "failures": failures,
                "citation_ids": [item.passage_id for item in record.citations],
            }
        )
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "provider": "fake",
        "total": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "pass_rate": round(passed / len(cases), 4) if cases else 0,
        "results": results,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="fake")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    report = run_harness()
    text = json.dumps(report, indent=2)
    out = Path(args.out) if args.out else default_golden_path().parent / "reports" / (
        datetime.now(UTC).strftime("%Y-%m-%d") + f"-{args.provider}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
