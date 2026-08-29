# Install this in a cautious org next week

**Prompt:** Security wants RBAC, an audit log, and no shadow MCP servers.

**Week-one install**

- One corpus directory they already approve.
- Four tools with explicit READ/WRITE. WRITE is pending until a named person clicks approve.
- HTTP `GET /v1/tools` plus the stdio MCP-shaped server — same catalog, no surprise tools.
- Trace on every run: citations, tool names, decision, latency, tokens.
- Demo replay with no keys so legal can watch the path before any live model.

**Do not claim:** SOC 2, ServiceNow ownership, or a customer production deploy.

**Handover:** program lead owns markdown and fixtures; engineer owns the eval gate.
