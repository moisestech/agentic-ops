# ADR 0001: Companion-repo boundary

## Status

Accepted

## Context

Infra24 already runs a Memory Agent and a Network Readiness approval flow on
DCC. It is a large multi-tenant platform. Recruiter-readable proof of Python,
LangGraph, Vercel AI SDK, and AWS evaluation does not belong buried there.

`agentic-evidence-pipeline` already proves TypeScript evidence gates. It does
not close the Python/LangGraph hiring gap.

## Decision

Publish `moisestech/agentic-ops` as a **public companion**:

- Infra24 remains the live customer-delivery case.
- This repo is the clean reference implementation and coding-lab sample.
- The DCC public sample corpus is a portable teaching set, not a CRM export.
- Credential rotation, pgvector migration, embedding sync, and lockfile repair
  stay P1 work **inside Infra24**. They are not duplicated here.

## Consequences

Claims about live DCC routes must be verified against Infra24, not inferred
from this scaffold. This repo may compare against Infra24 using the same
golden questions once both eval reports are dated and published.
