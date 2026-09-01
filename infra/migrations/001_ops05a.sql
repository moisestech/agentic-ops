-- OPS-05A: durable runs, one decision per run, one internal task per run, append-only audit.

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    org_slug TEXT NOT NULL,
    status TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS runs_org_updated_idx ON runs (org_slug, updated_at DESC);

CREATE TABLE IF NOT EXISTS decisions (
    run_id TEXT PRIMARY KEY REFERENCES runs (id) ON DELETE CASCADE,
    org_slug TEXT NOT NULL,
    decision TEXT NOT NULL,
    note TEXT,
    edited_draft TEXT,
    decided_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS internal_tasks (
    id TEXT PRIMARY KEY,
    originating_run_id TEXT NOT NULL UNIQUE REFERENCES runs (id) ON DELETE CASCADE,
    org_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    risk TEXT NOT NULL,
    citation_ids JSONB NOT NULL DEFAULT '[]',
    reviewer_decision TEXT NOT NULL,
    reviewer_note TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS internal_tasks_org_idx ON internal_tasks (org_slug);

CREATE TABLE IF NOT EXISTS audit_events (
    run_id TEXT NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    seq INTEGER NOT NULL,
    at TIMESTAMPTZ NOT NULL,
    kind TEXT NOT NULL,
    detail TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (run_id, seq)
);
