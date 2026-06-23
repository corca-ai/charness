# Quality Review
Date: 2026-06-23

## Scope

Operator-requested review after #397/#398: inspect whether the `quality` skill's
deterministic gates are healthy, necessary, correctly layered, and whether the
scripts give agents useful next-review/action packets instead of only terminal
green.

No Cautilus evaluator run was performed:
`python3 scripts/plan_cautilus_proof.py --repo-root . --json` returned
`next_action: "none"` and `must_ask_before_running: true`.

## Current Gates

- Full read-only quality:
  `./scripts/run-quality.sh --read-only`: **78 passed, 0 failed, total 38.7s**.
- Maintainer-local enforcement: **healthy**. `.githooks/pre-push` runs the
  read-only quality gate; this review reran `./scripts/run-quality.sh --read-only`.
- CI/local posture: **intentional single-maintainer local-first**. PR CI does not
  mirror the full gate by policy; only `check-markdown` is CI-recoverable.
- Clone advisory baseline: refreshed
  [nose-baseline.json](./nose-baseline.json) from nose 0.14.0 ids to the
  live nose 0.15.0 set. Follow-up inventory returned clean drift after accepting
  **534** current families: `version_skew: null`, `family_count: 0`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` **38.1s latest / 65.7s median**
  unbudgeted; `check-coverage` **29.9s latest / 19.5s median**, budget **55.0s**;
  `pytest` **23.0s latest / 23.6s median**, budget **140.0s**; `check-duplicates`
  **10.0s latest / 11.9s median** unbudgeted; `check-markdown` **4.8s median**,
  budget **11.0s**.
- coverage gate: full read-only quality passed; `check-coverage` is budgeted and
  under budget.
- evaluator depth: deterministic gates only; Cautilus planner said no evaluator
  proof was required.
- test economics: `test_file_count: 323`, `nested_cli_file_count: 10`, plus a
  **2.86GB** retained pytest temp footprint; cleanup signal, not a removal reason.

## Healthy

- `run-quality.sh` is correctly structured as a report-first packet: per-phase
  labels, elapsed time, advisory output, and a verbose escape hatch are present.
- Expensive gates that carry real confidence (`pytest`, `check-coverage`,
  `check-duplicates`) are **keep-local** today because CI does not fully rerun
  their proof.
- `validate-cautilus-diagnostics` is now healthy as a deterministic diagnostic
  artifact floor; it validates all current diagnostic bundles in `--all` mode.

## Weak

- `run-quality-read-only` and `check-duplicates` are unbudgeted aggregate hot
  spots. Existing per-label budgets cover the dominant child phases, but the
  aggregate and duplicate-scan advisory still lack explicit budget posture.
- `inventory_nose_clones` was noisy until this slice because the advisory
  baseline used nose 0.14.0 ids while the active scanner is 0.15.0.
- Skill ergonomics fields: `scope_status: scanned`, `finding_status:
  heuristics_present`, `prose_review_status: inventory-only`;
  `host_surface_reference_count: 96` is portability review material, not failure.
- prose review result: not performed; this pass did not adjudicate each
  host-surface reference.

## Missing

- No new blocking gate is justified by this review.
- There is no current CI backstop for moving `pytest`, `check-coverage`, or
  `check-duplicates` off the local/pre-push path. That is intentional under the
  current maintainer model, but it means speed optimization should preserve
  local proof.

## Deferred

- Do not move `check-markdown` off local only because CI can rerun it; at **4.8s**
  median, the tradeoff is not worth another split unless local wall-clock
  pressure rises.
- Do not weaken `pytest` or `check-coverage` to chase runtime. If they need a
  speed slice, reduce duplicated fixture/process work or split repeated contract
  proof below the CLI boundary.
- Structural waste: `command_snippet_count: 12`, `python_source_count: 261`,
  `broad_scanner_candidates: 1`; prefilter `check_test_repo_copy_invariants.py`
  when that gate becomes hot or is edited.

## Advisory

- command: `inventory_nose_clones.py --json` now reports clean drift; do not treat
  accepted clone count or `total_dup_lines` as a reduction target.
- command: `inventory_standing_test_economics.py --json` reports nested CLI
  fanout and temp footprint as advisory, not a gate-removal reason.
- command: `inventory_skill_ergonomics.py --json` reports 96 host-surface
  references; this is portability review material, not a failing gate.

## Enforcement Triage

- `AUTO_EXISTING`: hard gates: `run-quality.sh --read-only`, pre-push,
  runtime budgets, changed-line mutation coverage, Cautilus validators; advisory
  packets still need judgment: CI/local parity, skill ergonomics, duplicate scans.
- `AUTO_CANDIDATE`: budget `run-quality-read-only` / `check-duplicates` if drift
  recurs; prefilter `check_test_repo_copy_invariants.py` when hot or edited.
- `NON_AUTOMATABLE`: judge whether host-surface-reference hits are acceptable
  portability boundaries for each skill package; do not automate a blanket
  failure from the count alone.

## Delegated Review

- Delegated Review: executed. Fresh-eye reviewer agreed the immediate actions
  were re-baselining [nose-baseline.json](./nose-baseline.json) and updating this durable artifact.
- Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof.
  Findings: keep `pytest`/`check-coverage` local; defer `check-markdown` move.

## Commands Run

- `python3 skills/public/find-skills/scripts/list_capabilities.py --recommend-for-task ... --summary`.
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`.
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`.
- `./scripts/run-quality.sh --read-only`.
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_standing_gate_verbosity.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_ci_recoverable_gates.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_structural_waste.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline --json`.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`.

## Recommended Next Gates

- active Commit this review and the nose advisory baseline refresh together.
- passive because one more drift observation is needed after the baseline refresh:
  add aggregate runtime budgets for `run-quality-read-only` and `check-duplicates`.
- passive until a specific repeated subprocess contract is touched: review nested
  CLI fanout families, move repeated proof in-process, keep one thin binary smoke.

## History

- [2026-06-16 quality review](./history/2026-06-16-quality-review.md)
