# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v0.36.0`. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`)
- The operator-selected next queue, four independent per-slice-closed-out slices: (1) `run_slice_closeout.py --base` committed-range ergonomics; (2) the #N-anchor edit-time guard auto-firing via the adapter-declared host-hook machinery; (3) light push/tag CI + the CI-PR changed-line mutation mirror; (4) the source-guard timing audit with the favorable subset pulled to commit time and the `docs/conventions/validator-timing-layers.md` doctrine. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`; sources: 22)
- **W1 — slice-2 escape paid two slices later (~25 min).** The `skill_anchor_edit_guard` adapter section passed commit-time `validate-adapters` but violated the usage-episodes integration's `additionalProperties: false` jsonschema; the usage-episode emitter failed with `invalid_adapter`, surfaced only by slice 4's wider test run and fixed forward in `72f74b7f` plus a wasted full producer run that died at the surface-match block. Root cause: an adapter file has two validation owners and only the weaker one runs at the commit boundary. Filed as #342 with a timing-pull destination. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- **W2 — parity watchdog fired at the bundle, two slices after the workflow was authored (~12 min producer re-run).** `quality-core.yml` was authored in slice 3; the CI/local-gate parity watchdog (`test_real_repo_workflows_or_zero_parity_issues`) only fired inside the bundle's instrumented broad pytest. Resolution used the doctrine's own extension path (`local-gate-subset-mirror` policy). The structural fix is a slice-4-class timing pull: workflow edits now run the parity inventory with `--require-canonical-gate-match` at commit time (applied this session). (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- **W3 — producer DISCOVERED four uncovered changed lines at the boundary (~10 min re-run), the standing recent-lessons repeat trap.** Slices 1–2 added branch tests per the carried lesson, but the reconcile `HostHookError` branch, the non-dict-payload fail-open return, and the guard's `__main__` process entry were missed; the consumer flagged them and one more producer run was paid. Partial improvement over prior sessions (4 lines vs 7/85), still discovery rather than confirmation. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`; sources: 22)
- I1 — adapter-vs-integration-schema commit-time validation gap: `issue #342`. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- I2 — host-hook lifecycle robustness (dangling-checkout noise, one-logical- hook-per-machine coverage gap, reconcile fan-out registry refactor before a fourth hook): `issue #343`. (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
- I3 — coverage confirm-not-discover (W3): applied — in-process branch tests + one ratchet-exempted subprocess proof for the guard's stdin/exit-code contract (`2bbd8a40`), and the re-run producer + consumer confirmed green; the recurring class stays a recent-lessons repeat trap (recurrence noted, trend improving: 4 lines this run vs 7 prior). (source: `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)

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
- `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
