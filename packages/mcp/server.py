"""Thin entry so `packages/mcp` is inspectable. Runtime lives in agentic_ops.mcp."""

from agentic_ops.mcp import handle, main

__all__ = ["handle", "main"]

if __name__ == "__main__":
    main()
