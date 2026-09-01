# Agent service

FastAPI + LangGraph process that:

1. Retrieves approved public passages.
2. Drafts a cited answer and optional operational action.
3. Runs grounding and policy evaluators.
4. Interrupts for human approval before consequential actions.
5. After approval, persists one internal task. Pause/resume uses the Postgres checkpointer when `AGENT_PERSISTENCE=postgres`.

```bash
# from repo root after `make install`
docker compose up -d postgres
make agent-persist
# http://localhost:8080/health
# http://localhost:8080/docs
# memory-only (unit tests / eval-offline): make agent-dev
```

Offline tests use `AGENT_PROVIDER=fake`. No provider credential is required for CI.
