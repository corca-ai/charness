# Skill Migration Map

This document records how the original Ceal-centered skill set mapped into the
current `charness` taxonomy and what remains intentionally outside the core
public skill surface.

It is a durable memory surface for migration intent, not a historical diary.

## Current Destination Map

| Source surface | Current `charness` destination | Status |
| --- | --- | --- |
| `gather` | `skills/public/gather` | landed |
| `interview` | absorbed into `skills/public/ideation` | landed |
| `concept-review` | absorbed into `skills/public/quality` concept lens | landed |
| `test-improvement` | absorbed into `skills/public/quality` concept lens | landed |
| `impl` | `skills/public/impl` | landed |
| `expert-debugging` | `skills/public/debug` | landed |
| `retro` | `skills/public/retro` with `session` / `weekly` modes | landed |
| `handoff` | `skills/public/handoff` | landed |
| `announcement` | `skills/public/announcement` | landed |
| `create-skill` | `skills/public/create-skill` | landed |
| `find-skills` | `skills/public/find-skills` | landed |
| `hitl` | collaboration profile public skill | landed |
| `agent-browser` | external integration plus support consumption policy | landed as integration surface |
| `specdown` | external integration plus support consumption policy | landed as integration surface |
| `web-fetch` | support skill target | still open |
| `workbench` evaluator shell | extracted external evaluator path via `cautilus` | in progress |

## Fixed Migration Decisions

- `quality` is one public skill rather than separate `concept-review` and
  `test-improvement` skills.
- `ideation` replaces and absorbs `interview`.
- `retro` stays one public skill with modes instead of split skills.
- `hitl` belongs to the collaboration profile, not the constitutional core.
- `workbench` is not a long-term `charness` public skill; generic evaluator
  depth belongs in `cautilus`.
- external binaries and upstream-maintained tool surfaces should be consumed
  through integration manifests and support policy, not copied into public
  skill bodies.

## Still Open

- finish the `cautilus` integration contract in `charness`
- decide whether `web-fetch` should land as a first-class support skill or stay
  deferred behind other support/runtime priorities
- keep checking whether any host-specific provider helper should become a true
  `skills/support/*` package instead of living only as an external integration

## Guardrails

- Do not reintroduce Ceal-specific runtime paths, prompts, or delivery
  channels into public skill bodies.
- Do not split one public concept into multiple public skills unless the user
  need is truly different, not just a mode or adapter seam.
- Do not move host policy into `charness` just because the first consumer
  needed it once.
