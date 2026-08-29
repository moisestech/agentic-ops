from agentic_ops.evals.harness import run_harness


def test_offline_golden_set_passes() -> None:
    report = run_harness()
    assert report["failed"] == 0
    assert report["passed"] == report["total"]
