# Quality Gate Health And Cost Review

## Scope

Review the remaining `quality` gate health work before moving to other skills:

- catalog/index drift prevention
- exact-prose test coupling
- standing gate health, cost, and parallelization posture

## Current Gates

- `plan_quality_run.py --json` emits three gate packets:
  `read-only-quality`, `runtime-summary`, and `skill-ergonomics`.
- `./scripts/run-quality.sh --read-only` remains the broad deterministic proof
  packet. It is intentionally serial-critical at the packet level; internally
  it batches independent checks between `flush_phase` barriers.
- `render_runtime_summary.py --json` is the cheap measurement packet and is the
  correct source for speed claims.
- `inventory_skill_ergonomics.py --json` is an advisory packet with expected
  false positives and false negatives.

## Runtime Signals

Measured through `render_runtime_summary.py --json` on
`local-linux-x86_64-36cpu`:

- `run-quality-read-only`: latest 38.1s, median 65.7s, max 73.6s
- `check-coverage`: latest 29.9s, median 19.5s, budget 55.0s
- `pytest`: latest 24.3s, median 23.5s, budget 140.0s
- `check-duplicates`: latest 10.0s, median 11.9s, unbudgeted historical signal
- `check-markdown`: latest 4.7s, median 4.8s, budget 11.0s

The old "10+ minute" concern is not what current local samples show. Current
samples put the broad read-only packet around one minute median on this machine,
with `check-coverage` and `pytest` as the dominant internal costs.

## Healthy

- `check_runtime_budget.py` is already enforcing budgeted internal hot spots for
  this profile; current budgeted entries pass.
- The standing gate exposes phase labels and elapsed time, and replays advisory
  attention lines from passing commands.
- The new `validate_quality_reference_catalog.py` catches the actual
  catalog/index drift class that let human-visible references be absent from the
  planner.
- The exact-prose coupling touched by the quality compression is now reduced:
  the quality prose-pin precheck reports clean for the changed quality surfaces.

## Weak

- The top-level `run-quality-read-only` packet was unbudgeted despite being the
  main operator-facing cost signal. This slice adds a default 120s budget and a
  `local-linux-x86_64-36cpu` 90s budget so a future total-cost regression is
  visible.
- `check-duplicates` appears as an unbudgeted historical hotspot label. The
  current broad gate now uses `doc-duplicates` and `dup-ratchet`; do not add a
  budget until a fresh current label proves it is still active.
- Some exact-ish tests remain outside the directly changed quality surfaces.
  They are not current blockers, but future skill compression should continue
  moving duplicated prose checks toward producer constants, validators, or
  catalog/schema checks.

## Missing

- No automated scheduler consumes `parallel_group` yet. For now it is judgment
  metadata for agents; executable orchestration would need command
  applicability, env expansion, dependencies, and failure aggregation.
- No catalog/index parity validator existed before this slice. It now exists
  and runs in `run-quality`; it is also pulled to commit-time for quality
  reference/catalog edits.

## Advisory

- `read-only-quality` should stay broad and serial-critical until a smaller
  packet proves the same release/blocking confidence. Moving it off local would
  violate maintainer-local proof unless CI or another independent channel fully
  reruns the same proof.
- `skill-ergonomics` should stay advisory. Its findings are useful pressure
  signals, but false positives/false negatives are expected.

## Delegated Review

Not executed for this narrow gate-health review artifact. The previous
quality-catalog closeout used three bounded reviewers plus a counterweight; this
slice's new code path is small and deterministic, and closeout critique should
focus on the combined validator/test/budget changes.

## Recommended Next Gates

- active AUTO_EXISTING: keep `validate_quality_reference_catalog.py` in both
  `run-quality` and the commit-time structural sweep for quality reference
  edits.
- active AUTO_EXISTING: keep `run-quality-read-only` budgeted in
  `.agents/quality-adapter.yaml`; revisit if median exceeds 90s on
  `local-linux-x86_64-36cpu`.
- passive AUTO_CANDIDATE: if `check-duplicates` appears again under a current
  run-quality label, rename or retire the stale signal before adding a budget.
- passive AUTO_CANDIDATE: consider executable gate scheduling only after a
  separate design proves `parallel_group` can be evaluated without turning the
  skill catalog into a fragile shell runner.

## Commands Run

- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --runtime-profile local-linux-x86_64-36cpu`
- `python3 scripts/check_timing_layer_completeness.py --repo-root .`
- `python3 scripts/validate_quality_reference_catalog.py --repo-root .`
- `python3 scripts/check_prose_pin.py --repo-root . --paths skills/public/quality/SKILL.md skills/public/quality/references/maintainer-local-enforcement.md --json`
- `python3 -m pytest -q tests/quality_gates/test_quality_run_planner.py tests/quality_gates/test_staged_commit_gate_plan.py`
