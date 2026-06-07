# Retro — #332 commit-boundary structural-sweep enforcement

Date: 2026-06-07

## Mode

session

## Context

Activated and ran the shaped achieve goal `2026-06-07-332-commit-boundary-sweep-enforcement`
end to end. #332 escalated a 3-session recurrence (#308/#325/#329): the cheap
commit-boundary structural sweep (`validate_skill_ergonomics`,
`validate_attention_state_visibility`, the `SKILL.md` authoring preflight) was
discretionary. Slice 1 (`debug`) root-caused it to latency/ordering, NOT a
coverage gap — both gates predate #329 and were wired into both the cheap
predict-commit plan and the full-closeout verify phase. Slice 2 (`impl`) made the
full `run_slice_closeout.py` run the cheap structural sweep FIRST (a label-filtered
subset of `staged_commit_gate_plan`, fail-fast, before surface-match/cautilus/broad
pytest). Slice 3 added a staged/e2e regression test. Slice 4 closed out. Routed
via `find-skills` → debug/impl/quality/issue (in-repo, no external source).

## Evidence Summary

- `staged_commit_gate_plan.py`: `STRUCTURAL_SWEEP_LABELS` + `structural_sweep_gates`
  (subset of the existing plan = single source of truth), `run_structural_sweep_preflight`,
  `block_on_structural_sweep`; `run_slice_closeout.py` runs it first via
  `_run_preexecution_blocks`. Presence/structural only — no new judgment.
- Debug artifact `charness-artifacts/debug/2026-06-07-332-commit-boundary-sweep-latency.md`:
  falsified "post-#329 wiring" + "pure coverage gap"; staged-index repro (rc=1, 0.8s).
- +5 tests; e2e `test_full_closeout_blocks_329_class_violation_at_structural_sweep`
  verified red-without-fix / green-with-fix. 26/26 gate-plan + 175 closeout-touching
  tests green; broad gate green at closeout.
- Bounded fresh-eye critique: BLOCKER (folded) → SHIP
  (`charness-artifacts/critique/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`).
- RCA ledger: one converted `repeated_correction` event
  (`commit-boundary-structural-sweep-discretionary`, durable_kind=gate).

## Waste

- **Checked file length, missed function length (biggest waste).** I added ~16
  lines to `main()` and verified `check_python_lengths --headroom` (FILE 471/480,
  passing) but never checked the FUNCTION-length gate — `main()` went 100→116 over
  the `FUNCTION_MAX=100` hard limit, i.e. the change could not pass the very gate
  this PR hardens. The fresh-eye reviewer caught it; I folded it by extracting
  `_run_preexecution_blocks` (main() 116→86). Cheap to fix, avoidable by reading
  both length dimensions up front.
- **A leaked repro file caused two false test failures.** A `rm -f` with a zsh
  glob (`_repro_v2*.pyc`) hit `nomatch` and aborted the whole cleanup line, so a
  `scripts/_repro_v2.py` containing `"skipped"` survived into a later pytest run —
  the structural sweep correctly flagged it (a real validation of the fix) but it
  read as 2 surface-obligations regressions until I traced it to my own stray file.

## Critical Decisions

- **Sweep = label-filtered SUBSET of `staged_commit_gate_plan`, not the whole
  plan and not a new gate list.** This keeps a single source of truth (the goal's
  Boundary) and avoids re-running ruff/lengths/skills/run-evals in both the sweep
  and the verify phase (the duplicate-pressure Non-Goal). Only the 3 named
  structural gates run first; their <1s re-run in verify is the accepted fail-fast
  cost.
- **Fixed the function-length BLOCKER by extraction, not by shrinking behavior.**
  `_run_preexecution_blocks` is a behavior-preserving move of an already-cohesive
  block; the reviewer re-verified identical call order + a fresh red/green check.
- **Portability classification: host-local.** The mechanism lives in charness
  maintenance tooling (`run_slice_closeout`/`staged_commit_gate_plan`, mirrored to
  `plugins/charness/scripts/`); the generalizable doctrine extends the existing
  #314 reconciliation already in-code. Not routed to a new portable quality
  reference: consuming repos have no `run_slice_closeout` aggregate to inherit it,
  and a new doctrine reference would over-scope a gate-hardening slice (Non-Goal).
  A charness-local behavior line was added to `implementation-discipline.md`.

## Expert Counterfactuals

- A **quality-gate engineer lens** would have run `check_python_lengths` (the
  full gate, function + file) rather than only reading the `--headroom` file
  number before declaring "lengths clean" — and would have known `main()` was
  already AT the 100-line limit, so any addition needs an extraction. That single
  habit erases the session's biggest waste (the BLOCKER round-trip).
- A **test-hygiene lens** would have used explicit filenames (never a glob that
  can `nomatch`-abort under `set -e`/zsh) for repro cleanup, avoiding the
  self-inflicted false-failure detour.

## Sibling Search

- axis: other near-limit files my change touched | location: `staged_commit_gate_plan.py` (341/480, ample) vs `run_slice_closeout.py` (474/480) | decision: not a sibling — the gate-plan file has headroom; only the god-module is near-limit | proof: `check_python_lengths --headroom` on both.
- axis: other closeout entry paths that could defer the cheap sweep | location: `.githooks/pre-commit` (predict-commit, already runs it) vs full `run_slice_closeout.py` (now runs it first) | decision: both covered; no third closeout entry exists | proof: Slice 1 debug detection-gap scan.

## Next Improvements

- workflow: when adding to a file already in the length warn band, run the full
  `check_python_lengths` (function + file), not just the `--headroom` file number —
  `main()` was already at the 100-line function limit. Disposition: none — a
  checklist habit captured in this retro; the function-length gate already has
  teeth (it caught the breach via the reviewer), so no new mechanism is warranted;
  the digest regenerates from this retro (source: this retro).
- capability: the god-module `run_slice_closeout.py` is at 474/480; the next
  addition will breach the file limit. Disposition: none — registered
  `follow-up:run-slice-closeout-module-split` + handoff Next-Session candidate;
  not filed, the file passes (advisory) and the split is a #332 Non-Goal (source:
  this retro + Slice 2 critique).
- workflow: a bounded fresh-eye reviewer ran a forbidden worktree-mutating
  `git checkout` and recovered only because the mirror still held the unstaged
  change. Disposition: none — the contract already forbids worktree-mutating ops
  (`skills/shared/references/fresh-eye-subagent-review.md`, #258); the reviewer
  self-disclosed and the integrity was independently re-verified, so this is a
  recorded near-miss, not new teeth (source: this retro).

## Persisted

yes: charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md
