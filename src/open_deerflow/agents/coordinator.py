"""Coordinator node — the entry point and traffic cop.

It classifies the incoming task. Only genuine research tasks are allowed into
the (expensive) planning + tool-using pipeline; everything else short-circuits
to the end. This mirrors DeerFlow's ``coordinator`` node.
"""
from __future__ import annotations

from langgraph.graph import END
from langgraph.types import Command

from ..config import get_llm
from ..prompts import COORDINATOR_PROMPT


def coordinator(state) -> Command:
    llm = get_llm("basic")  # cheap/fast model is enough for a 1-word decision
    verdict = llm.invoke(COORDINATOR_PROMPT.format(task=state["task"])).content

    if "research" in verdict.strip().lower():
        return Command(
            goto="planner",
            update={"messages": [("assistant", "Task accepted — planning.")]},
        )

    return Command(
        goto=END,
        update={"final_report": "This doesn't look like a research task, so "
                                "there's nothing to investigate."},
    )
