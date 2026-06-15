# Quality Review
Date: 2026-06-15

## Scope

Operator-requested `charness:quality` pass with autonomous repair. Routing:
`find-skills` -> `quality`. Scope covered current gates, skill/docs/runtime/test
economics inventories, maintainer-local enforcement, CI/local parity, plugin
mirror sync, and one repo-owned structural fix. The implemented slice preserves
the public planner module API while moving private helper families to
`scripts/staged_commit_gate_plan_helpers.py`.

## Current Gates

- `./scripts/run-quality.sh --read-only`: **77 passed, 0 failed, 45.8s**.
- Focused repair proof: `pytest -q tests/quality_gates/test_staged_commit_gate_plan.py
  tests/quality_gates/test_closeout_headroom_and_mirror_gate.py`: **53 passed**.
- Packaging/export sync: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
  reported `plugins/charness` plus marketplace paths; only mirror copies remain
  in the diff.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 65.7s latest / 66.6s median;
  `check-coverage` 47.1s / 46.6s vs 55.0s; `pytest` 22.5s / 22.1s vs 140.0s;
  `check-duplicates` 10.0s / 11.9s.
- coverage gate: read-only quality pass ran green; no coverage-floor failure.
- evaluator depth: deterministic gates only; no log-backed behavior failure or
  Cautilus planner-triggering request was present.

## Healthy

- All standing read-only quality phases passed.
- CLI ergonomics, CLI side-effect probe contracts, CI/local parity, attention
  visibility, usage episode validation, public spec inventory, and package sync
  checks were healthy.
- Maintainer-local enforcement is present through checked-in `.githooks/pre-push`
  plus the `run-quality --read-only` policy in `docs/conventions/operating-contract.md`.
- `check_changed_surfaces.py` mapped this slice to repo-python, checked-in plugin
  export, integrations/control-plane, and python-scan-hygiene surfaces; planned
  sync/verify commands were followed.

## Weak

- `report_usage_episodes.py`: usage episodes remain engineering signal only:
  feedback coverage 0.0%, no satisfaction signal, single emitter, single trigger
  type, and explicit request only.
- `inventory_skill_ergonomics.py --json`: gate-clean but 17 advisory findings,
  mostly host-surface references; explicit prose review remains required.
- `inventory_standing_test_economics.py --json`: 309 pytest files, 136 nested
  CLI-spawning test files, and 6.4GB allocated pytest temp retention across 2
  retained sessions; no pruning was safe without a scorecard.

## Missing

- No missing repo-local enforcement was found in this pass.
- `update_tools.py --json` found `defuddle` absent on this machine; that is an
  external-tool readiness advisory, not a repo-local gate failure.

## Deferred

- Product-success instrumentation remains outside this code slice.
- Runtime/test-economics cleanup needs candidate scorecards before edits.
- Broad skill-portability prose review remains a quality follow-up, not a
  deterministic repair.

## Advisory

- `check_python_lengths.py --headroom`: `scripts/staged_commit_gate_plan.py`
  started at 475/480 code lines and was the only clear `AUTO_CANDIDATE`.
- `inventory_ci_recoverable_gates.py --json`: only `check-markdown` matched a
  CI-backed move-off-local candidate, but at 4.6s it is not worth changing.
- `inventory_public_spec_quality.py --json`: 4 specs, no source-guard pressure,
  no duplicate command examples, one smoke path, and one E2E path for review.
- `inventory_nose_clones.py` in the quality gate reported 20 displayed clone
  families / 2002 duplicated lines under nose 0.10.0; interpretation remains
  per-family, not a metric target.
- `inventory_lint_ignores.py --json`: 160 narrow inline `noqa` sites, no blanket
  or file-level ignores; advisory inventory only.

## Delegated Review

- Delegated Review: executed. Bounded fresh-eye reviewer `Herschel`, requested
  high-leverage tier, parent-delegated, read-only shared worktree. Verdict:
  the `staged_commit_gate_plan.py` split was the highest-confidence autonomous
  fix; no smaller safer automatable fix had comparable confidence.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not re-delegated; slow-gate signals were advisory and not edited.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`;
  `bootstrap_adapter.py`; `resolve_quality_artifact.py`; `rg --files .`;
  `git status --short --branch`.
- `./scripts/run-quality.sh --read-only`; `validate_usage_episodes.py`;
  `report_usage_episodes.py`; `validate_attention_state_visibility.py`;
  `render_runtime_summary.py`.
- Inventories: skill ergonomics, CLI ergonomics, entrypoint-doc ergonomics,
  standing-gate verbosity, standing-test economics, CI/local parity,
  CI-recoverable gates, CLI side-effect probes, public spec quality, lint ignores.
- Repair proof: `py_compile`, `ruff check`, focused pytest, headroom check,
  `check_changed_surfaces.py`, `sync_support.py --json`, `update_tools.py --json`,
  `sync_root_plugin_manifests.py`.

## Recommended Next Gates

- active none — the clear repo-owned deterministic repair was implemented in
  this slice.
- passive test-economics consolidation because nested CLI fanout needs a
  candidate scorecard before production/test edits.
- passive skill-portability prose review because host-surface references are
  advisory heuristics, not automatic debt.
- passive product-success instrumentation because usage episodes still do not
  prove satisfaction or feedback.

## History

- [2026-06-12 quality review](history/2026-06-12-quality-review.md)
