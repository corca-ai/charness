# Retro Memory Seam

Seed this only when the repo wants durable retrospective pickup rather than
chat-only retros.

## Goal

Give future sessions one stable place to read the latest recurring traps without
forcing a full retro every time.

## Seeded Files

- `<repo-root>/.agents/retro-adapter.yaml`
- `<repo-root>/charness-artifacts/retro/recent-lessons.md`

## Preferred Path

Use `$SKILL_DIR/scripts/seed_retro_memory.py` to create the initial seam:

```bash
python3 "$SKILL_DIR/scripts/seed_retro_memory.py" --repo-root .
```

This seeds:

- `summary_path: charness-artifacts/retro/recent-lessons.md`
- empty `evidence_paths` and `metrics_commands` that the repo can tighten later
- an expectation that `<repo-root>/AGENTS.md` should list `<repo-root>/charness-artifacts/retro/recent-lessons.md`
  in repo memory when the seam is enabled

## Lesson Loop (separate, explicit opt-in)

The seam above gives a repo durable retro memory. The lesson loop — presenting a
scored lesson list before the work and recording sparse anchored effects at retro
— is a second, separate opt-in. `seed_retro_memory.py` REPORTS its state as
`lesson_loop.state` and creates nothing, because declaring an evaluator turns on a
per-retro disposition duty and that is an operator decision, not a side effect of
running setup.

Four steps get a consuming repo the whole loop:

1. `charness init` (or `charness update` on an existing install) — installs the
   user-level SessionStart hook that presents the lesson list. Already done for
   any repo installed through the charness CLI; the hook command path never
   changes, so an existing install picks up new script content on update with no
   hook reinstall.
2. Have the retro seam above: `<repo-root>/.agents/retro-adapter.yaml` and
   `<repo-root>/charness-artifacts/retro/`.
3. Run the opt-in once: the `lesson_loop.opt_in_command` this script prints
   (`init_lesson_ledger.py`, resolved repo-locally when the repo has its own
   `scripts/`, otherwise from the installed package). Until then the hook injects
   nothing and the retro disposition floor stays inert.
4. Tag at least one retro bullet `recurrence-class: <slug>` and append its seed
   transition. Until a lesson is seeded the preview is empty, session declaration
   refuses, and `not-evaluated / missing-start` remains the only honest
   disposition — an empty ledger makes the lifecycle *reachable*, not *finished*.

A repo that installs charness only through the Claude plugin marketplace, without
ever running the `charness` CLI, gets no SessionStart hook and therefore no
presentation seam. See `<authoring-repo>/docs/host-packaging.md`.

## Guardrails

- keep it opt-in; not every repo needs durable retro memory on day one
- do not seed hidden telemetry or background collection
- prefer one stable digest path over many ad hoc retro summaries
