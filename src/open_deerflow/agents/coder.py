"""Coder node — a tool-using ReAct sub-agent for analysis.

Identical shape to the researcher, but wired to the ``python_exec`` sandbox tool
instead of search. This symmetry is deliberate: a "team member" is just an LLM +
a prompt + a set of tools. Swap the tools and the prompt and you have a new
specialist without touching the graph.
"""
from __future__ import annotations

from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from ..config import get_llm
from ..prompts import CODER_PROMPT


def make_coder(tools):
    """Factory: bind the sandbox tool and return a graph node."""
    agent = create_react_agent(get_llm("reasoning"), tools=tools,
                               prompt=CODER_PROMPT)

    def coder(state) -> Command:
        step = state["plan"][state["cursor"]]
        # Give the analyst the step plus evidence gathered so far.
        context = "\n".join(state["observations"][-4:])
        prompt = f"{step['description']}\n\nContext so far:\n{context}"
        result = agent.invoke({"messages": [("user", prompt)]})
        answer = result["messages"][-1].content

        plan = state["plan"]
        plan[state["cursor"]]["done"] = True
        plan[state["cursor"]]["result"] = answer

        return Command(
            goto="research_team",
            update={"plan": plan,
                    "observations": state["observations"] + [answer]},
        )

    return coder
