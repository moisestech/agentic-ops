# ADR 0003: Public corpus only

## Status

Accepted

## Context

Live Memory Agent retrieval in Infra24 can see staff-approved institutional
records. A public GitHub repo cannot.

## Decision

`data/dcc-public` contains original public/synthetic markdown only. No emails,
phones, applicant files, or production secrets. Prompt construction still
treats corpus text as untrusted data.

## Consequences

Golden questions that need private Oolite or CRM rows stay in Infra24's eval
harness. This repo's harness covers the public DCC teaching set.
