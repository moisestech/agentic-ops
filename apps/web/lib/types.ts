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

export type TraceEvent = {
  at: string;
  node: string;
  detail: string;
};

export type RunRecord = {
  id: string;
  status: string;
  question: string;
  answer: string | null;
  citations: Citation[];
  proposed_action: ProposedAction | null;
  evaluation: { grounded: boolean; policy_ok: boolean; requires_approval: boolean; reasons: string[] } | null;
  approval: { decision: string; note: string | null } | null;
  outcome: string | null;
  trace: TraceEvent[];
  latency_ms: number | null;
  token_usage: Record<string, number>;
  tool_calls?: { name: string; permission: string }[];
};

export function agentUrl(): string {
  return process.env.NEXT_PUBLIC_AGENT_URL ?? "http://localhost:8080";
}
