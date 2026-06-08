# Issue #335 Changed-Line Mutation Recurrence Debug
Date: 2026-06-08

## Problem

Scheduled mutation gate on `main` (run `27110952590`) reported `Status: FAIL`,
`Mutation score: PASS` (86.7% vs 80%), `Blocking signals: FAIL` — "changed lines
left test-uncovered, or eligible changed files dropped by selection/workload
budgets, before mutation" — and auto-filed #335. Nth instance of the
#219 → #251 → #260 → #320 → #321 seam.

## Correct Behavior

- Given a `base..head` range whose eligible mutation-pool changed lines are all
  test-covered, the blocking changed-line signal is clean (score path is
  independent).
- Given a closeout touched eligible mutation-pool files, any uncovered changed
  line is SURFACED to the author before it lands on `main` — not discovered
  post-merge by the cron, whose only action is to auto-file.

## Observed Facts

- #335 lists exact `path:line` targets in TWO files: `check_python_lengths.py`
  (217, 281, 282, 289) and `staged_commit_gate_plan.py` (361–364) — the #332
  additions (`function_warn_for` test-branch return, `function_headroom_for`
  `except SyntaxError`/None-lineno guards, `block_on_structural_sweep` failing-
  stream print). Per-line `changed_and_missing` lists (not a budget-drop notice)
  ⇒ genuinely uncovered, not a selection drop; files are in the eligible set.
- Scheduled CI base = the previous completed run's `head_sha`
  (`mutation-tests.yml:149-150`, success OR failure). #335 ran `7f0231e3..858c9eab`;
  the NEXT run uses base `858c9eab` → HEAD, accumulating all commits since.
- The LOCAL gate uses a different base, `merge-base origin/main HEAD`
  (`run-quality.sh:509`, producer `mutation_coverage_producer.py:81-89`).
  Producing coverage is opt-in (`--produce-mutation-coverage`); the consumer
  skips silently (`--skip-if-no-coverage` exits 0; `--require-fresh-coverage`
  skips on a stale fingerprint).

## Reproduction

One instrumented coverage run (the gate's own `run_test_coverage`, parallel +
subprocess-capturing), then classify:

- `7f0231e3..HEAD` (incl. #332 + v0.28.0): 5 blocking files.
- `858c9eab..HEAD` (ACTUAL next-run base): **85 uncovered changed lines / 3
  files** — `check_artifact_surface_preflight.py` (33: `_format_changed` + `main`
  CLI), `slice_closeout_reporting.py` (47: the extracted print functions),
  `check_goal_artifact.py` (5: de-launder reporting).

Cmd: `MUTATION_BASE_SHA=7f0231e3 MUTATION_HEAD_SHA=HEAD python3
scripts/check_changed_line_mutation_coverage.py --repo-root . --write-fresh-marker`
then `--base-sha 858c9eab --head-sha HEAD --reuse-coverage`. The #335 survivors
are now in the next run's base, so covering ONLY them leaves the 85 v0.28.0 lines
to fail the next run and auto-file a fresh issue — the recurrence.

## Candidate Causes

- Genuinely uncovered changed lines: #332 + v0.28.0 added branch/print/CLI lines
  tested only on happy/JSON paths.
- Selection/workload-budget drop: FALSIFIED — per-line `changed_and_missing`, files
  in eligible set, no budget-drop notice.
- Stale-coverage false positive: FALSIFIED — coverage produced fresh this session
  over the current worktree via the gate's own probe.
- Structural recurrence: local gate runs a narrower base than the scheduled gate
  AND skips silently without fresh coverage, so debt accumulates on `main`.

## Hypothesis

Covering the genuinely-uncovered lines (the #335 survivors + the 85 v0.28.0 lines)
flips the local producer's changed-line verdict green over the next-run range; and
making the gate SURFACE the obligation when eligible files changed but no fresh
coverage exists stops the class reaching the scheduled run un-checked. Falsifier:
a covered line still reported uncovered ⇒ a measurement/selection bug, not a gap.

## Verification

- Budget-drop and stale-coverage refuted by the per-line evidence + fresh probe.
- Slice 2 covers the lines and re-runs the producer to confirm `ok: true` over
  `858c9eab..HEAD` (no threshold/pool/signal change).
- The authoritative #335 verdict is the next SCHEDULED run; agent cannot run CI —
  recorded as external proof, not claimed.

## Root Cause

1. **Instance:** #332 (and, for the next run, the v0.28.0 commits) added
   branch/print/CLI lines to eligible mutation-pool scripts with tests covering
   only happy/JSON paths; the gate correctly flagged the uncovered lines.
2. **Recurrence:** the local changed-line gate (a) runs over `merge-base origin/
   main HEAD` while the scheduled gate runs `prev-run-head..HEAD` — so local
   "green" never spans the accumulated since-last-cron range — and (b) skips
   silently (exit 0) without fresh coverage, which is opt-in. Uncovered changed
   lines land on `main` and are caught only by the cron, which can only auto-file.

## Invariant Proof

- Invariant: every changed line in an eligible mutation-pool file is test-covered
  (or its absence surfaced) BEFORE it lands on `main`, so the scheduled consumer
  never finds a NEW uncovered changed line.
- Producer Proof: local gate over `merge-base..HEAD` — PARTIAL (skips silently;
  narrower range than the consumer).
- Final-Consumer Proof: the scheduled run over `prev-run-head..HEAD`, where #335
  surfaced — confirming producer-only proof is not end-to-end.
- Interface-Shape Sibling Scan: consumer base (`prev-run head`) and producer base
  (`merge-base origin/main HEAD`) are different functions of history.
- Non-Claims: NOT proven the next CI run is green (agent cannot run CI); only the
  local producer over the next-run range.

## Detection Gap

- local changed-line consumer | `--skip-if-no-coverage` exits 0 silently and
  `--produce-mutation-coverage` is opt-in | fire it: when eligible files changed
  AND no fresh coverage exists, SURFACE a visible "produce coverage + verify
  changed lines" obligation instead of a silent skip.

## Sibling Search

- Mental model (wrong): "a local gate over `merge-base..HEAD` proves no uncovered
  changed line reaches the scheduled run."
- same-file: `check_python_lengths.py`, `staged_commit_gate_plan.py` (#335) |
  fixed now (Slice 2) | proof: producer re-run.
- same-boundary: `check_artifact_surface_preflight.py`, `slice_closeout_reporting.py`,
  `check_goal_artifact.py` (same class already queued) | fixed now (Slice 2) |
  proof: producer re-run.
- same-mental-model: producer/consumer base divergence + opt-in/silent-skip |
  structural reduction (Slice 3) + critique | proof: deferred to Slice 3.
- adjacent-clean: `disposition_form.py`, `validate_retro_artifact.py`,
  `run_slice_closeout.py`, `goal_artifact_disposition.py` changed but covered |
  no action | proof: not in `blocking`.
- cross-file: `scripts/check_artifact_surface_preflight.py`,
  `scripts/slice_closeout_reporting.py`,
  `skills/public/achieve/scripts/check_goal_artifact.py` — same-class uncovered
  changed lines OUTSIDE the subject changed-line-gate file (the v0.28.0 debt),
  covered in Slice 2.
- follow-up: none outside this goal's slices.

## Seam Risk

- Interrupt ID: issue-335-changed-line-mutation-recurrence
- Risk Class: host-disproves-local
- Seam: local closeout gate (`merge-base..HEAD`, opt-in/skip-prone) → `main` →
  scheduled run (`prev-run-head..HEAD`, authoritative).
- Disproving Observation: v0.28.0 closeouts left 85 uncovered changed lines the
  scheduled run would flag; the local gate skipped without fresh coverage.
- What Local Reasoning Cannot Prove: the next scheduled CI run is green.
- Generalization Pressure: factor-now

## Interrupt Decision

- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/mutation-changed-line-premerge-gate.md
  (the canonical premerge-gate spec — the seam mechanism is designed + critiqued
  there in Slice 3 before its impl; Slice 2 covers the lines as ordinary impl.)

## Prevention

Turn the local gate's silent skip into a SURFACED obligation when eligible
mutation-pool files changed but no fresh coverage exists (Slice 3), so the author
covers the line before it lands. Cover the genuinely-uncovered changed lines
across all 5 files (Slice 2) so the next-run range is green — not just #335's two
survivors.

## Related Prior Incidents

- `2026-06-06-issue-320-mutation-changed-line-coverage.md`: the direct #320
  predecessor on this seam.
- `2026-05-22-mutation-changed-diff-suppression.md`: failed changed-file diff
  collapsed to empty changed set (a different failure on the same gate).
- `2026-05-21-mutation-subprocess-coverage.md`: subprocess CLI scripts read as 0%
  under naive coverage — why the gate uses parallel coverage.
