# ADR 0004: Shared tool catalog, MCP-shaped server

## Status

Accepted

## Context

Hiring conversations for Stacklok, Glean, and similar FDE roles ask how tools
are exposed, permissioned, and approved. A LangGraph node that only calls
internal functions is not inspectable as a tool server.

## Decision

One catalog in `agentic_ops.tools` is used by:

- the LangGraph `tools` node
- `GET /v1/tools` and `POST /v1/tools/{name}`
- `python -m agentic_ops.mcp` (newline JSON, no extra SDK)

WRITE tools return `pending_approval` unless a human decision has been recorded.

## Consequences

Adding a fifth tool means adding it once. A second MCP implementation is not
allowed to grow a different permission model.
