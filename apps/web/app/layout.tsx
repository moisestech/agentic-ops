import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic Ops — Retrieve. Cite. Pause. Record.",
  description:
    "Governed agent for organizational briefs: cited retrieval, permissioned tools, human approval before writes. Public FDE reference — no API key required.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <nav className="top">
            <Link href="/" className="brand">
              <img src="/ops-mark.svg" alt="" width={28} height={28} />
              agentic-ops
            </Link>
            <span>
              <Link href="/console">console</Link>
              {" · "}
              <a href="https://github.com/moisestech/agentic-ops">github</a>
            </span>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
