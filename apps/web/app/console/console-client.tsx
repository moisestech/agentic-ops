"use client";

import { useState } from "react";
import { agentUrl, type RunRecord } from "@/lib/types";

const EXAMPLES = [
  "What is DCC Open Lab and how does it differ from workshops?",
  "Draft a partner follow-up after DCC network signup.",
  "Prepare a six-week creative technology program launch: schedule, budget, equipment, and staff capacity.",
  "Who won the Nobel Prize in Physics at DCC last Tuesday?",
];

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
      <form
        className="ask"
        onSubmit={(event) => {
          event.preventDefault();
          void createRun();
        }}
      >
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? "Running…" : "Run"}
          </button>
          <button type="button" className="ghost" disabled={busy} onClick={() => void replayDemo()}>
            Replay sample workflow
          </button>
          {EXAMPLES.map((item) => (
            <button key={item} type="button" className="ghost" onClick={() => setQuestion(item)}>
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

function RunView({
  run,
  busy,
  onDecide,
}: {
  run: RunRecord;
  busy: boolean;
  onDecide: (decision: "approved" | "rejected") => void;
}) {
  const tone = run.status === "needs_approval" ? "wait" : run.status === "rejected" || run.status === "failed" ? "fail" : "ok";
  return (
    <article className="card">
      <p>
        <span className={`badge ${tone}`}>{run.status}</span>{" "}
        <span className="mono">
          {run.id.slice(0, 8)} · {run.latency_ms ?? "—"}ms · tokens{" "}
          {(run.token_usage.prompt_tokens ?? 0) + (run.token_usage.completion_tokens ?? 0)}
        </span>
      </p>
      <h2>Answer</h2>
      <p>{run.answer}</p>
      {run.citations.map((citation) => (
        <p className="cite" key={citation.passage_id}>
          <span className="mono">{citation.passage_id}</span> — {citation.quote}
        </p>
      ))}
      {run.tool_calls?.length ? (
        <p className="cite">
          tools {run.tool_calls.map((item) => item.name).join(" → ")}
        </p>
      ) : null}
      {run.proposed_action ? (
        <div>
          <h2>{run.proposed_action.title}</h2>
          <p>{run.proposed_action.draft}</p>
          <p className="cite">
            risk {run.proposed_action.risk} · destination {run.proposed_action.destination}
          </p>
        </div>
      ) : null}
      {run.status === "needs_approval" ? (
        <div className="actions">
          <button type="button" disabled={busy} onClick={() => onDecide("approved")}>
            Approve draft
          </button>
          <button type="button" className="ghost" disabled={busy} onClick={() => onDecide("rejected")}>
            Reject
          </button>
        </div>
      ) : null}
      <h2>Trace</h2>
      <ol className="trace">
        {run.trace.map((event) => (
          <li key={`${event.at}-${event.node}`}>
            <span className="mono">{event.node}</span> — {event.detail}
          </li>
        ))}
      </ol>
    </article>
  );
}
