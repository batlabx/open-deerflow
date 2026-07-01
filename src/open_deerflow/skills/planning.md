# Skill: Research Planning

Guidance the `planner` agent can load to shape how it decomposes a task. Kept as
a **skill** (editable Markdown) because "what makes a good plan" is domain
knowledge a non-engineer should be able to tune.

## Principles

- **Minimal steps.** Prefer the fewest steps that fully cover the task. Merge
  anything that one agent could do in a single pass.
- **One owner per step.** Every step is either `researcher` (gather/cite) or
  `coder` (compute/analyse). If a step needs both, split it.
- **Dependencies flow downward.** Later steps may rely on earlier results;
  never the reverse.
- **End analytical, not exhaustive.** The last step should synthesise or
  compute the actual answer, not just "gather more".

## Anti-patterns

- A step that says "research everything about X" (too broad — split it).
- A `coder` step with no data to operate on (schedule the `researcher` first).
- More than ~6 steps (usually a sign the task should be narrowed).
