"""Research-team node — the supervisor loop.

This is the heart of the "multi-agent" pattern. It owns no LLM of its own; it
just looks at the plan and dispatches the next unfinished step to the agent that
owns it. When every step is done it hands off to the reporter. Each dispatched
agent returns *here*, so control cycles through the supervisor once per step.
"""
from __future__ import annotations

from langgraph.types import Command


def research_team(state) -> Command:
    for step in state["plan"]:
        if not step["done"]:
            goto = "coder" if step["agent"] == "coder" else "researcher"
            return Command(goto=goto, update={"cursor": step["id"]})

    # All steps complete -> synthesise the report.
    return Command(goto="reporter")
