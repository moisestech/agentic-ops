import { generateId } from "ai";

/** Reserved for OPS-07: Vercel AI SDK streaming of graph nodes and tool state. */
export function newClientRunId(): string {
  return generateId();
}
