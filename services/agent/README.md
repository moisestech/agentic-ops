# Agent service

FastAPI + LangGraph process that:

1. Retrieves approved public passages.
2. Drafts a cited answer and optional operational action.
3. Runs grounding and policy evaluators.
4. Interrupts for human approval before consequential actions.
5. Executes only the approved draft and writes an audit record.

```bash
# from repo root after `make install`
make agent-dev
# http://localhost:8080/health
# http://localhost:8080/docs
```

Offline tests use `AGENT_PROVIDER=fake`. No provider credential is required for CI.
