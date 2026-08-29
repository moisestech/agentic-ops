# Architecture

**Status:** v0 scaffold. The FastAPI/LangGraph path, keyword retrieval, citation
gate, and approval interrupt are implemented. pgvector, live providers, and
Bedrock eval are planned.

## Companion boundary

```mermaid
flowchart LR
    Q[Institutional question] --> AOPS[agentic-ops<br/>public reference]
    Q --> I24[Infra24<br/>live DCC delivery]
    AOPS --> Corpus[data/dcc-public]
    I24 --> Live[(Airtable + Supabase)]
    AOPS --> Graph[LangGraph interrupt]
    I24 --> Memory[Memory Agent]
    I24 --> Network[Network Readiness]
```

| Repo | Role |
| --- | --- |
| `moisestech/infra24` | Live customer-delivery platform. Memory Agent + Network Readiness on DCC. |
| `moisestech/agentic-evidence-pipeline` | TypeScript evidence/assessment pipeline. Adjacent proof. |
| `moisestech/agentic-ops` | Recruiter-readable Python + LangGraph + Vercel AI SDK reference. |

Infra24 is the production comparison, not a file to copy into this repo.

## Product workflow

```mermaid
flowchart TD
    A[Question or operational brief] --> B[Retrieve]
    B --> T[Permissioned tools]
    T --> C[Cited draft + optional action]
    C --> D[Grounding and policy evaluators]
    D --> E{Consequential action?}
    E -->|no| F[Answered]
    E -->|yes| G[Human approval interrupt]
    G -->|approved| H[Execute approved draft only]
    G -->|rejected| I[Rejected]
    H --> J[Audit record]
    F --> J
    I --> J
```

## Run states

`queued → retrieving → drafting → evaluating → needs_approval | answered → executed | rejected | failed`

Invalid transitions fail. A process restart must not lose a pending approval
once Postgres checkpointer lands (in-memory checkpointer for v0 tests).

## Deterministic vs model-driven

| Deterministic | Model-driven |
| --- | --- |
| Load and chunk corpus | Map passages to an answer |
| Keyword (and later vector) retrieval | Optional action draft |
| Citation allowlist, policy markers | Bounded repair later |
| Approval / reject commands | — |
| Audit persistence | — |

## Stack

- FastAPI service with committed OpenAPI
- LangGraph state graph + interrupt/resume
- LangChain text splitters for chunking
- PostgreSQL + pgvector (Compose image present; retrieval is keyword-first)
- Next.js console with Vercel AI SDK types reserved for streaming
- Fake provider as the CI default
- Shared tool catalog + MCP-shaped stdio server
- Deterministic demo replay at `POST /v1/demo/replay`
