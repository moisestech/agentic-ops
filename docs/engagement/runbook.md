# Runbook

## Recruiter path (no keys)

```bash
python3 -m venv .venv && source .venv/bin/activate
make install
make verify
make agent-dev
```

In another terminal: `cd apps/web && npm install && npm run dev`.  
Open `http://localhost:3000/console` → **Program Launch** → **Run this brief**.

Or: `curl -s -X POST http://localhost:8080/v1/demo/replay | python3 -m json.tool`

## Live path (still fake provider)

Ask a program-launch or intake brief. Approve or reject the draft. Writes stay internal.

## Failures

| Symptom | Check |
| --- | --- |
| Console cannot reach agent | `make agent-dev` on port 8080; CORS in `.env` |
| Empty citations | Corpus missing under `data/<org>` |
| 409 on decision | Run is not `needs_approval` |
| Eval red | `make eval-offline` and read `failures` |
| Process crash | Runtime should mark `failed` and not execute a write |

## Rollback

There is no external side effect in v0. Approved writes file one internal task. Memory mode drops runs on restart; Postgres mode (`make agent-persist`) does not.
