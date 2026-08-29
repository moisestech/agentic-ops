# MCP tool server

Four permissioned tools, same catalog the LangGraph runtime uses.

| Tool | Permission | Purpose |
| --- | --- | --- |
| `search_documents` | READ | RAG over an org corpus |
| `check_calendar` | READ | Staff capacity / constraints |
| `calculate_budget` | READ | Line items vs cap |
| `manage_actions` | WRITE | Tasks stay pending until approval |

## Run

From the repo root, with the agent package installed:

```bash
source .venv/bin/activate
python -m agentic_ops.mcp
```

The process speaks newline-delimited JSON (MCP-shaped, no extra SDK):

```text
{"method":"tools/list"}
{"method":"tools/call","params":{"name":"search_documents","arguments":{"query":"open lab","org_slug":"dcc"}}}
```

HTTP inspect surface (same catalog):

- `GET /v1/tools`
- `POST /v1/tools/{name}`

WRITE calls never persist a task unless `approved=true`, and the graph only
sets that after `POST /v1/runs/{id}/decision`.
