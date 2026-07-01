"""Human-feedback node — the human-in-the-loop plan gate.

``interrupt()`` freezes the graph and hands control back to the caller with a
payload (the proposed plan). The run resumes when the caller sends a
``Command(resume=...)``. Because state is checkpointed, the pause can last
milliseconds or days — the graph simply continues from where it stopped.
"""
from __future__ import annotations

from langgraph.types import Command, interrupt


def human_feedback(state) -> Command:
    decision = interrupt(
        {
            "plan": state["plan"],
            "prompt": "Reply 'accept' to run this plan, or send an edited "
                      "list of steps to replace it.",
        }
    )

    # Accepted as-is.
    if isinstance(decision, str) and decision.strip().lower().startswith("accept"):
        return Command(goto="research_team", update={"plan_approved": True})

    # Otherwise the caller returned an edited plan; adopt it and proceed.
    return Command(
        goto="research_team",
        update={"plan": decision, "plan_approved": True},
    )
