# Retro: Producer broad-pytest re-run waste (v0.25.0 producer slice)

Date: 2026-06-07
Mode: session

## Context

Landed the changed-line mutation-coverage producer (slice 2, lever A+B), pushed,
and released v0.25.0. The producer's instrumented broad pytest (~351s/run) ran
**four times** before a clean push. This retro is bounded to that re-run waste.

## Evidence Summary

Four producer runs (`/tmp/produce{,2,3,4}.json`), ~351s broad pytest each
(~23 min total broad-pytest wall time):

- run1 **FAILED** `check_spec_evidence_durability`: my spec Slice 2 text cited the
  gitignored `reports/mutation/test-coverage.json` without `<!-- reproduction-source -->`.
- run2 OK, but the consumer dry-run then surfaced stdout pollution (coverage
  combine/json leaked into `--json`), the untracked-new-file fingerprint mismatch,
  and a TRUE positive `rca_link_advisory.py:111`.
- run3 OK (after stdout fix + rca pragma); the POST-commit consumer then flagged
  `mutation_changed_files_lib.py:201` + `mutation_sampling_lib.py:136` — the gate
  judged my OWN changes for the first time.
- run4 OK (after adding tests for 201/136).

## Waste

- **Serial discovery behind a 6-min gate.** Each run surfaced one new issue; I
  fixed one, paid another ~6 min, found the next. 2-3 of the four runs were
  avoidable with earlier/batched detection.
- **A misleading false-green pre-commit dry-run.** The pre-commit consumer
  dry-run used `--head-sha HEAD` while HEAD was the *parent* (changes
  uncommitted), so `base..HEAD` EXCLUDED my changes → "blocking: []" looked safe,
  but the gate only judged my changes after commit (drove run3→run4). The dry-run
  gave false confidence.
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest`
  (run first, green) does NOT run `check_spec_evidence_durability` (it is a
  broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1.

## Critical Decisions (good — not waste)

- Content-fingerprint freshness (asked the user, chose A). Prevented a permanent
  silent-skip gate. Right call, and worth the one round-trip.
- Verify-via-push. Correct; the gate proved itself on the real boundary.

## Expert Counterfactuals

- **Don Reinertsen (product-dev flow / batch size + queue cost).** The dominant
  waste is large-batch, high-latency feedback: a 6-min producer is a slow queue
  and I fed it one fix at a time. Prescription: from the FIRST valid coverage
  artifact, run the consumer over the *full to-be-pushed range* once to surface
  ALL uncovered changed lines, run the cheap doc gates the broad pytest enforces,
  fix everything together, then pay for ONE final producer run.
- **Gary Klein (pre-mortem).** A 30-second "why will this be slow?" would have
  flagged: the gate scores `base..HEAD`, my work is uncommitted, the only
  coverage source is expensive — so a base..parent dry-run is a false green and
  issues surface post-commit. Same prescription: judge the worktree range.

## Next Improvements

- **workflow:** When dogfooding the changed-line gate on an uncommitted slice,
  run the consumer over **base→worktree** (a range that includes uncommitted /
  staged work), never `base..HEAD` when HEAD is the parent. And before the
  expensive producer, run the cheap gates the broad pytest enforces (esp.
  `python3 scripts/check_spec_evidence_durability.py`). Owner: a short note next
  to the producer guidance in `docs/conventions/implementation-discipline.md`.
- **capability:** the consumer's verdict is silently misleading when `--head-sha`
  excludes the worktree. Add a `check_changed_line_mutation_coverage.py` warning
  when the analyzed head == `HEAD` and the worktree has uncommitted mutation-pool
  changes, or a documented worktree-range dry-run. Cheap tripwire, kills the
  false-green. (follow-up:changed-line-gate-worktree-dryrun-warning)
- **memory:** this lesson, persisted here + refreshed into recent-lessons.

## Sibling Search

Transferable pattern: "a pre-commit dry-run keyed on `base..HEAD` gives a false
green for uncommitted work." Bounded scan of other range-based gates:

- `broad_pytest_fingerprint` (slice_closeout_broad_gate) already hashes the
  *working tree* (`git diff --binary` + `--cached` + file content) — not affected.
- `sample_mutation_files.list_changed` / `check_changed_surfaces` operate over
  committed ranges at closeout/cron time by design, not as pre-commit dogfood
  dry-runs — out of scope.
- Conclusion: the false-green is specific to manually dogfooding the changed-line
  consumer pre-commit; the durable fix is the workflow note + the optional
  worktree warning above. No broad sibling refactor needed.

## Persisted

Written by the retro persist helper (path in closeout).
