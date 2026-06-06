# Spec Handoff: Pre-Merge Gate for Changed-Line Mutation Coverage

Date: 2026-06-06
Source: debug #320 (`charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md`)
Status: draft handoff — escalated from debug because this is a repeated symptom
on the same seam (#219 -> #251 -> #260 -> #320).

## Problem (Seam, not the single file)

The scheduled mutation gate fails on `main` whenever a newly-changed line in an
eligible mutation-pool Python file lacks test coverage: the changed-line
classifier drops the file before mutation and reports `Blocking signals: FAIL`.
Each instance is resolved per-file by covering the flagged lines (the durable
per-file fix per `skills/public/quality/references/mutation-testing.md`), but the
**seam** keeps producing the same post-merge failure because there is no
pre-merge/per-slice gate that forces coverage of newly-added lines/branches in
mutation-pool files. This is the 4th occurrence; #251 and #260 already proposed a
pre-merge detection follow-up that was never built.

## What Already Exists

- `scripts/check_changed_line_mutation_coverage.py` reproduces ONLY the blocking
  changed-line signal locally over a `base..head` range, reusing the gate's own
  `classify_changed_line_scope_gap`. It is faithful but needs a real `base_sha`
  and a full coverage probe (slow), and is not wired into the per-slice closeout
  or commit gate.
- The scheduled gate (`.github/workflows/mutation-tests.yml`) computes `base_sha`
  from the previous completed mutation run; only `schedule` events compute it, so
  a `workflow_dispatch` cannot prove a changed-line fix.

## Decision To Make

Should a pre-merge or per-slice gate force coverage of newly-added changed lines
(esp. degrade/error branches) in mutation-pool files, so this class is caught
before merge instead of by the <=3h cron? Sub-questions / trade-offs:

- Cost: the faithful check needs a full coverage probe (parallel + subprocess
  capture). Is that acceptable in the per-slice aggregate, or only as an opt-in
  pre-push step? A cheaper heuristic (changed-line coverage from the already-run
  pytest coverage, without a fresh probe) may catch most cases at low cost.
- Base selection: per-slice has no "previous mutation run" base. Options: merge
  base with `origin/main`, or the staged/committed diff range.
- Scope: limit to eligible mutation-pool files (`sample_mutation_files.list_eligible`)
  to avoid noise on non-pool changes.
- Must NOT be a floor/budget tweak — mutation-testing.md is explicit the durable
  fix is coverage, not threshold relaxation. This spec is about detection timing,
  not scoring thresholds.

## Fold-In Follow-Ups

- #251 retro: a "tiny repo helper that prints changed-line coverage + blocking
  verdict pre-merge".
- #260 retro: "verify a new pool file clears both floors before commit".
- #320: `follow-up:mutation-selection-budget-setup-libs` — confirm whether the
  `setup_agent_docs_fresh_eye_lib.py` / `setup_commit_discipline_lib.py`
  selection-budget drops recur (a distinct workload-budget question, not coverage).

## Success Criteria (to refine in `spec`)

- A newly-added uncovered changed line in a mutation-pool file fails a gate the
  author runs BEFORE the scheduled cron, with an actionable `path:line` target.
- The gate's cost is bounded enough to run in the chosen phase (per-slice vs
  pre-push) without regressing closeout latency.
- No threshold/budget relaxation; the durable fix path stays "cover the lines".

## Open Non-Claims

- This handoff does not yet decide the phase (per-slice vs pre-push vs CI-PR), the
  base-selection strategy, or whether a cheap heuristic is sufficient. Those are
  the `spec` deliverables.
