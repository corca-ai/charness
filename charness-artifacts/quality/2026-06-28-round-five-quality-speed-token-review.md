# Quality Review
Date: 2026-06-28

## Scope

Target boundary: repo-wide quality posture filtered to the user's focus —
test/script speed and token efficiency (round five). It re-checks whether
standing proof costs admit a new high-leverage active move post round-four/#406.

Ambient repo findings: two production scripts in the Python length warn band
(`run_slice_closeout.py`, `nose_report_lib.py`) and 3 new #406 doc-duplicate
template families; both from broad gates, neither a speed finding. No gate failed.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed: 79 phases, 0 failed, 40.1s
  total (`pytest` phase 23.2s is the dominant cost).
- `check-boundary-bypass-ratchet` passed: 45 candidates, **0 clean-convertible**,
  31 internally-spawning, 23 likely keep-boundary (no_increase policy holds).
- `check-runtime-budget`, `dup-ratchet`, `inventory-ci-local-gate-parity`,
  `measure-startup-probes`, and `doc-duplicates` (advisory, exit 0) all passed.
- `check-python-lengths` passed with 2 advisory warn-band files (exit 0).

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median, budget
  90.0s; `pytest` 22.6s latest / 22.8s median, budget 140.0s; `check-coverage`
  5.3s; `check-markdown` 5.1s; `specdown` 3.2s. No gate is over budget.
- coverage gate: read-only gate passed; changed-line mutation + test-completeness
  phases passed inside it.
- evaluator depth: deterministic-gates-only; no Cautilus run claimed (the
  eval-only/ask-before-run contract was not triggered for a speed/token review).

## Healthy

- The subprocess-fanout test surface is harvested: the boundary-bypass ratchet
  reports 0 clean-convertible candidates, and Reviewer A confirmed the 20 tests
  with clean in-process targets are correctly `keep-boundary` (they assert
  exit-code/stderr contracts, not importable logic) — no hidden speed conversion.
- Every standing gate is within budget; gate-verbosity inventory all healthy/quiet
  (token-cheap to read on green).
- Skill ergonomics: `checked_skill_count`=24, `finding_status`=heuristics_present,
  `heuristic_finding_count`=17 all in `host_surface_reference_count`=92 (intentional
  adapter structure); `prose_review_status`=required is recorded below.

## Weak

- `pytest`/nested-CLI fanout (`nested_cli_file_count`=147 of `test_file_count`=348,
  `nested_cli_standing_or_mixed_file_count`=146) is still the dominant local proof
  cost — budgeted and ratchet-guarded, not a defect; the one speed lever left.
- #406 left 3 doc-duplicate template families visible (advisory, not baselined);
  useful as a drift signal, not yet dispositioned by their owner.

## Missing

- No missing speed/token gate for this scope: the concern is owned by runtime
  budgets, the boundary-bypass ratchet, length warn bands, and the
  verbosity/CI-recoverable inventories.
- Latent (not promoted): the achieve↔handoff shared goal-artifact template is
  intentional duplication with advisory drift detection but no hard consistency
  gate; per floor-addition-restraint this stays describe-first, not a new floor.

## Deferred

- Nested-CLI / test-file consolidation remains a later runtime slice; no
  convertible candidate exists today, so it is a watch, not an action.
- `check-markdown` (~5s) is the only CI-recoverable gate (see passive move #3).

## Advisory

- structural review result: command: `plan_quality_run.py --repo-root . --json`.
  capability_needed = keep standing test/script proof fast and token-cheap; it is
  currently STRONG (gates above own it), so the honest move set is defer-watch,
  not a new gate. sequencing lens unused (order does not affect correctness).
  current_centers = budgets + boundary-bypass ratchet + length warn bands +
  verbosity/CI-recoverable inventories, all holding. authoring_form_relevance:
  ambient/non-claim — no helper-ownership, core-overfill, or dogfood gap.
- prose review result: artifact: this file. `quality` still routes correctly;
  target (speed/token) vs ambient (warn-band scripts, doc families) split is
  explicit; warn-band files are cohesive (Reviewer B agreed), so no trigger or
  progressive-disclosure regression; `quality` dogfood stays satisfied.
- length review result: command: `check_python_lengths.py --repo-root .`;
  `run_slice_closeout.py` 455/[432,480] and `nose_report_lib.py` 330/[330,360]
  are cohesive (closeout orchestrator; nose-report pipeline), not grab-bags —
  defer-watch, split only on creep toward the hard limit.
- duplicate review result: artifact: `doc-nose-baseline.json` (28 accepted); the
  3 new families are intentional shared template across two independently-portable
  skills plus a roundtrip fixture — keep-with-fence, owner-dispositioned here.

## Delegated Review

- Delegated Review: executed — two bounded fresh-eye reviewers via the host
  Agent (Explore) tool, parent-delegated, distinct named lenses (speed-harvest;
  disposition/over-reach); requested tier `high-leverage`, host-defaulted (no
  model-override fields sent). Reviewer A: refutation FAILED — the "no active
  speed move" verdict survives, evidence confirmed correct. Reviewer B: agreed
  both warn-band files are cohesive (defer-watch honest), DISAGREED with
  opportunistically re-baselining the doc-nose families in a test-speed run —
  adopted; no baseline mutation this turn.
- Slow-gate lenses: Reviewer A covered duplicated-proof and parallel-critical-path
  (neither found); fixture-economics covered by the test-economics inventory +
  temp footprint (~0.88 MB, healthy). No slow standing gate is moved/weakened, so
  no further slow-gate re-delegation.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_standing_gate_verbosity.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_ci_recoverable_gates.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 scripts/inventory_boundary_bypass.py --repo-root . --summary`
- `python3 scripts/check_python_lengths.py --repo-root .`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Quality Moves

- passive watch nested-CLI/test-file growth because no clean-convertible candidate
  exists today (verified 0) — capability_needed=fast standing proof;
  next_center=boundary-bypass ratchet; transformation=convert a test in-process
  only when a future change makes behavior importable below the boundary;
  proof_boundary=ratchet stays no-increase; enforcement_posture=no-gate.
- passive owner-disposition the 3 doc-duplicate template families until an
  achieve/handoff-scoped pass owns them — capability_needed=honest single-source
  vs portable copy; next_center=doc-nose baseline; transformation=accept with a
  policy note or add a consistency gate; proof_boundary=drift advisory or fix-mode
  gate; enforcement_posture=describe-first (out of scope to silence here).
- passive revisit `check-markdown` local placement until a larger runtime slice
  lands — capability_needed=cheaper local bar; next_center=CI-recoverable
  inventory; transformation=move off local then; proof_boundary=CI mirror;
  enforcement_posture=no-gate (~5s savings < parity risk today).

## History

- [round four quality speed/token review](2026-06-27-round-four-quality-speed-token-review.md)
- [retro skill quality review](history/2026-06-25-retro-skill-quality-review.md)
