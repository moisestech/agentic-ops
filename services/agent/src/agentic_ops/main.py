from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agentic_ops import __version__
from agentic_ops.config import settings
from agentic_ops.demo import load_demo_run
from agentic_ops.graph.runtime import resume_with_decision, run_to_interrupt_or_end
from agentic_ops.models import DecisionRequest, RunRecord, RunRequest
from agentic_ops.store import store
from agentic_ops.tools import call_tool, list_tools

app = FastAPI(
    title="Agentic Ops",
    version=__version__,
    summary="Governed agent: retrieve, cite, pause for approval, record the outcome.",
    description=(
        "Public reference implementation. Consequential actions never execute without "
        "an explicit human decision. Fixtures are public/synthetic only."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {
        "status": "ready",
        "provider": settings.agent_provider,
        "demo_mode": str(settings.demo_mode),
    }


@app.get("/v1/tools")
def tools() -> dict[str, Any]:
    return {"tools": list_tools()}


@app.post("/v1/tools/{name}")
def invoke_tool(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return {"name": name, "result": call_tool(name, payload or {})}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/demo/replay", response_model=RunRecord)
def replay_demo() -> RunRecord:
    record = load_demo_run()
    return store.insert(record)


@app.post("/v1/runs", response_model=RunRecord)
def create_run(payload: RunRequest) -> RunRecord:
    record = store.create(payload.question, payload.org_slug)
    return run_to_interrupt_or_end(record, require_action=payload.require_action)


@app.get("/v1/runs", response_model=list[RunRecord])
def list_runs() -> list[RunRecord]:
    return store.list()


@app.get("/v1/runs/{run_id}", response_model=RunRecord)
def get_run(run_id: str) -> RunRecord:
    record = store.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    return record


@app.post("/v1/runs/{run_id}/decision", response_model=RunRecord)
def decide(run_id: str, payload: DecisionRequest) -> RunRecord:
    record = store.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    if record.status != "needs_approval":
        raise HTTPException(status_code=409, detail="run_not_awaiting_approval")
    return resume_with_decision(record, payload)


def run() -> None:
    import uvicorn

    uvicorn.run(
        "agentic_ops.main:app",
        host=settings.agent_host,
        port=settings.agent_port,
        reload=False,
    )
