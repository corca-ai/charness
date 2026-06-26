# Quality Review
Date: 2026-06-26

## Scope

Target paths: `scripts/subprocess_guard.py`,
`scripts/check_skill_surface_preflight.py`, `scripts/check_command_docs.py`,
their checked-in plugin mirrors, `tests/test_subprocess_guard.py`, and
`charness-artifacts/quality/dup-ratchet-baseline.json`.

Ambient repo findings: closeout `run-quality --read-only` failed only
`dup-ratchet` after the two parallel-check slices because new helper-like blocks
rotated/newly surfaced code clone family ids.

## Current Gates

- Ruff passed for the subprocess helper, two consumers, and focused tests.
- Focused subprocess helper, command-docs, and skill-surface preflight tests
  passed.
- Dup-ratchet passed after refactoring the duplicated parallel subprocess pattern
  into the shared helper and refreshing the gate baseline.
- Plugin mirror drift check passed after syncing generated surfaces.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`, plus closeout failure output and
  focused pytest samples from this slice.
- runtime hot spots: focused helper/command-docs/preflight tests passed in
  11.61s; command-docs current-repo test remained 0.37s after helper extraction.
- coverage gate: ruff, focused pytest, dup-ratchet, and staged mirror drift
  passed.
- evaluator depth: deterministic gates only; no evaluator-backed behavior was
  in scope.
- runtime interpretation: the speedups remain, while duplicate-prone
  ThreadPool/subprocess result collection now lives in one helper.

## Healthy

- `run_processes_in_order()` preserves input order and is covered directly.
- The command-docs validator still assembles findings in contract order.
- Skill-surface preflight still reports check rows in configured order.
- Dup-ratchet is clean after the reviewed baseline refresh.

## Weak

- Dup-ratchet family ids are line-offset sensitive; baseline refresh must be read
  as scanner maintenance after inspecting family summaries, not proof that there
  was never duplication pressure.

## Missing

- Missing before this slice: the two speedup slices independently introduced the
  same parallel subprocess collection shape.

## Deferred

- Consider a stricter helper API if more call sites need per-command timeout or
  environment customization.

## Advisory

- failure command: `./scripts/run-quality.sh --read-only` failed
  `dup-ratchet` with 17 new code families before this helper extraction and
  baseline refresh.
- repair command: `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
  passed after `--write-baseline`, reporting no new fixable-eligible families.

## Delegated Review

- Delegated Review: not_applicable — closeout-gate repair with direct failing
  gate reproduction and no behavior-surface expansion.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through dup-ratchet family summaries and focused
  duration samples.

## Commands Run

- `python3 -m ruff check scripts/subprocess_guard.py scripts/check_command_docs.py scripts/check_skill_surface_preflight.py tests/test_subprocess_guard.py`
- `pytest -q tests/test_subprocess_guard.py tests/quality_gates/test_command_docs_gate.py tests/quality_gates/test_skill_surface_preflight.py --durations=12`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline --json`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- `python3 scripts/check_staged_mirror_drift.py --repo-root .`

## Recommended Next Gates

- active because this repaired a closeout failure: rerun `./scripts/run-quality.sh --read-only`.
- passive because publication is next: run release gates before push/release.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
