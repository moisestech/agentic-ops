# Agentic Ops visual language

The UI should make agent behavior legible before it makes it attractive. Every visual must answer at least one operational question: **what happened, why, what can happen next, and who controls it?**

## Core semantic roles

| Role | Token | Meaning | Default treatment |
| --- | --- | --- | --- |
| Evidence | `E` | Retrieved source passage | cyan / outlined circle |
| READ tool | `R` | Permissioned observation | blue / outlined circle |
| WRITE tool | `W` | State-changing action | violet / outlined circle |
| Human | `H` | Approval or editorial judgment | teal / outlined circle |
| Pass | label + icon | Gate cleared | green text/border |
| Wait | label + icon | Human or dependency pending | amber text/border |
| Block | label + icon | Policy, evidence, or execution failure | red text/border |

Color is never the only carrier. Pair color with a token, text label, border, and/or shape.

## Primary views

### 1. Recruiter / customer narrative

Use a compact six-stage flow:

`Brief → Retrieve → Tools → Cited draft → Gate → Human / Record`

Goal: explain the system in under 30 seconds.

### 2. Operator run view

Expose:

- run status
- latency and token use
- grounding / policy results
- ordered graph stages
- citations with scores
- tool names + READ/WRITE permission
- proposed action risk + destination
- explicit human approval boundary
- trace events

Goal: answer “why did the system do this?” without opening logs.

### 3. Failure view

Failure is a first-class product state, not an error toast. Show:

- the failed or blocked gate
- the evidence/tool/policy object that caused it
- the safe next action
- what the system **did not** execute

## Diagram rules

1. Deterministic components use rectangles.
2. Model interpretation uses a distinct soft container, never a magic sparkle icon.
3. Human decisions use a circular `H` token and explicit boundary line.
4. External writes appear only after the human boundary.
5. Evidence lineage always points from source → passage → claim.
6. Every architecture diagram should identify deterministic vs probabilistic work.

## FDE concepts the visuals should teach

- human-in-the-loop / interrupt-resume
- tool RBAC / least privilege
- grounded RAG and citation gates
- stateful workflow / explicit state machine
- observability / traces
- evaluation gates
- failure injection / fail-closed behavior
- idempotency and durable execution
- cost / latency budgets
- environment and provider boundaries

## Next visual artifacts

1. **Run anatomy** — one annotated console screenshot naming state, evidence, tools, gate, human boundary, trace.
2. **Permission boundary** — READ tools above line, WRITE below approval line.
3. **Happy path vs fail-closed path** — paired diagram using the Nobel trap.
4. **Hybrid retrieval view** — lexical + vector → fused ranking with per-hit provenance.
5. **Eval gate card** — groundedness, citation precision, refusal rate, cost/run, latency.
6. **Deployment boundary** — offline fake provider / local app / optional live provider.

These should be generated from or faithfully reflect real system state; avoid decorative “AI network” imagery that cannot be mapped back to implementation.
