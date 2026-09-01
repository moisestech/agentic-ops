import Link from "next/link";

const STEPS = [
  { n: "01", title: "Brief", body: "Handbook question, program launch, or intake ticket." },
  { n: "02", title: "Retrieve", body: "Keyword overlap on approved files. Source ids travel with the answer. Hybrid is OPS-05B." },
  { n: "03", title: "Tools", body: "Calendar and budget are READ. Writes stay locked." },
  { n: "04", title: "Draft", body: "Grounded draft, or an honest abstention. No invented KPIs." },
  { n: "05", title: "Evaluate", body: "Grounding, policy, and whether a write needs a human." },
  { n: "06", title: "Pause", body: "A person approves, edits, or rejects before anything is filed.", accent: true },
  { n: "07", title: "Record", body: "One internal task after approval. Append-only audit. No email." },
];

const GRAPH = ["brief", "retrieve", "tools", "draft", "evaluate", "pause", "record"];

const TOOLS = [
  { name: "search_documents", perm: "READ", role: "RAG over the org corpus" },
  { name: "check_calendar", perm: "READ", role: "Staff capacity and windows" },
  { name: "calculate_budget", perm: "READ", role: "Line items versus the cap" },
  { name: "manage_actions", perm: "WRITE", role: "Pending until a human decides" },
];

const CONTRACTS = [
  {
    give: "A handbook question",
    does: "Cited answer, or “I do not have approved records.”",
    willNot: "Invent a Nobel prize, a grant, or a KPI",
  },
  {
    give: "A six-week program launch",
    does: "Retrieve brief, calendar, and budget — then pause.",
    willNot: "Send invites or buy equipment",
  },
  {
    give: "An intake / write ticket",
    does: "Cite policy and wait for a reviewer.",
    willNot: "Close the ticket or write a directory",
  },
];

const BRIEFS = [
  {
    n: "01",
    title: "Handbook",
    ask: "What is DCC Open Lab and how does it differ from workshops?",
    out: "Cited answer",
  },
  {
    n: "02",
    title: "Launch",
    ask: "Prepare a six-week creative technology program…",
    out: "Calendar + budget + pending WRITE",
  },
  {
    n: "03",
    title: "Refusal",
    ask: "Who won the Nobel Prize at DCC last Tuesday?",
    out: "Fail closed — no fabrication",
  },
];

const FDE = [
  {
    side: "AI engineering",
    items: [
      "LangGraph: brief → retrieve → tools → draft → evaluate → pause → record",
      "Citation fail-closed (the Nobel trap does not fabricate)",
      "MCP-shaped tool catalog with explicit READ / WRITE",
      "Offline golden evals; fake provider so CI never needs a key",
    ],
  },
  {
    side: "FDE delivery",
    items: [
      "Customer-shaped domain: a cultural lab launching a six-week program",
      "Discovery, constraints, cost/safety, runbook, handover in docs/",
      "Three decomposition cases for the Palantir-style round",
      "Enablement: a non-engineer can run Program Launch and reject without the builder",
    ],
  },
];

const SKILLS = [
  { skill: "When to use an agent", here: "Interview case: should this be an agent", gap: "—" },
  { skill: "Grounded RAG", here: "Keyword retrieval + citation allowlist + golden set", gap: "Dense / hybrid is OPS-05B" },
  { skill: "MCP / tool RBAC", here: "Four tools, WRITE pending", gap: "No Entra / multi-tenant OAuth" },
  { skill: "HITL", here: "Durable interrupt + console player", gap: "Streaming UX is OPS-07" },
  { skill: "Evals as a gate", here: "make eval-offline", gap: "Cost/deploy CI fail is OPS-08" },
  { skill: "Discovery / handover", here: "docs/engagement/", gap: "No priced SoW" },
  { skill: "Decomposition cases", here: "docs/cases/ — three writeups", gap: "Not a 10-scenario library" },
];

const SPINE = [
  { name: "Agentic Ops", lane: "This runtime", role: "Agents, RAG, MCP, HITL, evals, FDE docs" },
  { name: "Evidence", lane: "Sister overlay", role: "Citations, fail-closed policy, durable jobs" },
  { name: "Field Kit", lane: "Sister overlay", role: "Brief → techniques → review → case" },
  { name: "Provenance", lane: "Sister overlay", role: "CI, tests, auditability — production OSS" },
];

export default function HomePage() {
  return (
    <main className="home">
      <section className="hero">
        <p className="kicker">Governed agent · public reference</p>
        <h1>Retrieve. Cite. Pause. Record.</h1>
        <p className="lede">
          Someone asks an organizational brief. The runtime answers only from approved
          records, calls permissioned tools, and stops before any write. That loop — not
          a chatbot demo — is the engineering half of a Forward Deployed role.
        </p>
        <div className="hero-actions">
          <Link className="btn" href="/console">
            Open the approval console
          </Link>
          <a className="btn ghost" href="https://github.com/moisestech/agentic-ops">
            Source on GitHub
          </a>
        </div>
        <p className="hero-note">
          No API key. Run <strong>Program Launch</strong> on the console.
        </p>
      </section>

      <section className="band">
        <p className="kicker">Architecture</p>
        <h2>One graph. Four tools. A human on the write.</h2>
        <p className="section-lede">
          FastAPI owns the HTTP surface. LangGraph owns the state machine. Tools share
          one catalog with the MCP-shaped server. The evaluator can fail a draft closed.
          Writes never execute from the model path.
        </p>

        <figure className="proof">
          <img
            src="/what-the-app-does.svg"
            alt="Seven stages: brief, retrieve, tools, draft, evaluate, pause, record"
          />
          <figcaption>
            Keyword overlap on approved files. Hybrid is later.
          </figcaption>
        </figure>

        <ol className="flow">
          {STEPS.map((step) => (
            <li
              key={step.n}
              className={[
                step.accent ? "accent" : "",
                step.done ? "done" : "",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              <span className="step-n">{step.n}</span>
              <strong>{step.title}</strong>
              <span className="step-body">{step.body}</span>
            </li>
          ))}
        </ol>

        <div className="graph-strip" aria-label="LangGraph node order">
          <p className="kicker">Graph</p>
          <ol>
            {GRAPH.map((node) => (
              <li key={node}>
                <code>{node}</code>
              </li>
            ))}
          </ol>
          <p className="graph-note">
            Same seven stages as the console. After evaluate: answer if no write,
            pause if a write is pending. Nothing is emailed.
          </p>
        </div>

        <ul className="tools">
          {TOOLS.map((tool) => (
            <li key={tool.name}>
              <code>{tool.name}</code>
              <span className={`perm ${tool.perm.toLowerCase()}`}>{tool.perm}</span>
              <span className="tool-role">{tool.role}</span>
            </li>
          ))}
        </ul>

        <figure className="proof">
          <img
            src="/tool-fence.svg"
            alt="Three READ tools open; manage_actions WRITE locked until a human decides"
          />
          <figcaption>
            The model may propose. It may not execute.
          </figcaption>
        </figure>
      </section>

      <section className="band">
        <p className="kicker">Contract</p>
        <h2>What you give it. What it will not do.</h2>
        <p className="section-lede">
          Three briefs. Same permission model. The Nobel trap is the proof that
          retrieval is fail-closed, not a chatbot with a citation skin.
        </p>
        <div className="contract">
          <div className="contract-head">
            <span>You give it</span>
            <span>It does</span>
            <span>It will not</span>
          </div>
          {CONTRACTS.map((row) => (
            <div className="contract-row" key={row.give}>
              <strong>{row.give}</strong>
              <span>{row.does}</span>
              <span className="will-not">{row.willNot}</span>
            </div>
          ))}
        </div>
        <ul className="briefs">
          {BRIEFS.map((brief) => (
            <li key={brief.n}>
              <span className="step-n">{brief.n}</span>
              <strong>{brief.title}</strong>
              <p>{brief.ask}</p>
              <span className="brief-out">{brief.out}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="band">
        <p className="kicker">Console</p>
        <h2>Seven stages. One write. A person on the pause.</h2>
        <p className="section-lede">
          Approve or edit-and-approve files one internal task. Reject creates none.
          Recruiters can run Program Launch without a provider key.
        </p>
        <figure className="proof">
          <img
            src="/screenshots/console-02-pause.png"
            alt="Operator console paused on the program-launch write with Approve, Edit-and-approve, and Reject"
          />
          <figcaption>
            Live six-week launch at Pause — keyword retrieve, calendar and budget
            tools, then a human decision before any task is filed.
          </figcaption>
        </figure>
      </section>

      <section className="band">
        <p className="kicker">FDE qualification</p>
        <h2>The role is two stacks. This repo holds both, inspectably.</h2>
        <p className="section-lede">
          Forward Deployed Engineering is customer discovery plus production agent
          systems. Agentic Ops is one customer-shaped engagement you can run, reject,
          and defend — not eight course toys, and not a claim of Bedrock or
          ServiceNow ownership.
        </p>
        <div className="split">
          {FDE.map((col) => (
            <article key={col.side} className="card deep">
              <p className="kicker">{col.side}</p>
              <ul>
                {col.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        <p className="kicker table-kicker">Skill map</p>
        <div className="skill-wrap">
          <table className="skill-map">
            <thead>
              <tr>
                <th>FDE skill</th>
                <th>In this repo</th>
                <th>Honest gap</th>
              </tr>
            </thead>
            <tbody>
              {SKILLS.map((row) => (
                <tr key={row.skill}>
                  <th scope="row">{row.skill}</th>
                  <td>{row.here}</td>
                  <td className="gap">{row.gap}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="kicker table-kicker">Portfolio spine</p>
        <ul className="spine">
          {SPINE.map((repo) => (
            <li key={repo.name} className={repo.name === "Agentic Ops" ? "here" : ""}>
              <strong>{repo.name}</strong>
              <span className="step-n">{repo.lane}</span>
              <span className="step-body">{repo.role}</span>
            </li>
          ))}
        </ul>
        <p className="spine-note">
          This service is the runtime. Sister repos cover governance inspect, creative
          delivery, and production OSS. There is no fifth product.
        </p>
      </section>

      <section className="band">
        <p className="kicker">Honest status</p>
        <h2>What to send a hiring team — and what not to claim.</h2>
        <div className="status-row">
          <article className="card status proven">
            <h3>Proven here</h3>
            <p>
              Keyword retrieval with citations, permissioned tools, HITL interrupt,
              durable pause/resume, one internal task after approval, offline evals,
              engagement docs. Fake provider is the supported path.
            </p>
          </article>
          <article className="card status next">
            <h3>Next in this repo</h3>
            <p>
              OPS-05B hybrid retrieval, a cost CI gate, and streaming. Hosted demo
              and v0.1.0 after that. This 48-hour slice does not include those.
            </p>
          </article>
          <article className="card status later">
            <h3>Not claimed</h3>
            <p>
              Customer production, Infra24 live routes, ServiceNow, SOC 2, fine-tuning,
              voice agents, or a triple-cloud capstone.
            </p>
          </article>
        </div>
        <p className="close">
          <Link href="/console">Run a brief in the console</Link>
          {" · "}
          <a href="https://github.com/moisestech/agentic-ops/blob/main/docs/FDE-ROADMAP.md">
            Full skill map
          </a>
        </p>
      </section>
    </main>
  );
}
