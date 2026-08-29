# Course lab — governed agents (90 minutes)

**Audience:** advanced undergrad / early professional applied-AI course.
**Repo:** `moisestech/agentic-ops`
**Live comparison (optional):** Infra24 Memory Agent at `/o/dcc/memory-agent`

## Learning objectives

1. Retrieve with citations instead of unconstrained chat.
2. Separate deterministic gates from model-drafted text.
3. Implement a human interrupt before a consequential tool.
4. Read an audit trail (latency, tokens, decision, outcome).

## Instructor setup

- Docker Desktop, Python 3.11+, Node 20+.
- No provider key required (`AGENT_PROVIDER=fake`).
- Clone, `make install`, `make verify`, `make agent-dev`.

## Student path

1. Ask “What is DCC Open Lab…?” and inspect citations.
2. Ask a Nobel-prize trap question and confirm the fail-closed answer.
3. Ask for a partner follow-up draft; approve and reject in two runs.
4. Break the citation allowlist in a test and watch CI fail.
5. (Stretch) Swap in a live provider behind the same graph contract.

## Screencast beats (P2)

1. Console: cited answer.
2. Console: approval interrupt.
3. Terminal: `make eval-offline` green.
4. Optional: Infra24 live Memory Agent as production comparison — only if the
   dated eval report is already published.
