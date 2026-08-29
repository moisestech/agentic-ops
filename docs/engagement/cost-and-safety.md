# Cost and safety

The CI path uses `AGENT_PROVIDER=fake`. Cost is zero. That is intentional: recruiters and GitHub Actions never need a key.

When a live provider is added later:

| Control | Rule |
| --- | --- |
| Default | Fake / cached replay |
| Routing | Retrieval + tools first; model only to draft from passages |
| Caching | Identical brief + corpus hash → replay, do not re-call |
| Batching | Eval harness runs offline against the golden set |
| Writes | Never from the model path; only after `POST /v1/runs/{id}/decision` |
| PII | Public/synthetic corpus only. Ticket text is not stored as raw email. |

**When not to use an agent:** a single policy lookup with one citation, or a form that already has required fields. Use retrieval or no software.

**Injection:** `ignore previous instructions` and similar markers fail the policy evaluator and block execution.
