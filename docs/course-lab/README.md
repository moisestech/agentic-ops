# Course lab — governed agents (90 minutes)

**Audience:** software engineers, product teams, and technical decision-makers learning applied GenAI.
**Repo:** `moisestech/agentic-ops`
**Delivery assets:** [instructor guide](./instructor-guide.md) · [screencast script](./screencast-script.md)

## Learning objectives

1. Retrieve with citations instead of unconstrained chat.
2. Separate deterministic gates from model-drafted text.
3. Implement a human interrupt before a consequential tool.
4. Read an audit trail for the proposal, decision, and outcome.
5. Explain which behaviors the reference proves and which remain roadmap items.

## Instructor setup

- Docker Desktop, Python 3.12, Node 20, and Make.
- No provider key required (`AGENT_PROVIDER=fake`).
- Clone the repository and run:

```bash
make install
make verify
make agent-dev
```

Start the web app in a second terminal with `make web-dev`.

## Student path

1. Ask a handbook question and inspect its citations.
2. Ask a question outside the corpus and confirm the fail-closed answer.
3. Request a side-effecting action; approve and reject it in two runs.
4. Inspect the audit records for both decisions.
5. Run the deterministic offline evaluation.
6. (Stretch) Swap in a live provider behind the same graph contract.

## Assessment

Learners must demonstrate a grounded answer, an evidence-based refusal, and a write that cannot proceed without approval. Use the rubric in the [instructor guide](./instructor-guide.md).

## Truth boundary

The lab currently demonstrates keyword retrieval, citations, read/write tool classification, human approval, and deterministic offline evaluations. It is a public reference implementation, not evidence of a customer production deployment. Hybrid retrieval, live integrations, and production hardening remain roadmap work.
