.PHONY: verify verify-recruiter install agent-dev agent-persist web-dev up down openapi eval-offline demo mcp

PYTHON ?= python3
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff
UVICORN := .venv/bin/uvicorn

install:
	$(PYTHON) -m venv .venv
	$(PIP) install -e "services/agent[dev]"

verify:
	$(RUFF) check services/agent
	cd services/agent && ../../$(PYTEST) -q -m "not persistence"

verify-recruiter:
	docker compose up -d postgres
	@until docker compose exec -T postgres pg_isready -U ops -d ops; do sleep 1; done
	$(RUFF) check services/agent
	cd services/agent && AGENT_PERSISTENCE=postgres DATABASE_URL=postgresql://ops:ops@localhost:5433/ops ../../$(PYTEST) -q

agent-dev:
	$(UVICORN) agentic_ops.main:app --reload --app-dir services/agent/src --port 8080

agent-persist:
	AGENT_PERSISTENCE=postgres DATABASE_URL=postgresql://ops:ops@localhost:5433/ops \
	  $(UVICORN) agentic_ops.main:app --reload --app-dir services/agent/src --port 8080

web-dev:
	npm --prefix apps/web run dev

up:
	docker compose up --build

down:
	docker compose down

openapi:
	.venv/bin/python services/agent/scripts/export_openapi.py

eval-offline:
	.venv/bin/python -m agentic_ops.evals.harness --provider fake

demo:
	.venv/bin/python -c "from agentic_ops.demo import load_demo_run; print(load_demo_run().model_dump_json(indent=2))"

mcp:
	.venv/bin/python -m agentic_ops.mcp
