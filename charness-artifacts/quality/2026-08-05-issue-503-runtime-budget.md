# Quality Review
Date: 2026-08-05
Title: Issue #503 runtime budget owner decision

## Scope

Target boundary: the local runtime-budget contract and recurring closeout-cost
ownership raised by #503. The selected seam is the local pytest budget for
`local-linux-x86_64-36cpu`, plus the owner/decision record for over-slice cost.

Ambient repo findings: release and aggregate runtime signals remain visible but
are not optimized or re-budgeted by this slice; no unrelated gate was changed.

## Current Gates

- `check_runtime_budget.py --summary` is OK after the measured pytest retune:
  27 checked labels are OK, with no violations or profile errors.
- The pre-push runtime gate remains active. The old 58500ms pytest bar refused
  a valid carrier; the new bar is evidence-based, not a bypass.
- No test, runner, mutation lane, or coverage floor changed.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->,
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: the target pytest cohort has latest 60356ms, median
  61816ms, and max 69353ms across 20 recent samples; the helper derives
  97500ms at 1.4x the max. The broader latest summary ranks
  `run-quality-full-release` at 167982ms and `run-quality-read-only` at
  135071ms, but neither is retuned here.
- coverage gate: unchanged; no coverage or mutation result is claimed by this
  runtime-policy slice.
- evaluator depth: deterministic gates only; no Cautilus run or live-agent
  behavior claim is in scope.

## Healthy

- The budget helper and the checked-in adapter agree on the selected profile;
  the configured 97500ms bar remains below 2x the 61816ms median.
- `quality` owns runtime telemetry and budget records, including the standing
  quality-suite and release-bundle dispositions. `achieve` owns the goal-level
  over-slice response. This preserves the distinction between gate cost and
  goal-boundary cost without leaving any recurring class ownerless.

## Weak

- Runtime telemetry is local-machine evidence and cannot distinguish a stable
  proof cost from cache or host contention without a matched experiment.
- Existing aggregate/release bars contain deliberate historical range policy;
  this slice records `quality` as owner, retains the current bars, and sends
  their matched-cost decision to #505 rather than pretending one pytest retune
  explains them.

## Missing

- No remote CI, installed-host, provider, or GitHub issue readback is established
  by this quality artifact.
- No matched before/after runner experiment exists for the recurring over-slice,
  standing quality-suite, or release-bundle signals; `quality` owns the runtime
  record and #505 owns the next experiment boundary.

## Deferred

- Parallelism, batching, CI relocation, and proof-runner optimization are
  deferred until the final runner shape is measured under #505. The current
  `run-quality-read-only` slack finding is intentionally retained under
  `quality` ownership; the `run-quality-full-release` latest spike is advisory
  and is also a #505 remeasurement input, not a one-sample retune trigger.
- Per-label slack policy for broad aggregate bars remains a separate deferred
  decision; #503 records its owner rather than silently expanding this slice.

## Advisory

- structural review result (command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`): the existing runtime-budget gate is the smallest
  enforcement surface for this observation; no new floor is justified (command:
  `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`).
- prose review result (artifact: `docs/deferred-decisions.md`): the adapter's historical 58500ms explanation is preserved
  as history and a dated #503 correction names the new cohort, derivation, and
  owner; stale D43 wording was corrected.
- The helper's `--suggest-budgets` output is a starting point, not a verdict
  (command: `check_runtime_budget.py --suggest-budgets`);
  the 97500ms value was reviewed against the whole current cohort and the 2x
  regression restraint.

## Delegated Review

- Delegated Review: executed — an unnamed bounded fresh-eye reviewer inspected
  the adapter, current cohort, helper derivation, owner split, and aggregate
  relationship; its findings and any repair are recorded in the bound critique.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): applied as review questions; the proposal changes one
  measured threshold and adds no test or proof path.

## Commands Run

- `issue_tool.py read --repo corca-ai/charness --number 503`
- `check_runtime_budget.py --runtime-profile local-linux-x86_64-36cpu --summary`
- `check_runtime_budget.py --runtime-profile local-linux-x86_64-36cpu --suggest-budgets`
- `render_runtime_summary.py --repo-root . --detail`
- `plan_quality_run.py --repo-root . --detail`
- `resolve_subagent_delegation.py resolve --repo-root . --scope quality`
- `measure_inventory_consumption_floor.py --repo-root . --json`
- `measure_inventory_marker_rule.py --repo-root . --json` and `--recursive --json`
- `pytest -q tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py tests/test_inventory_marker_rule_measurement.py` — 60 passed.
- `check_spec_evidence_durability.py --repo-root . --require-git-file-listing`

## Recommended Next Quality Moves

- active retain the measured pytest budget and explicit quality/achieve owner
  split; capability_needed=actionable recurring-cost ownership; next_center=the
  adapter plus goal slice ledger; transformation=refresh from a new cohort;
  proof_boundary=runtime summary, budget gate, and issue carrier;
  enforcement_posture=existing-gate-reuse.
- passive defer runner optimization until #505 because the final matched command
  shape is not fixed; capability_needed=matched cost attribution; next_center=
  final runner experiment; transformation=measure before changing execution;
  proof_boundary=unchanged failure visibility and full-command timing;
  enforcement_posture=no-gate because the optimization premise is unproven.

## History

- [prior quality review](history/2026-07-19-portable-proof-path-learning-review.md)
