"""Researcher node — a tool-using ReAct sub-agent.

It receives ONE plan step, then loops (reason -> call web_search/read_url ->
observe) until it can answer, using LangGraph's prebuilt ReAct agent. The tools
are injected at build time (dependency injection) so this node knows nothing
about SearxNG, DuckDuckGo, or MCP — it just calls ``web_search``.
"""
from __future__ import annotations

from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from ..config import get_llm
from ..prompts import RESEARCHER_PROMPT


def make_researcher(tools):
    """Factory: bind the search/crawl tools and return a graph node."""
    agent = create_react_agent(get_llm("reasoning"), tools=tools,
                               prompt=RESEARCHER_PROMPT)

    def researcher(state) -> Command:
        step = state["plan"][state["cursor"]]
        result = agent.invoke({"messages": [("user", step["description"])]})
        answer = result["messages"][-1].content

        plan = state["plan"]
        plan[state["cursor"]]["done"] = True
        plan[state["cursor"]]["result"] = answer

        # Return to the supervisor with the new evidence appended.
        return Command(
            goto="research_team",
            update={"plan": plan,
                    "observations": state["observations"] + [answer]},
        )

    return researcher
