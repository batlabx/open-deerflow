"""CLI entry point.

    python -m open_deerflow.main "Compare the top 3 open-source vector DBs in 2026"

The run pauses at the plan gate, prints the plan, auto-accepts it (swap this for
real input in a UI), then streams the research/analysis loop and prints the
final report. State is checkpointed to SQLite so an interrupted run resumes.
"""
from __future__ import annotations

import argparse
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from .config import CONFIG
from .graph import build_graph


def _fmt(event: dict) -> str:
    node = next(iter(event))
    return f"· {node}"


def run(task: str, auto_accept: bool = True) -> str:
    conn = sqlite3.connect(CONFIG.checkpoint_db, check_same_thread=False)
    graph = build_graph(SqliteSaver(conn))
    cfg = {"configurable": {"thread_id": "cli-session"}}

    # 1) Run until the human_feedback interrupt fires.
    for event in graph.stream({"task": task, "observations": [], "messages": []}, cfg):
        print(_fmt(event))

    snapshot = graph.get_state(cfg)
    print("\nProposed plan:")
    for step in snapshot.values.get("plan", []):
        print(f"  [{step['agent']:>10}] {step['description']}")

    decision = "accept" if auto_accept else input("\naccept / edit > ") or "accept"

    # 2) Resume from the interrupt with the human's decision.
    for event in graph.stream(Command(resume=decision), cfg):
        print(_fmt(event))

    report = graph.get_state(cfg).values["final_report"]
    print("\n===== FINAL REPORT =====\n")
    print(report)
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Open-DeerFlow research agent")
    ap.add_argument("task", help="the research task to run")
    ap.add_argument("--interactive", action="store_true",
                    help="prompt to accept/edit the plan instead of auto-accepting")
    args = ap.parse_args()
    run(args.task, auto_accept=not args.interactive)


if __name__ == "__main__":
    main()
