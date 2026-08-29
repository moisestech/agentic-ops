# AWS evaluation path (P2)

This directory is reserved for the Bedrock evaluation job that reuses
`packages/evals` golden fixtures.

**Not claimed as production AWS experience.** The first merge will add:

1. An IAM-scoped Bedrock invoke role (no wildcard `*`).
2. A SageMaker processing job **or** Bedrock model evaluation config that
   scores the same dated golden set used in CI.
3. A published report under `packages/evals/reports/`.

Until that lands, `AGENT_PROVIDER=fake` is the supported path.
