# Instructor guide: governed GenAI agent lab

This guide turns the Agentic Ops reference implementation into a 90-minute, hands-on module for software engineers, product teams, and technical decision-makers. It is designed to be taught with the repository's default fake provider and synthetic corpus, so the session is reproducible without paid credentials or customer data.

## Learning outcomes

By the end of the module, learners can:

1. distinguish a model response from a grounded, auditable system response;
2. trace retrieval evidence into sentence-level citations;
3. classify tools as read-only or side-effecting;
4. explain why a write action pauses for human approval;
5. run a small offline evaluation and interpret the result;
6. identify which parts of the reference are implemented and which remain roadmap items.

## Prerequisites

- Python 3.12, Node 20, Docker, and Make
- basic Python and HTTP familiarity
- no provider API key required for the core lab

Validate the environment before class:

```bash
make install
make verify
make agent-dev
```

In a second terminal:

```bash
make web-dev
```

## 90-minute plan

| Time | Activity | Evidence of learning |
|---|---|---|
| 0–10 min | Frame the business problem and inspect the architecture | Learners name the trust boundary |
| 10–25 min | Run a grounded handbook question | Learners trace an answer to its citation |
| 25–40 min | Compare answerable and unanswerable prompts | Learners explain the refusal condition |
| 40–60 min | Trigger a proposed write action | Learners identify the interrupt and approval state |
| 60–72 min | Approve, reject, and replay the action | Learners compare audit records |
| 72–82 min | Run the offline evaluation harness | Learners interpret groundedness and refusal checks |
| 82–90 min | Debrief and production-gap review | Learners separate current proof from future work |

## Facilitation path

### 1. Grounded answer

Use the employee-handbook brief. Ask for a policy answer and inspect the returned citations. Have learners locate the cited source in `corpora/employee_handbook/`.

Checkpoint: the answer must be supported by the retrieved text. A fluent answer without support is not a pass.

### 2. Honest refusal

Use the Nobel Prize brief. Ask a question that the local corpus cannot support.

Checkpoint: the system should decline to fabricate and should expose the evidence boundary. Discuss why abstention can be a product feature.

### 3. Human-in-the-loop write

Use the launch-plan brief to request an action with a side effect. Inspect the proposal before approving it, then repeat and reject it.

Checkpoint: no write executes before approval. Learners should be able to identify the proposed payload, decision, and audit entry.

### 4. Offline evaluation

Run:

```bash
.venv/bin/python -m agentic_ops.evals.harness --provider fake
```

Checkpoint: learners can describe what the deterministic fake provider proves—and what it does not prove about a live model.

## Independent validation rubric

Score each dimension 0–2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Grounding | Unsupported output | Partial support | Claims trace to evidence |
| Citation behavior | Missing | Present but unclear | Precise and inspectable |
| Refusal | Hallucinates | Hedged guess | Clear evidence-based abstention |
| Tool safety | Write executes directly | Informal confirmation | Enforced interrupt and decision |
| Auditability | No trace | Partial log | Proposal, decision, and result recorded |
| Explanation | Jargon only | Mostly accurate | Accurate for both technical and business audiences |

A passing demonstration scores at least 9/12 and cannot score 0 on grounding or tool safety.

## Truth boundaries

What this lab currently demonstrates:

- a LangGraph workflow with explicit state;
- keyword retrieval over a synthetic local corpus;
- citations and refusal behavior;
- read/write tool classification;
- human approval for side effects;
- deterministic offline evaluation.

What it does not claim:

- customer production deployment;
- hybrid or dense retrieval;
- live calendar or email integrations;
- production observability, load testing, or cloud hardening;
- measured business outcomes.

Use those boundaries in instruction. When discussing how the system could evolve, label proposed architecture as roadmap rather than implemented proof.

## Common failure modes

- **No citation:** verify the selected brief and corpus path.
- **Write does not pause:** inspect the tool classification and graph interrupt.
- **Eval differs across machines:** confirm the fake provider is selected.
- **Learner confuses demo with production:** return to the truth-boundary table and ask what operational evidence is still missing.

## Assessment prompt

“Explain to a product owner why this agent can be useful even though it sometimes refuses, then show the code path that enforces that behavior.”

A strong response connects business risk, evidence quality, and the implementation without overstating the repository's maturity.
