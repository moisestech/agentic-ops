import { ConsoleClient } from "./console-client";

export default function ConsolePage() {
  return (
    <main>
      <p className="kicker">Operator console</p>
      <h1>Ask, then decide.</h1>
      <p className="lede">
        Program launch is the full governed workflow. Approve or edit-and-approve
        files one internal task. Reject creates none. Nothing is emailed.
      </p>
      <ConsoleClient />
    </main>
  );
}
