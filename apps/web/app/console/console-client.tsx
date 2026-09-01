"use client";

import { useEffect, useState } from "react";
import { agentUrl, type RunRecord } from "@/lib/types";

type StageId = "brief" | "retrieve" | "tools" | "draft" | "evaluate" | "pause" | "record";

type Scenario = {
  id: string;
  label: string;
  kind: string;
  question: string;
  org_slug: string;
  require_action: boolean;
  expected: string;
  lead?: boolean;
};

const SCENARIOS: Scenario[] = [
  {
    id: "launch",
    label: "Program Launch",
    kind: "Full governed workflow",
    question:
      "Prepare a six-week creative technology program launch: schedule, budget, equipment, and staff capacity.",
    org_slug: "creative-program",
    require_action: true,
    expected: "Calendar + budget READ tools, then a pending WRITE.",
    lead: true,
  },
  {
    id: "handbook",
    label: "Handbook",
    kind: "Cited answer",
    question: "What is DCC Open Lab and how does it differ from workshops?",
    org_slug: "dcc",
    require_action: false,
    expected: "Cited answer. No write path.",
  },
  {
    id: "refusal",
    label: "Refusal",
    kind: "Insufficient evidence",
    question: "Who won the Nobel Prize in Physics at DCC last Tuesday?",
    org_slug: "dcc",
    require_action: false,
    expected: "Fail closed. No fabrication.",
  },
  {
    id: "intake",
    label: "Enterprise Intake",
    kind: "Alternate write workflow",
    question: "Route this intake ticket for human review after citing the PII policy.",
    org_slug: "enterprise-intake",
    require_action: true,
    expected: "Cited policy, then a pending WRITE.",
  },
];

const STAGES: { id: StageId; n: string; title: string }[] = [
  { id: "brief", n: "01", title: "Brief" },
  { id: "retrieve", n: "02", title: "Retrieve" },
  { id: "tools", n: "03", title: "Tools" },
  { id: "draft", n: "04", title: "Draft" },
  { id: "evaluate", n: "05", title: "Evaluate" },
  { id: "pause", n: "06", title: "Pause" },
  { id: "record", n: "07", title: "Record" },
];

const LAUNCH_BUNDLE = {
  calendar: "Saturday 10:00–13:00 · week-3 instructor A blocked · no second venue without a new hire",
  budget: "$4,800 cap · consumables $900 · nozzles $250 · licenses $1,800 · guest technician $1,700",
  staff: "instructor-a, instructor-b, lab-technician",
  task: "File six-week creative technology program plan for staff review",
};

function currentStage(run: RunRecord | null): StageId {
  if (!run) return "brief";
  if (run.status === "needs_approval") return "pause";
  if (run.status === "executed" || run.status === "rejected" || run.status === "failed") return "record";
  if (run.status === "answered") return "draft";
  if (run.evaluation) return "evaluate";
  if (run.answer) return "draft";
  if (run.tool_calls?.length) return "tools";
  if (run.passages?.length) return "retrieve";
  return "brief";
}

export function ConsoleClient() {
  const [scenario, setScenario] = useState<Scenario>(SCENARIOS[0]);
  const [run, setRun] = useState<RunRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState<StageId>("brief");
  const [note, setNote] = useState("");
  const [editedDraft, setEditedDraft] = useState("");
  const [showEdit, setShowEdit] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const existing = params.get("run");
    if (!existing) return;
    void (async () => {
      try {
        const response = await fetch(`${agentUrl()}/v1/runs/${existing}?org_slug=${scenario.org_slug}`);
        if (!response.ok) throw new Error(`agent ${response.status}`);
        const next = (await response.json()) as RunRecord;
        setRun(next);
        setEditedDraft(next.proposed_action?.draft ?? "");
      } catch (err) {
        setError(err instanceof Error ? err.message : "request failed");
      }
    })();
  }, [scenario.org_slug]);

  useEffect(() => {
    setStage(currentStage(run));
    if (run?.proposed_action?.draft) {
      setEditedDraft(run.proposed_action.draft);
    }
  }, [run?.id, run?.status]);

  async function createRun() {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${agentUrl()}/v1/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: scenario.question,
          org_slug: scenario.org_slug,
          require_action: scenario.require_action,
        }),
      });
      if (!response.ok) throw new Error(`agent ${response.status}`);
      const next = (await response.json()) as RunRecord;
      setRun(next);
      setEditedDraft(next.proposed_action?.draft ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  async function decide(decision: "approved" | "rejected" | "edited") {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${agentUrl()}/v1/runs/${run.id}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          note: note || undefined,
          edited_draft: decision === "edited" ? editedDraft : undefined,
        }),
      });
      if (!response.ok) throw new Error(`agent ${response.status}`);
      setRun((await response.json()) as RunRecord);
      setShowEdit(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <div className="scenarios" role="list">
        {SCENARIOS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="listitem"
            className={`scenario ${item.id === scenario.id ? "on" : ""} ${item.lead ? "lead" : ""}`}
            onClick={() => {
              setScenario(item);
              setRun(null);
              setShowEdit(false);
              setNote("");
              setStage("brief");
            }}
          >
            <span className="step-n">{item.kind}</span>
            <strong>{item.label}</strong>
            <span className="step-body">{item.expected}</span>
          </button>
        ))}
      </div>

      {scenario.id === "launch" ? (
        <div className="bundle card">
          <p className="kicker">Input bundle · creative-program</p>
          <p>
            <strong>Calendar.</strong> {LAUNCH_BUNDLE.calendar}
          </p>
          <p>
            <strong>Budget.</strong> {LAUNCH_BUNDLE.budget}
          </p>
          <p>
            <strong>Staff.</strong> {LAUNCH_BUNDLE.staff}
          </p>
          <p>
            <strong>Intended task.</strong> {LAUNCH_BUNDLE.task}
          </p>
        </div>
      ) : null}

      <form
        className="ask"
        onSubmit={(event) => {
          event.preventDefault();
          void createRun();
        }}
      >
        <textarea
          value={scenario.question}
          readOnly
          aria-label="Scenario brief"
        />
        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? "Running…" : "Run this brief"}
          </button>
        </div>
      </form>
      {error ? (
        <p className="error">
          {error}. Start Postgres, then <code>make agent-persist</code>.
        </p>
      ) : null}

      <ol className="player" aria-label="Operator stages">
        {STAGES.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className={item.id === stage ? "on" : ""}
              onClick={() => setStage(item.id)}
            >
              <span className="step-n">{item.n}</span>
              {item.title}
            </button>
          </li>
        ))}
      </ol>

      {run ? (
        <StagePanel
          stage={stage}
          run={run}
          scenario={scenario}
          busy={busy}
          note={note}
          editedDraft={editedDraft}
          showEdit={showEdit}
          onNote={setNote}
          onEditedDraft={setEditedDraft}
          onShowEdit={setShowEdit}
          onDecide={decide}
        />
      ) : (
        <p className="cite">Run the brief to fill retrieve → record. Stages stay inspectable after.</p>
      )}
    </section>
  );
}

function StagePanel({
  stage,
  run,
  scenario,
  busy,
  note,
  editedDraft,
  showEdit,
  onNote,
  onEditedDraft,
  onShowEdit,
  onDecide,
}: {
  stage: StageId;
  run: RunRecord;
  scenario: Scenario;
  busy: boolean;
  note: string;
  editedDraft: string;
  showEdit: boolean;
  onNote: (value: string) => void;
  onEditedDraft: (value: string) => void;
  onShowEdit: (value: boolean) => void;
  onDecide: (decision: "approved" | "rejected" | "edited") => void;
}) {
  const tone =
    run.status === "needs_approval" ? "wait" : run.status === "rejected" || run.status === "failed" ? "fail" : "ok";

  return (
    <article className="card stage-panel">
      <p>
        <span className={`badge ${tone}`}>{run.status}</span>{" "}
        <span className="mono">
          {run.id.slice(0, 8)} · {run.org_slug ?? scenario.org_slug} · {run.latency_ms ?? "—"}ms
        </span>
      </p>
      {stage === "brief" ? (
        <>
          <h2>Brief</h2>
          <p>{run.question}</p>
          <p className="cite">
            Organization {run.org_slug ?? scenario.org_slug}. Expected: {scenario.expected}
          </p>
          <Duty code="Org slug, scenario fixtures, HTTP create." model="None." human="Chooses the brief." />
        </>
      ) : null}
      {stage === "retrieve" ? (
        <>
          <h2>Retrieve</h2>
          <p className="cite">Keyword overlap on approved files. Hybrid retrieval is OPS-05B.</p>
          {(run.passages ?? []).map((passage) => (
            <p className="cite" key={passage.id}>
              <span className="mono">{passage.source_id}</span> · {passage.title} · score{" "}
              {passage.score} — {passage.text.slice(0, 160)}
            </p>
          ))}
          {!run.passages?.length ? <p className="cite">No passages on this run yet.</p> : null}
          <Duty code="Keyword retriever + allowlist." model="None." human="None." />
        </>
      ) : null}
      {stage === "tools" ? (
        <>
          <h2>Tools</h2>
          <ul className="tools">
            {(run.tool_calls ?? []).map((call, index) => (
              <li key={`${call.name}-${index}`}>
                <code>{call.name}</code>
                <span className={`perm ${call.permission.toLowerCase()}`}>{call.permission}</span>
                <span className="tool-role">
                  {call.result ? JSON.stringify(call.result).slice(0, 140) : "—"}
                </span>
              </li>
            ))}
          </ul>
          {!run.tool_calls?.length ? <p className="cite">No tools recorded.</p> : null}
          <Duty
            code="Catalog + READ/WRITE gate. WRITE stays pending."
            model="None."
            human="None until Pause."
          />
        </>
      ) : null}
      {stage === "draft" ? (
        <>
          <h2>Draft</h2>
          <p>{run.answer}</p>
          {run.citations.map((citation) => (
            <p className="cite" key={citation.passage_id}>
              <span className="mono">{citation.passage_id}</span> — {citation.quote}
            </p>
          ))}
          {run.proposed_action ? (
            <p className="cite">
              Proposed: {run.proposed_action.title} · risk {run.proposed_action.risk}
            </p>
          ) : (
            <p className="cite">No write proposed.</p>
          )}
          <Duty code="Citation packing." model="Grounded sentences from passages." human="None." />
        </>
      ) : null}
      {stage === "evaluate" ? (
        <>
          <h2>Evaluate</h2>
          {run.evaluation ? (
            <ul className="eval">
              <li>grounded · {String(run.evaluation.grounded)}</li>
              <li>policy_ok · {String(run.evaluation.policy_ok)}</li>
              <li>requires_approval · {String(run.evaluation.requires_approval)}</li>
              {run.evaluation.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
              {(run.evaluation.unsupported_claims ?? []).map((claim) => (
                <li key={claim}>unsupported · {claim}</li>
              ))}
            </ul>
          ) : (
            <p className="cite">Evaluator has not run.</p>
          )}
          <Duty
            code="Grounding + policy gate."
            model="Claims checked against citations."
            human="None yet."
          />
        </>
      ) : null}
      {stage === "pause" ? (
        <>
          <h2>Pause</h2>
          {run.proposed_action ? (
            <div>
              <h3>{run.proposed_action.title}</h3>
              <p>{run.proposed_action.draft}</p>
              <p className="cite">
                risk {run.proposed_action.risk} · destination {run.proposed_action.destination} · no
                external side effects
              </p>
            </div>
          ) : (
            <p>No consequential action. This run does not need a write decision.</p>
          )}
          {run.status === "needs_approval" ? (
            <div className="review">
              <label>
                Reviewer note
                <input value={note} onChange={(event) => onNote(event.target.value)} />
              </label>
              {showEdit ? (
                <label>
                  Edited draft
                  <textarea value={editedDraft} onChange={(event) => onEditedDraft(event.target.value)} />
                </label>
              ) : null}
              <div className="actions">
                <button type="button" disabled={busy} onClick={() => onDecide("approved")}>
                  Approve
                </button>
                <button
                  type="button"
                  className="ghost"
                  disabled={busy}
                  onClick={() => {
                    if (!showEdit) onShowEdit(true);
                    else onDecide("edited");
                  }}
                >
                  {showEdit ? "Save edit and approve" : "Edit and approve"}
                </button>
                <button type="button" className="ghost" disabled={busy} onClick={() => onDecide("rejected")}>
                  Reject
                </button>
              </div>
            </div>
          ) : (
            <p className="cite">
              Decision: {run.approval?.decision ?? "none"}. Inspect Record for the task.
            </p>
          )}
          <Duty
            code="LangGraph interrupt. Writes locked."
            model="None."
            human="Approve, edit, or reject."
          />
        </>
      ) : null}
      {stage === "record" ? (
        <>
          <h2>Record</h2>
          {run.internal_task ? (
            <div>
              <p>
                <span className="mono">{run.internal_task.id.slice(0, 8)}</span> ·{" "}
                {run.internal_task.title}
              </p>
              <p>{run.internal_task.body}</p>
              <p className="cite">
                status {run.internal_task.status} · reviewer {run.internal_task.reviewer_decision} ·
                citations {run.internal_task.citation_ids.join(", ") || "—"}
              </p>
            </div>
          ) : run.status === "needs_approval" ? (
            <p className="cite">
              No task yet. Approve or edit-and-approve on Pause. The interrupt survives an agent
              restart; the task is written only after that decision.
            </p>
          ) : (
            <p className="cite">
              No internal task. Read-only answers and rejections create none.
            </p>
          )}
          <h3>Audit</h3>
          <ol className="trace">
            {(run.audit_events ?? []).map((event) => (
              <li key={`${event.seq}-${event.kind}`}>
                <span className="mono">{String(event.seq).padStart(2, "0")}</span> {event.kind} —{" "}
                {event.detail}
              </li>
            ))}
          </ol>
          {!run.audit_events?.length ? <p className="cite">No audit events on this run.</p> : null}
          <Duty
            code="Postgres run, decision, task, audit_events."
            model="None."
            human="Already decided."
          />
        </>
      ) : null}
    </article>
  );
}

function Duty({ code, model, human }: { code: string; model: string; human: string }) {
  return (
    <dl className="duty">
      <div>
        <dt>Deterministic code</dt>
        <dd>{code}</dd>
      </div>
      <div>
        <dt>Model judgment</dt>
        <dd>{model}</dd>
      </div>
      <div>
        <dt>Human decision</dt>
        <dd>{human}</dd>
      </div>
    </dl>
  );
}
