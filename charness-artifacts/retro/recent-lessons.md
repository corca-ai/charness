# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v0.36.0`. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`)
- The activated goal `charness-artifacts/goals/2026-06-10-342-343-adapter-schema-hook-lifecycle-deferred-proofs.md` ran start-to-finish in one session: slice 1 closed #342 (integration-schema validation pulled into `validate_adapters.py`, commit 76909cc8), slice 2 closed #343 (liveness + posture + registry, commit 7f835610, repair f084c875), slice 3 consumed the three deferred proofs read-only (quality-core first remote run GREEN at run 27249353164; the edit-time anchor guard observed BLOCKING a live scratch `PostToolUse` edit; #335 confirmed closed by the github-actions bot marker). (source: `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`; sources: 22)
- **W1 — producer DISCOVERED 3 uncovered changed lines at the bundle boundary (~6.7 min extra instrumented broad-pytest run, per the producer proof record).** The `_import_module` ImportError fallback in the NEW `scripts/host_hook_registry.py`. The carried lesson (cover degrade branches in the introducing slice) WAS applied inside slice 1 (`validate_adapters` ImportError/YAMLError branches covered up front) but missed in slice 2's new module, because the lazy-import fallback only fires when `scripts/` is off `sys.path` — a branch the default in-process test pattern never executes. Trend improving (3 lines vs 4 prior vs 7 before) but still discovery, not confirmation. (source: `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`)
- **W1 — slice-2 escape paid two slices later (~25 min).** The `skill_anchor_edit_guard` adapter section passed commit-time `validate-adapters` but violated the usage-episodes integration's `additionalProperties: false` jsonschema; the usage-episode emitter failed with `invalid_adapter`, surfaced only by slice 4's wider test run and fixed forward in `72f74b7f` plus a wasted full producer run that died at the surface-match block. Root cause: an adapter file has two validation owners and only the weaker one runs at the commit boundary. Filed as #342 with a timing-pull destination. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- **W2 — first cut of slice 1 parsed adapters with the minimal `adapter_lib` parser instead of the runtime owner's `yaml.safe_load`** (~3 min, caught by the slice's own test before commit). Ironic-but-cheap: the slice existed to close a two-owner drift and nearly introduced a two-parser drift; the fidelity rule is now in the slice log and the commit message. (source: `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`; sources: 22)
- I1 — adapter-vs-integration-schema commit-time validation gap: `issue #342`. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- **I1 (workflow/capability): issue #344** — deterministic closeout nudge when a slice adds a new eligible mutation-pool file, naming the early producer self-check, so confirm-not-discover stops depending on recall. (source: `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`)
- I2 — host-hook lifecycle robustness (dangling-checkout noise, one-logical- hook-per-machine coverage gap, reconcile fan-out registry refactor before a fourth hook): `issue #343`. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`
- `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
