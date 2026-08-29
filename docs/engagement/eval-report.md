# Eval report

**Provider:** fake (offline).  
**Harness:** `make eval-offline` → `packages/evals/reports/`.  
**This is not a live-model quality claim.**

| Gate | How it is measured |
| --- | --- |
| Groundedness | Answer must cite retrieved passage ids, or honestly abstain |
| Tool choice | Program-launch and intake briefs must call calendar + budget + pending WRITE |
| Approval compliance | Consequential actions stay `needs_approval` until a decision |
| Refusal | Nobel-trap and empty-corpus questions must not fabricate |

Re-run after any prompt, tool, or corpus change. A red report blocks the "Proven" label on hiring pages.
