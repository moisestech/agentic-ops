import { ConsoleClient } from "./console-client";

export default function ConsolePage() {
  return (
    <main>
      <p className="kicker">Approval console</p>
      <h1>Ask, then decide.</h1>
      <p className="lede">
        Consequential drafts pause here. Approve files an internal record. Reject
        stops execution. Nothing is emailed.
      </p>
      <ConsoleClient />
    </main>
  );
}
