# Implementation plan — Agentic Ops

P1 Infra24 work (credential rotation, pgvector migration, DCC embedding sync,
dated eval, lockfile repair) stays in `infra24`. This table is the companion
repo only.

| ID | Status | Task | Verification |
| --- | --- | --- | --- |
| OPS-01 | done | Repo scaffold, FastAPI health, Docker, CI | `make verify` |
| OPS-02 | done | Keyword retrieval + LangChain chunking + public corpus | retrieval tests |
| OPS-03 | done | LangGraph interrupt/resume + citation/policy gate | graph tests |
| OPS-04 | done | Next.js console for ask / approve / audit | `apps/web` |
| OPS-05A | done | Durable runs, Postgres checkpointer, internal task ledger | `make verify-recruiter` |
| OPS-05B | pending | pgvector hybrid retrieval + RRF | integration tests; keyword stays fallback |
| OPS-06 | pending | OpenAI and Claude provider parity tests | live opt-in + fake fixtures |
| OPS-07 | pending | Vercel AI SDK streaming + tool-state rendering | console stream |
| OPS-08 | pending | Observability: traces, tokens, cost thresholds | CI budget gate |
| OPS-09 | pending | Bedrock / SageMaker evaluation path | dated AWS report |
| OPS-10 | pending | Demo, lab recording, Hurix/profile update from verified results | release `v0.1.0` |
| OPS-11 | done | MCP-shaped tool catalog + institution-launch / intake scenarios | `make verify`, `/v1/tools` |
| OPS-12 | done | Deterministic demo replay + engagement / interview docs | `POST /v1/demo/replay` |
