from __future__ import annotations

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agentic_ops.graph.nodes import (
    await_approval_node,
    draft_node,
    evaluate_node,
    execute_node,
    respond_node,
    retrieve_node,
    route_after_eval,
    tools_node,
)
from agentic_ops.graph.state import AgentState


@lru_cache(maxsize=1)
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("tools", tools_node)
    graph.add_node("draft", draft_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("await_approval", await_approval_node)
    graph.add_node("respond", respond_node)
    graph.add_node("execute", execute_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "tools")
    graph.add_edge("tools", "draft")
    graph.add_edge("draft", "evaluate")
    graph.add_conditional_edges(
        "evaluate",
        route_after_eval,
        {"await_approval": "await_approval", "respond": "respond"},
    )
    graph.add_edge("await_approval", "execute")
    graph.add_edge("respond", END)
    graph.add_edge("execute", END)
    return graph.compile(checkpointer=MemorySaver())
