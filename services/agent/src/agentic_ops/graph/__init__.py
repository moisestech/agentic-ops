from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agentic_ops.config import settings
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

_graph = None
_pool = None


def reset_graph() -> None:
    global _graph, _pool
    _graph = None
    if _pool is not None:
        _pool.close()
        _pool = None


def _postgres_checkpointer():
    global _pool
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg_pool import ConnectionPool

    if _pool is None:
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=8,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
    saver = PostgresSaver(conn=_pool)
    saver.setup()
    return saver


def build_graph(checkpointer=None):
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
    saver = checkpointer
    if saver is None:
        saver = _postgres_checkpointer() if settings.use_postgres else MemorySaver()
    return graph.compile(checkpointer=saver)


def compiled_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
