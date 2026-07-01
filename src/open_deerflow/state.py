"""Shared graph state.

LangGraph passes one mutable state object between nodes. Each node returns a
partial dict; LangGraph merges it in. Fields annotated with a reducer (like
``add_messages``) are *appended* rather than *overwritten*.
"""
from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class Step(TypedDict):
    """One unit of the research plan."""
    id: int
    description: str
    agent: str          # "researcher" | "coder"
    done: bool
    result: str


class DeerState(TypedDict):
    """The single source of truth that flows through the graph."""
    task: str                              # the user's original request
    messages: Annotated[list, add_messages]  # running chat log (append-only)
    plan: list[Step]                       # the (possibly human-edited) plan
    plan_approved: bool                    # gate set by the human_feedback node
    cursor: int                            # index of the step being executed
    observations: list[str]                # evidence accumulated by the team
    final_report: str                      # filled in by the reporter node
