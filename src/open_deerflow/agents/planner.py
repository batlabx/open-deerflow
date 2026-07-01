"""Planner node — turns a task into a typed, agent-assignable plan.

We use the LLM's *structured output* so the plan comes back as validated
Pydantic objects, not free text we have to parse. Each step is tagged with the
agent that should run it.
"""
from __future__ import annotations

from langgraph.types import Command
from pydantic import BaseModel, Field

from ..config import CONFIG, get_llm
from ..prompts import PLANNER_PROMPT


class PlanStep(BaseModel):
    description: str = Field(..., description="What to do in this step")
    agent: str = Field(..., description="'researcher' or 'coder'")


class PlanOut(BaseModel):
    steps: list[PlanStep]


def planner(state) -> Command:
    llm = get_llm("reasoning").with_structured_output(PlanOut)
    out: PlanOut = llm.invoke(
        PLANNER_PROMPT.format(task=state["task"], k=CONFIG.max_plan_steps)
    )

    plan = [
        {"id": i, "description": s.description,
         "agent": "coder" if s.agent.strip().lower() == "coder" else "researcher",
         "done": False, "result": ""}
        for i, s in enumerate(out.steps)
    ]
    return Command(goto="human_feedback", update={"plan": plan})
