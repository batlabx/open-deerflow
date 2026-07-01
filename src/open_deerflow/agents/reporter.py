"""Reporter node — synthesises the final, cited report.

Notice what it does NOT do: it calls no tools. Its behaviour is governed by a
*skill* (``skills/report_writing.md``) that is loaded at runtime and injected
into the prompt. Change the house style by editing Markdown — no code change.
"""
from __future__ import annotations

from langgraph.graph import END
from langgraph.types import Command

from ..config import get_llm
from ..prompts import REPORTER_PROMPT
from ..skills import load_skill


def reporter(state) -> Command:
    llm = get_llm("reasoning")
    evidence = "\n\n---\n\n".join(state["observations"]) or "(no evidence gathered)"

    prompt = REPORTER_PROMPT.format(
        skill=load_skill("report_writing"),  # the editable playbook
        task=state["task"],
        evidence=evidence,
    )
    report = llm.invoke(prompt).content

    return Command(goto=END, update={"final_report": report})
