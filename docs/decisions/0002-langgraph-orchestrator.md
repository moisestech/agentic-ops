# ADR 0002: LangGraph as the orchestrator

## Status

Accepted

## Context

Infra24's agents are hand-rolled TypeScript. `agentic-evidence-pipeline` uses a
persisted state machine with LangGraph-compatible interrupt semantics.

The hiring gap to close here is an actual LangGraph graph: explicit nodes,
checkpointer, retries later, and a human interrupt before consequential tools.

## Decision

`services/agent` compiles a LangGraph `StateGraph`:

`retrieve → tools → draft → evaluate → (await_approval → execute) | respond`

`interrupt()` pauses the graph. Resume happens only through
`POST /v1/runs/{id}/decision`. The fake provider is first-class so CI never
needs a model key.

## Consequences

OpenAI, Claude, and Bedrock adapters must keep the same state contract.
Swapping a provider cannot skip the evaluator or the interrupt.
