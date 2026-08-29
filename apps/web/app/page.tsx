import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <p className="kicker">Public reference · DCC teaching set</p>
      <h1>Retrieve. Cite. Pause. Record.</h1>
      <p className="lede">
        Agentic Ops is a governed agent: it answers from approved records, proposes
        operational actions, waits for a person, and keeps the audit trail. Infra24
        remains the live DCC case. This repo is the recruiter-readable companion.
      </p>
      <div className="grid">
        <article className="card">
          <h2>What it proves</h2>
          <p>FastAPI + LangGraph, hybrid retrieval with citations, human interrupt, eval harness.</p>
        </article>
        <article className="card">
          <h2>What it will not do</h2>
          <p>No auto-send. No private CRM. No invented citations. Destination is an internal record.</p>
        </article>
      </div>
      <p>
        <Link href="/console">Open the approval console →</Link>
      </p>
    </main>
  );
}
