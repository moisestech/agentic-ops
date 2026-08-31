"use client";

import { useState } from "react";
import { agentUrl, type RunRecord } from "@/lib/types";

const EXAMPLES = [
  "What is DCC Open Lab and how does it differ from workshops?",
  "Draft a partner follow-up after DCC network signup.",
  "Prepare a six-week creative technology program launch: schedule, budget, equipment, and staff capacity.",
  "Who won the Nobel Prize in Physics at DCC last Tuesday?",
];

const STAGE_LABELS: Record<string, string> = {
  retrieve: "Retrieve",
  tools: "Tool",
  answer: "Draft",
  evaluate: "Gate",
  approval: "Human",
  execute: "Record",
};

export function ConsoleClient() {
  const [question, setQuestion] = useState(EXAMPLES[1]);
  const [run, setRun] = useState<RunRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function createRun() {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${agentUrl()}/v1/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          org_slug: /program launch|intake ticket/i.test(question)
            ? /intake/i.test(question)
              ? "enterprise-intake"
              : "creative-program"
            : "dcc",
          require_action: /follow-up|invite|email|outreach|program launch|intake/i.test(question),
        }),
      });
      if (!response.ok) throw new Error(`agent ${response.status}`);
      setRun((await response.json()) as RunRecord);
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  async function replayDemo() {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${agentUrl()}/v1/demo/replay`, { method: "POST" });
      if (!response.ok) throw new Error(`agent ${response.status}`);
      setRun((await response.json()) as RunRecord);
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  async function decide(decision: "approved" | "rejected") {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${agentUrl()}/v1/runs/${run.id}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      if (!response.ok) throw new Error(`agent ${response.status}`);
      setRun((await response.json()) as RunRecord);
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <form className="ask" onSubmit={(event) => { event.preventDefault(); void createRun(); }}>
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
        <div className="actions">
          <button type="submit" disabled={busy}>{busy ? "Running…" : "Run workflow"}</button>
          <button type="button" className="ghost" disabled={busy} onClick={() => void replayDemo()}>Replay sample</button>
          {EXAMPLES.map((item) => (
            <button key={item} type="button" className="ghost example" onClick={() => setQuestion(item)}>
              {item.slice(0, 28)}…
            </button>
          ))}
        </div>
      </form>
      {error ? <p className="error">{error}. Start the agent with `make agent-dev`.</p> : null}
      {run ? <RunView run={run} busy={busy} onDecide={decide} /> : null}
    </section>
  );
}

function RunView({ run, busy, onDecide }: { run: RunRecord; busy: boolean; onDecide: (decision: "approved" | "rejected") => void }) {
  const tone = run.status === "needs_approval" ? "wait" : run.status === "rejected" || run.status === "failed" ? "fail" : "ok";
  const evaluation = run.evaluation;
  const totalTokens = (run.token_usage.prompt_tokens ?? 0) + (run.token_usage.completion_tokens ?? 0);

  return (
    <article className="run-shell">
      <header className="run-header">
        <div>
          <p className="kicker">Run control plane</p>
          <h2 className="run-title">{run.question}</h2>
        </div>
        <span className={`badge ${tone}`}>{run.status.replaceAll("_", " ")}</span>
      </header>

      <section className="signal-grid" aria-label="Run signals">
        <Signal label="Latency" value={run.latency_ms ? `${run.latency_ms} ms` : "—"} />
        <Signal label="Tokens" value={String(totalTokens)} />
        <Signal label="Grounded" value={evaluation ? (evaluation.grounded ? "yes" : "no") : "—"} tone={evaluation && !evaluation.grounded ? "fail" : "ok"} />
        <Signal label="Policy" value={evaluation ? (evaluation.policy_ok ? "pass" : "blocked") : "—"} tone={evaluation && !evaluation.policy_ok ? "fail" : "ok"} />
      </section>

      <section className="flow-strip" aria-label="Agent workflow">
        {run.trace.map((event, index) => (
          <div className="flow-node" key={`${event.at}-${event.node}`}>
            <span className="flow-index">{String(index + 1).padStart(2, "0")}</span>
            <strong>{STAGE_LABELS[event.node] ?? event.node}</strong>
            <span>{event.detail}</span>
          </div>
        ))}
      </section>

      <div className="content-grid">
        <section className="panel answer-panel">
          <p className="section-label">Model output</p>
          <h2>Answer</h2>
          <p className="answer-copy">{run.answer}</p>
          {run.citations.length ? (
            <div className="evidence-list">
              {run.citations.map((citation) => (
                <article className="evidence-card" key={citation.passage_id}>
                  <div className="evidence-meta">
                    <span className="icon-token evidence-icon">E</span>
                    <span className="mono">{citation.passage_id}</span>
                    <span className="score">score {citation.score.toFixed(2)}</span>
                  </div>
                  <strong>{citation.title}</strong>
                  <p>{citation.quote}</p>
                </article>
              ))}
            </div>
          ) : <p className="empty-state">No approved evidence returned.</p>}
        </section>

        <aside className="panel control-panel">
          <p className="section-label">Execution boundary</p>
          <h2>Tools + approval</h2>
          <div className="tool-list">
            {run.tool_calls?.map((item) => (
              <div className="tool-row" key={`${item.name}-${item.permission}`}>
                <span className={`icon-token ${item.permission === "WRITE" ? "write-icon" : "read-icon"}`}>{item.permission === "WRITE" ? "W" : "R"}</span>
                <div><strong>{item.name}</strong><span>{item.permission}</span></div>
              </div>
            )) ?? <span className="empty-state">No tools called.</span>}
          </div>

          {run.proposed_action ? (
            <div className="action-card">
              <span className={`risk-badge risk-${run.proposed_action.risk}`}>{run.proposed_action.risk} risk</span>
              <h3>{run.proposed_action.title}</h3>
              <p>{run.proposed_action.draft}</p>
              <p className="mono destination">destination: {run.proposed_action.destination}</p>
            </div>
          ) : null}

          {run.status === "needs_approval" ? (
            <div className="approval-gate">
              <div><span className="icon-token human-icon">H</span><strong>Human decision required</strong></div>
              <p>The workflow is paused before WRITE. Approval changes system state; rejection leaves the external world untouched.</p>
              <div className="actions">
                <button type="button" disabled={busy} onClick={() => onDecide("approved")}>Approve draft</button>
                <button type="button" className="ghost danger" disabled={busy} onClick={() => onDecide("rejected")}>Reject</button>
              </div>
            </div>
          ) : null}
        </aside>
      </div>

      <section className="panel trace-panel">
        <div className="trace-heading"><div><p className="section-label">Observability</p><h2>Trace</h2></div><span className="mono">run {run.id.slice(0, 8)}</span></div>
        <ol className="trace visual-trace">
          {run.trace.map((event, index) => (
            <li key={`${event.at}-${event.node}`}>
              <span className="trace-dot" />
              <span className="trace-number mono">{String(index + 1).padStart(2, "0")}</span>
              <strong>{event.node}</strong>
              <span>{event.detail}</span>
            </li>
          ))}
        </ol>
      </section>
    </article>
  );
}

function Signal({ label, value, tone }: { label: string; value: string; tone?: "ok" | "fail" }) {
  return <div className={`signal ${tone ?? ""}`}><span>{label}</span><strong>{value}</strong></div>;
}
