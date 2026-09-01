export type Citation = {
  passage_id: string;
  source_id: string;
  title: string;
  quote: string;
  score: number;
};

export type ProposedAction = {
  action_type: string;
  title: string;
  draft: string;
  risk: string;
  destination: string;
};

export type Evaluation = {
  grounded: boolean;
  policy_ok: boolean;
  requires_approval: boolean;
  reasons: string[];
  unsupported_claims?: string[];
};

export type ToolCall = {
  name: string;
  permission: string;
  arguments?: Record<string, unknown>;
  result?: Record<string, unknown>;
};

export type Passage = {
  id: string;
  source_id: string;
  title: string;
  text: string;
  score: number;
};

export type InternalTask = {
  id: string;
  originating_run_id: string;
  title: string;
  body: string;
  status: string;
  risk: string;
  org_slug: string;
  citation_ids: string[];
  reviewer_decision: string;
  reviewer_note: string | null;
  created_at: string;
};

export type AuditEvent = {
  run_id: string;
  seq: number;
  at: string;
  kind: string;
  detail: string;
};

export type TraceEvent = {
  at: string;
  node: string;
  detail: string;
  data?: Record<string, unknown>;
};

export type RunRecord = {
  id: string;
  status: string;
  question: string;
  org_slug?: string;
  answer: string | null;
  citations: Citation[];
  proposed_action: ProposedAction | null;
  evaluation: Evaluation | null;
  approval: { decision: string; note: string | null; edited_draft?: string | null } | null;
  outcome: string | null;
  trace: TraceEvent[];
  latency_ms: number | null;
  token_usage: Record<string, number>;
  tool_calls?: ToolCall[];
  passages?: Passage[];
  internal_task?: InternalTask | null;
  internal_task_id?: string | null;
  audit_events?: AuditEvent[];
};

export function agentUrl(): string {
  return process.env.NEXT_PUBLIC_AGENT_URL ?? "http://localhost:8080";
}
