# Quality Review
Date: 2026-08-14
Title: Current-contract cleanup and runner visibility

## Scope

Target boundary: the current-only lifecycle/receipt cleanup, issue #617 lesson
bundle, lesson ledger schema 5, and lifecycle visibility for long-running runners.

Ambient repo findings: remaining compatibility/grandfather terminology and the
PLR2004 inventory are classified here but do not widen this reviewed slice silently.

## Surface Contract Review

- semantic coverage: observed — exact bundle bytes, receipt commitment, schema
  rejection, completion-order status, heartbeat, failure logs, exit aggregation,
  and final receipts have behavior tests.
- surface: lesson session producer/continuity checker, lesson ledger, reviewed-input
  identity, issue owner inspection, `run-quality`, and slice closeout.
- owner: each producer owns its single current schema; runner parents own lifecycle
  events while child bodies stay isolated.
- projections: session Markdown plus receipt, ledger selection/report, streamed
  status, durable failure logs, and final structured receipt.
- state scope: repository-local artifacts and temporary runner state; no hosted,
  installed, GitHub, or release state is changed.
- transitions: write bundle then stdout then receipt; queue, observe actual child
  completion, emit status/heartbeat, aggregate, and receipt.
- proof boundary: focused tests, source/plugin parity, shell syntax, deterministic
  validators, and bounded fresh-eye review; no live host session or publication claim.
- unexamined axes: hostile concurrent filesystem replacement and live provider behavior.

## Current Gates

- Exact-schema readers reject retired forms rather than dispatching to migrations.
- `run-quality` records child metadata atomically, synthesizes a failure if a child
  exits without metadata, and retains the existing failure-log/final-receipt boundary.
- Plugin generation remains the only source-to-shipped-surface projection.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `skills/public/quality/scripts/render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 229.9s latest / 102.4s median;
  changed-line mutation 219.1s / 71.9s; `run-quality-full` 142.7s / 142.6s.
- coverage gate: focused current-slice suites pass; the targeted changed-line gate
  covers every mapped changed file and explicitly leaves three unmapped pool files
  unproven; final broad gate follows the final commit.
- evaluator depth: deterministic-gates-only; Cautilus is ask-before-run and no live
  semantic evaluator claim is needed for these executable contracts.

## Healthy

- #617 stores the exact human-readable lesson bytes beside the receipt and validates
  the deterministic path, byte count, and digest before accepting the session.
- Current ledger/inspection/identity readers have one accepted schema or algorithm.
- Long-running runner diagnostics no longer trade non-interleaving for a silent
  control plane: start, child start, completion, heartbeat, and final receipt are visible.

## Weak

- Lexical inventory finds 128 production/test files mentioning compatibility,
  grandfathering, deprecation, or migration. Some are active strict refusals or
  historical prose; keyword count is not a safe deletion verdict.
- PLR2004 is not selected. A diagnostic scan reports 990 findings: 181 production
  and 809 tests, too noisy for an unbaselined global blocker.
- Test/production Python line ratio is 1.23, above the advisory 1.00 threshold.

## Missing

- The repo has no shared monitored-capture primitive. Long-running Python
  orchestrators therefore choose between inherited noisy bodies and silent
  `capture_output` ad hoc, and lifecycle formats can drift per runner.

## Deferred

- Historical artifact grandfather removal must be handled by owner cohort: either
  retire the old evidence population or make the validator current-scope-only. A
  blind keyword deletion would turn retained history into broad false reds.

## Advisory

- structural review result: inventory: 230 capture/redirect markers across 147 production
  files are not 147 defects. A timeout/fan-out inspection found 17 capture files
  declaring at least a 60-second timeout and ranks release runners, skill A/B,
  JS mutation, mutant restore, eval fan-out, worktree prepare, and skill-surface
  preflight as monitored-phase candidates. Atomic git/JSON/help probes remain
  legitimate quiet captures.
- prose review result: artifact: implementation discipline now states the repo default
  as isolated child bodies plus streamed lifecycle; no new blocking floor was added.
- command: the PLR2004 JSON inventory and compatibility residue scan are evidence for
  scoped follow-up, not proof that every numeric literal or every word is a defect.

## Delegated Review

- Delegated Review: executed — two high-leverage bounded rounds culminated in
  review-time identity `6647f7…353df`; the repaired-surface round passed 23 focused tests and
  returned no act-before-ship, bundle-anyway, or valid-but-defer finding; artifact:
  `charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  covered by the runner review; completion-order streaming preserves overlap and does
  not replay green bodies.

## Commands Run

- focused runner, continuity, ledger, contract, identity, and closeout suites — pass.
- five owner test modules — 80 pass; targeted changed-line coverage exits 0 with
  mapped coverage complete and three unmapped pool files explicitly unproven.
- `bash -n scripts/run-quality.sh`, `git diff --check`, plugin sync/parity — pass.
- standing-gate verbosity detail, timeout/fan-out capture inventory, PLR2004 JSON
  scan, runtime summary, and ratio advisory.
- reviewer-boundary snapshot/verify — `clean`; critique artifact validator — pass.

## Recommended Next Quality Moves

- active compatibility-owner cohorts — capability_needed=current-state premise scan;
  next_center=goal/artifact validators, quality baselines, release resume, and adapter
  bootstrap; transformation=delete each dual reader plus migration-only tests as one
  owner slice; proof_boundary=current checked-in corpus plus focused refusal tests;
  enforcement_posture=existing-gate-reuse.
- active Python orchestrator visibility — capability_needed=one shared monitored
  execution primitive with an explicit `atomic_capture`/`monitored_phase` caller
  choice; next_center=release publish helpers first because they can swallow the
  child quality runner's own lifecycle for 1,800 seconds, then skill A/B, JS
  mutation, mutant restore, eval fan-out, worktree prepare, and skill-surface
  preflight; transformation=stream compact lifecycle while preserving isolated
  bodies; proof_boundary=early start, bounded heartbeat, actual completion order,
  failure body, and terminal receipt tests; enforcement_posture=advisory.
- passive PLR2004 ratchet because production findings need classification before a
  ceiling is meaningful — capability_needed=baseline owner; next_center=production
  Python; transformation=no-increase pilot; proof_boundary=diagnostic inventory;
  enforcement_posture=no-gate because the current 990-item corpus is untriaged.

## History

- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
