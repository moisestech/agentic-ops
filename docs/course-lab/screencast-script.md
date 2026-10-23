# Screencast script: retrieve, cite, pause, record

Target length: 6–7 minutes. Record at 1080p with a readable terminal font. Use the fake provider and synthetic corpus so the walkthrough is repeatable and contains no customer data.

## Before recording

- Run `make verify`.
- Start the agent and web app.
- Select the employee-handbook brief.
- Clear previous demo state.
- Close unrelated tabs and silence notifications.

## Shot list and narration

### 0:00–0:35 — Outcome first

**Screen:** Repository README, then the running app.

**Narration:** “This is Agentic Ops, a public reference implementation for a governed AI workflow. In the next few minutes I’ll show four behaviors: retrieve evidence, cite it, pause before a side effect, and record the decision. The default path uses a deterministic fake provider and synthetic data, so this is a reproducible teaching system—not a claim of customer production.”

### 0:35–1:20 — Architecture and trust boundary

**Screen:** Architecture diagram and tool table.

**Narration:** “The graph owns orchestration state. Retrieval supplies evidence. Tools are classified as read-only or write-capable. Read operations can continue; proposed writes cross a trust boundary and require an explicit human decision.”

Point to the graph interrupt and audit path. Avoid implying that a UI confirmation alone is the safety control.

### 1:20–2:35 — Retrieve and cite

**Screen:** Ask a handbook policy question. Expand the returned citation and open the matching corpus file.

**Narration:** “The answer is not accepted because it sounds plausible. It is accepted only when its claims can be traced to retrieved material. Here the citation identifies the supporting source, and we can inspect the same text in the repository.”

Pause long enough for viewers to read the citation.

### 2:35–3:20 — Refuse outside the evidence

**Screen:** Ask a question the corpus cannot answer.

**Narration:** “When the evidence is missing, the safer behavior is to say so. This refusal is intentional: it makes the boundary visible instead of filling the gap with an unsupported answer.”

### 3:20–4:45 — Pause before a write

**Screen:** Switch to the launch-plan brief and request a side-effecting action. Show the proposal, approve it once, then show the audit record.

**Narration:** “The system can prepare a write, but it cannot silently execute it. The graph pauses with a structured proposal. A person can inspect the payload and approve or reject it. The decision and result are recorded for later review.”

If the default provider simulates execution, say so explicitly.

### 4:45–5:35 — Validate offline

**Screen:** Terminal running:

```bash
.venv/bin/python -m agentic_ops.evals.harness --provider fake
```

**Narration:** “The offline harness checks repeatable behaviors such as evidence use and refusal. Deterministic tests protect the control flow; they do not substitute for live-model evaluation, red teaming, or production monitoring.”

### 5:35–6:25 — Read the limits

**Screen:** README status and roadmap.

**Narration:** “The current implementation proves a governed workflow using keyword retrieval, citations, tools, approval interrupts, and offline evaluations. Hybrid retrieval, live providers, hosted deployment, and production hardening remain roadmap items. Keeping those boundaries explicit is part of the engineering.”

### 6:25–6:45 — Close

**Screen:** App overview and repository URL.

**Narration:** “The core design lesson is simple: useful agent systems need more than a model call. They need evidence, constrained actions, human control at consequential steps, and a record of what happened.”

## Recording quality checklist

- Claims match the current README and roadmap.
- Citations are legible on screen.
- No credentials, private URLs, or personal data appear.
- Every cut follows the stated learning outcome.
- Captions are enabled and technical terms are defined on first use.
- The final recording includes the exact commit used for the demo.
