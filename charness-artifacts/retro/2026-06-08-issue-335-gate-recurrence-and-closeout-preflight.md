# Session Retro
Date: 2026-06-08

## Mode

session

## Context

Ran the achieve goal `2026-06-08-gate-recurrence-mutation-and-closeout-preflight`
end to end (Slices 1–5): close two recurring harness gate seams — (1) #335, the
Nth instance of the changed-line mutation-coverage gate auto-filing post-merge,
and (2) the goal-closeout/coordination-floor authoring surfaces the v0.28.0
preflight generalization did not cover — applying the "close the loop, don't file
the N-th instance" discipline.

## Evidence Summary

- Debug artifact `charness-artifacts/debug/2026-06-08-issue-335-changed-line-mutation-recurrence.md`
  (validates; seam-risk-index synced): falsifiable root cause = genuinely-uncovered
  changed lines (not a selection/budget drop), proven by per-line `changed_and_missing`
  + a fresh same-worktree coverage probe.
- Local mutation-coverage producer (the gate's own probe): the NEXT scheduled run's
  range (base = `858c9eab`, the failed #335 run's head) blocked on **85 uncovered
  changed lines across 3 v0.28.0 files** beyond #335's 8 survivor lines. After
  Slices 2–4: `ok: True, blocking: []` over both `858c9eab..HEAD` and `7f0231e3..HEAD`
  (re-produced 3×, once per code slice).
- 6 commits (Slices 1–4 + closeouts); 2 fresh-eye critiques (both SHIP, zero
  blockers) — the Slice 3 reviewer independently traced the surfacing WARNING through
  `run-quality.sh:296` attention-output to confirm it reaches the operator.
- RCA ledger: one converted `repeated_correction` (durable_kind=gate).
- Host-log probe `charness-artifacts/probe/2026-06-08-issue-335-goal-closeout.md`:
  repeated broad gates = none (no gate-rerun waste); 4 subagent spawns; 4 compactions.

## Waste

- **The full coverage probe ran 4× (~3–4 min each, ~15 min total)** — once to
  reproduce (Slice 1) and once per code slice's boundary verification (Slices 2/3/4)
  plus the closeout. This is the slice-boundary verification cadence, not pure waste
  (each was a real per-slice proof and each caught nothing because the prior slice's
  targeted unit tests already covered the lines). But for consecutive slices that
  touch the SAME mutation-pool files, the full-coverage proof could batch to the
  bundle boundary, with the slice-boundary proxy being the targeted unit tests.
- Low otherwise: coverage is range-independent, so I re-classified the same coverage
  report over multiple base ranges with `--reuse-coverage` (cheap) instead of
  re-probing — that reuse avoided ~2 extra full runs.

## Critical Decisions

- **Reproduced over the ACTUAL next-run base (`858c9eab`), not just #335's
  `7f0231e3..858c9eab` range.** This surfaced the 85 v0.28.0 uncovered lines — the
  iceberg under #335. Without it, covering only #335's 8 survivors would have left
  the next scheduled run to fail on the v0.28.0 lines and auto-file the next
  instance. This is what made the work close the CLASS, not the instance.
- **Recurrence reduction = surfacing, not a new hard gate.** The silent skip (an
  unverified skip reads identically to a clean pass) became a loud non-blocking
  obligation — additive, behavior-preserving, matching the goal's "no Goodhart /
  no new hard gate" constraint. The hard-gate/auto-produce escalation is a recorded
  deferred follow-up.
- **Made the early-close floor module its own scaffold** so the preflight surfaces
  the early-close shape single-source with the validator (pinned by a round-trip
  test), rather than re-declaring the shape.

## Expert Counterfactuals

- **Gary Klein (premortem):** asking "what would make the NEXT scheduled run still
  fail?" up front is exactly what drove reproducing over the next-run base and
  finding the 85-line iceberg. The lens that turns "fix the reported survivors" into
  "fix what the next run will see" — the difference between instance and class.
- **Tony Hoare (null/absence confusion):** "an unverified skip reading as a clean
  pass" is the classic conflation of *absent* with *empty/ok*. Naming and breaking
  that equivalence structurally (a distinct `coverage_not_verified` signal) is the
  durable fix, not more coverage.

## Sibling Search

Transferable pattern: *a gate that skips silently when its input is absent reads
identically to a clean pass.* Four-axis scan across `run-quality.sh` / closeout gates:

- **content axis** (other `--skip-if-*` / non-blocking skips): the optional-inventory
  gates (`run-quality.sh:523,538,543,548`) all ECHO a "skipping" message — loud, not
  silent. decision: no change | proof: they print a skip line, so absence ≠ pass.
- **container axis** (the changed-line consumer, `run-quality.sh:510`): the LONE
  silent skip. decision: fixed now (Slice 3 surfacing) | proof: the new stderr
  WARNING + `coverage_not_verified` flag, reviewer-verified to reach the operator.
- **producer axis** (the closeout producer opt-in): producing coverage is still
  opt-in; the surfacing now makes its absence visible. decision: valid follow-up
  outside the slice | proof: deferred | follow-up: deferred mutation-coverage-auto-produce.
- **entity axis** (other auto-filing CI markers): only the mutation workflow
  auto-files on this repo. decision: no sibling | proof: single auto-issue workflow.

## Next Improvements

- **workflow:** When consecutive slices touch the SAME mutation-pool files, batch
  the full changed-line coverage proof to the bundle boundary and use the slice's
  targeted unit tests as the slice-boundary proxy, instead of re-probing full
  coverage every slice. Disposition: none — the per-slice proof caught real green
  state each time and the goal's cadence asked for it; recording the batching option
  for goals with many same-file slices rather than changing the contract now.
- **capability:** A one-shot "classify changed-line coverage over multiple base
  ranges from one coverage report" helper would formalize what I did by hand
  (`--reuse-coverage` over 7f02.. then 858c..). Disposition: none — `--reuse-coverage`
  already makes the manual reclassify cheap; not worth a new flag yet.
- **memory:** The "an unverified skip must not read as a pass" doctrine is now in
  `skills/public/quality/references/mutation-testing.md` (portable).
  Disposition: applied: committed the doctrine subsection in Slice 3 (commit `81332c72`).

## Persisted

yes: charness-artifacts/retro/2026-06-08-issue-335-gate-recurrence-and-closeout-preflight.md
