# Threat model (v0)

This is a public reference implementation, not a SOC 2 claim.

| Threat | Mitigation in v0 | Next |
| --- | --- | --- |
| Invented citations | Citation allowlist; fail closed | Stronger claim-to-span alignment |
| Prompt injection via corpus | Injection markers fail policy; corpus delimited in later providers | Untrusted-content tags in every prompt |
| Approval bypass | Execute node requires resumed `decision=approved` | AuthN on the decision route |
| Secret leakage | No live keys in CI; `.env` gitignored | Redaction helpers on traces |
| Cross-tenant leakage | Single public corpus in v0 | Tenant filters with pgvector |
| Autonomous outreach | Destination is `internal_record` only | Still no email/SMS |

Report secrets privately to the maintainer. Do not file public issues that
include credentials.
