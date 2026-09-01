<p align="center">
  <img src="docs/assets/ops-mark.svg" alt="Agentic Ops mark: retrieve, tool, pause, record" width="88" />
</p>

<p align="center">
  <img src="docs/assets/chat-vs-loop.svg" alt="Chat wrapper versus a seven-stage governed loop with a person on Pause" width="920" />
</p>

# Agentic Ops

### Retrieve. Cite. Pause. Record.

A governed agent for organizational work. Someone asks a handbook question or a program-launch brief. The runtime retrieves approved files (**keyword retrieval today**; hybrid is OPS-05B), calls permissioned tools, cites its sources, and **stops before any write**. A person approves, edits, or rejects. An approved WRITE files **one internal task**. Pause/resume and the task ledger survive an agent restart when Postgres is on.

Not a chatbot. Nothing is emailed. Public/synthetic corpus only. Fake provider is the CI default — recruiters need no API key.

[What it does](#what-this-app-does) ·
[Try it](#try-it-no-keys) ·
[Console](#approval-console) ·
[Roadmap](#roadmap) ·
[FDE map](#what-this-proves-for-fde-hiring) ·
[Run locally](#run-it-locally)

![Status](https://img.shields.io/badge/status-scaffold_v0-8D9088)
![CI](https://github.com/moisestech/agentic-ops/actions/workflows/verify.yml/badge.svg)
![Provider](https://img.shields.io/badge/provider-fake_offline-B6E2BA)

<p align="center">
  <img src="docs/assets/what-the-app-does.svg" alt="Brief, retrieve, tools, draft, evaluate, pause, record" width="920" />
</p>

## What this app does

| You give it | It does | It will not |
| --- | --- | --- |
| A handbook question | Cited answer, or “I do not have approved records” | Invent a Nobel prize, a grant, or a KPI |
| A six-week program launch | Retrieve brief + calendar + budget, then pause | Send calendar invites or buy equipment |
| An intake / write ticket | Cite policy and wait for a reviewer | Close the ticket or write a directory |

Four tools, one permission model:

| Tool | Permission | Role |
| --- | --- | --- |
| `search_documents` | READ | RAG over the org corpus |
| `check_calendar` | READ | Staff capacity / windows |
| `calculate_budget` | READ | Line items vs cap |
| `manage_actions` | WRITE | Tasks stay `pending_approval` until a human decides |

<p align="center">
  <img src="docs/assets/tool-fence.svg" alt="Three READ tools open; manage_actions WRITE locked until a human decides" width="920" />
</p>

```mermaid
flowchart TD
  A[Brief] --> B[Retrieve]
  B --> T[Tools]
  T --> C[Draft and cite]
  C --> D[Evaluate]
  D --> E{Write?}
  E -->|no| F[Answered]
  E -->|yes| G[Pause]
  G -->|approved or edited| H[Internal task]
  G -->|rejected| I[Rejected]
```

## Try it (no keys)

```bash
python3 -m venv .venv && source .venv/bin/activate
make install && make verify
docker compose up -d postgres
make agent-persist
# other terminal:
make web-dev
```

Open [http://localhost:3000/console](http://localhost:3000/console). Leave **Program Launch** selected and click **Run this brief**.

Five-minute script: [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md). Unit tests without Docker: `make verify`. Recruiter gate (includes pause/resume): `make verify-recruiter`.

## Approval console

Seven stages on one screen. Program Launch is the lead.

| | |
| --- | --- |
| **Brief** | Launch bundle (calendar, budget, staff) before Run |
| **Retrieve → Evaluate** | Keyword passages, READ tools, cited draft, grounding/policy |
| **Pause** | Approve / Edit-and-approve / Reject + note |
| **Record** | One internal task + ordered audit. Retry approval is a no-op |

<p align="center">
  <img src="docs/assets/screenshots/console-01-input.png" alt="Program Launch input bundle and seven-stage operator player" width="920" />
</p>

<p align="center">
  <img src="docs/assets/screenshots/console-02-pause.png" alt="Live launch run paused with Approve, Edit-and-approve, and Reject" width="920" />
</p>

<p align="center">
  <img src="docs/assets/screenshots/console-03-record.png" alt="Executed launch record with citations, tools, and audit trace" width="920" />
</p>

## Three briefs

1. **Handbook** — “What is DCC Open Lab and how does it differ from workshops?” → cited answer.
2. **Launch** — “Prepare a six-week creative technology program…” → calendar + budget + pending WRITE.
3. **Refusal** — “Who won the Nobel Prize at DCC last Tuesday?” → fail closed, no fabrication.

Engagement writeups (discovery through handover): [`docs/engagement/`](docs/engagement/). Interview cases: [`docs/cases/`](docs/cases/).

## Roadmap

<p align="center">
  <img src="docs/assets/roadmap-bands.svg" alt="Done, next, later roadmap for Agentic Ops" width="920" />
</p>

<p align="center">
  <img src="docs/assets/fde-spine.svg" alt="Four-repo FDE spine" width="920" />
</p>

| Now | Next (this repo) | Later / skip |
| --- | --- | --- |
| Tools, keyword RAG, MCP-shaped catalog, HITL, durable pause/resume, one internal task, offline evals, FDE docs | **OPS-05B** hybrid retrieval, **OPS-08** cost CI, **OPS-07** streaming | Live providers, hosted demo, `v0.1.0` |
| | | **Skip:** fine-tune, voice clones, travel planner, triple-cloud capstone |

Daily board: [`docs/DAILY.md`](docs/DAILY.md) · skill map: [`docs/FDE-ROADMAP.md`](docs/FDE-ROADMAP.md)

## What this proves for FDE hiring

One customer-shaped system instead of eight course toys. The FDE lifecycle (discover → scope → wire tools → eval → handover) is in this repo; live DCC delivery stays in Infra24.

| FDE skill | In this repo | Honest gap |
| --- | --- | --- |
| When to use an agent | [`docs/cases/01-should-this-be-an-agent.md`](docs/cases/01-should-this-be-an-agent.md) | — |
| Grounded RAG | Keyword retrieval + citation allowlist + golden set | Dense/hybrid is OPS-05B |
| MCP / tool RBAC | Four tools, WRITE pending | No Entra / multi-tenant OAuth |
| HITL | LangGraph `interrupt` + durable resume + console | Streaming UX is OPS-07 |
| Evals as a gate | `make eval-offline` | Not yet a cost/deploy CI fail (OPS-08) |
| Discovery / handover | [`docs/engagement/`](docs/engagement/) | No priced SoW |
| Decomposition cases | [`docs/cases/`](docs/cases/) | Three cases, not a 10-scenario library |
| Multi-agent planner/critic | Not split yet | Optional, same graph only |
| Fine-tuning | Out of scope | Keep skipped |

Sister overlays (do not duplicate): [evidence pipeline](https://github.com/moisestech/agentic-evidence-pipeline) · [flora-field-kit](https://github.com/moisestech/flora-field-kit) · [comfyui-output-provenance](https://github.com/moisestech/comfyui-output-provenance)

## What works today

| Area | Status | Proof |
| --- | --- | --- |
| FastAPI + OpenAPI + health | **done** | `/health`, `/docs` |
| Keyword retrieval + citations | **done** | Nobel trap + golden set |
| Tools + MCP-shaped server | **done** | `GET /v1/tools`, `make mcp` |
| HITL interrupt | **done** | `POST /v1/runs/{id}/decision` |
| Demo replay (no keys) | **done** | `POST /v1/demo/replay` |
| Offline eval | **done** | `make eval-offline` |
| Approval console | **done** | `apps/web` |
| Durable runs / checkpoints / task ledger | **done** | `make verify-recruiter` — restart while paused, one task |
| pgvector hybrid | pending | OPS-05B — do not start a search-demo repo |
| Cost CI budget gate | pending | OPS-08 |
| Streaming tool-state | pending | OPS-07 |
| Live OpenAI / Claude / Bedrock | pending | Fake stays default |

## Run it locally

Python 3.11+, Node 20+, Docker optional.

```bash
make verify              # ruff + unit tests (no Docker)
make verify-recruiter    # Compose Postgres + persistence gate
make agent-persist       # AGENT_PERSISTENCE=postgres on :8080
make web-dev             # console on :3000
make eval-offline        # golden-set report
```

Restart demo: create a launch run, `Ctrl-C` the agent, `make agent-persist` again, then approve the same `thread_id`. Reload `/console?run=<id>` if the page was closed.

No provider credential is required. `AGENT_PROVIDER=fake` is the supported path.

## Repository shape

```text
apps/web/               Approval console
services/agent/         FastAPI + LangGraph + tools + MCP
packages/evals/         Golden set + dated reports
data/                   dcc-public, creative-program, enterprise-intake
scenarios/              Calendar / budget fixtures
fixtures/demo-run.json  Recruiter replay
docs/engagement/        Discovery → handover
docs/cases/             Interview writeups
docs/assets/            Marks, diagrams, console screenshots
```

## Status and limitations

**Status:** scaffold toward `v0.1.0`. OPS-01–05A, 11–12 are done. Hybrid retrieval (OPS-05B), streaming, cost CI, live providers, and a hosted demo are not in this 48-hour slice.

This is a public reference — not customer production, not a live Infra24 deploy, not AWS AgentCore, not ServiceNow ownership.

[Moises Sanabria](https://moises.tech) — artist and full-stack AI systems builder in Miami.

## License

[MIT](LICENSE)
