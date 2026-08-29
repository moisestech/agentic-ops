import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic Ops",
  description: "Retrieve, cite, pause for approval, record the outcome.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <nav className="top">
            <Link href="/">agentic-ops</Link>
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
