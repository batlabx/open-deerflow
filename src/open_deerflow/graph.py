"""Assemble the LangGraph StateGraph.

Only the entry edge (START -> coordinator) is static. Everything else is routed
dynamically by the ``Command(goto=...)`` each node returns, which is why the
graph definition is so short: the topology lives in the nodes.
"""
from __future__ import annotations

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph

from .agents.coder import make_coder
from .agents.coordinator import coordinator
from .agents.human_feedback import human_feedback
from .agents.planner import planner
from .agents.reporter import reporter
from .agents.research_team import research_team
from .agents.researcher import make_researcher
from .state import DeerState

# The three MCP servers are launched as stdio subprocesses. Point any other MCP
# client (Claude Desktop, Cursor) at these same commands and the tools work
# there too — capabilities are decoupled from this app.
MCP_SERVERS = {
    "search":  {"command": "python", "args": ["-m", "open_deerflow.tools.search_server"],  "transport": "stdio"},
    "crawl":   {"command": "python", "args": ["-m", "open_deerflow.tools.crawl_server"],   "transport": "stdio"},
    "sandbox": {"command": "python", "args": ["-m", "open_deerflow.tools.sandbox_server"], "transport": "stdio"},
}


def _load_mcp_tools():
    """Start the MCP servers and return LangChain-compatible tool objects."""
    client = MultiServerMCPClient(MCP_SERVERS)
    return asyncio.run(client.get_tools())


def build_graph(checkpointer=None):
    tools = _load_mcp_tools()
    research_tools = [t for t in tools if t.name in ("web_search", "read_url")]
    code_tools = [t for t in tools if t.name == "python_exec"]

    g = StateGraph(DeerState)
    g.add_node("coordinator", coordinator)
    g.add_node("planner", planner)
    g.add_node("human_feedback", human_feedback)
    g.add_node("research_team", research_team)
    g.add_node("researcher", make_researcher(research_tools))
    g.add_node("coder", make_coder(code_tools))
    g.add_node("reporter", reporter)

    g.add_edge(START, "coordinator")  # the only static edge

    return g.compile(checkpointer=checkpointer)
