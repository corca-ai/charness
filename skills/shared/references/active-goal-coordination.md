# Active Goal Coordination (Shared)

`impl` and `issue` cite this reference directly because they read and write the
goal artifact during a run; `achieve` reads it to coordinate `quality` and
`critique` cadence (the sections below cover all four). The point is that a
long-running autonomous run behaves consistently across the workflow skills
instead of each skill re-deriving how to treat a live goal. The behavior is
prompt-enforced through these skills' own discipline, not gate-enforced.

## When This Applies

This step is **presence-gated**. It applies only when an active `achieve` goal
artifact exists for the current work — a file under
`<repo-root>/charness-artifacts/goals/<yyyy-mm-dd-slug>.md` whose `Status:` line
reads `active`. With no active goal artifact, every rule below is a **silent
no-op**: do not create a goal artifact, do not mention a missing one, and keep
the standalone skill behavior unchanged. The guidance here is generally useful;
it must not turn into an `achieve`-only branch that degrades the standalone
skill.

The goal artifact and its helper scripts are owned by the `achieve` public skill;
this reference only describes how the coordinated skills read and append to it.

## Per-Skill Behavior

### impl

- Treat the active goal artifact as the slice memory surface. Do not update
  `handoff` during every slice while a goal is active.
- Before a substantial slice, state the slice objective and expected evidence.
- After the slice, append concise evidence with `achieve`'s
  `append_slice_log.py` (commits, targeted verification, critique, lessons)
  rather than narrating it only in chat.
- Use targeted deterministic checks per commit or small change. Reserve broad
  gates for bundle or final boundaries unless the change warrants them now.

### quality

- Design verification before the run starts; record the plan in the goal
  artifact's `Agent Verification Plan`.
- Run cheap targeted checks during slices.
- Run broader quality gates near final completion or bundle boundaries.
- Preserve high-cost, live, or provider checks for the point where the result is
  stable enough to justify them.
- Record the final confidence level and residual risks in the goal artifact's
  `Final Verification` when one is active.

### critique

- Critique the goal plan before activation.
- Critique each substantial slice, not every tiny commit.
- Critique the final proof and user verification instructions before completion.
- Feed lessons forward into the goal artifact so a compacted context keeps the
  findings.

### issue

- If a finding is not required for the current goal, file or defer it through
  `issue` instead of silently expanding the active goal.
- Append only the issue reference and the reason to the goal artifact's
  `Off-Goal Findings` section.
- A local fix being possible is not a reason to grow the goal's scope.
