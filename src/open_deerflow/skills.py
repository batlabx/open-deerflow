"""Skills = versioned Markdown playbooks that agents load at runtime.

Why is a skill NOT a tool?
  * A tool has an API boundary and side effects: you *call* it and get a typed
    value back (search results, code output). The model must not know its
    internals.
  * A skill has no API and no side effects. It is *knowledge* — how to write a
    report, how to structure a debate — that shapes the model's reasoning. You
    can rewrite a skill in a text editor without touching a line of Python.

Keeping skills as plain Markdown means a domain expert (not an engineer) can
improve the system's behaviour by editing prose, and changes are diffable in
git like any other content.
"""
from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def load_skill(name: str) -> str:
    """Return the text of skills/<name>.md."""
    path = SKILLS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"No such skill: {name} ({path})")
    return path.read_text(encoding="utf-8")


def list_skills() -> list[str]:
    return sorted(p.stem for p in SKILLS_DIR.glob("*.md"))
