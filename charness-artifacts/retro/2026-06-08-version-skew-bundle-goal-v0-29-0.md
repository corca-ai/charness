# Retro: version-skew bundle goal (v0.29.0)
Date: 2026-06-08
Mode: session

## Context

Goal: `charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`.

Achieve goal bundling three release/tooling hardening proposals and proving them
end-to-end with a real release: (1) `charness update` as a required maintainer
install-refresh release-closeout step; (2) the six artifact scaffolds cite the
repo-local `scripts/` validator (repo-local-first) instead of the installed
plugin's; (3) a `goal-activation` author-time preflight surface. Shipped as
v0.29.0 (real push + tag + GitHub release), then proven by running `charness
update` on this dev machine and confirming installed == repo + the installed
scaffold cites the repo-local validator. #335 rides along (next scheduled
mutation run is its authoritative verdict).

## Evidence Summary

- 6 commits this goal (goal shape + Slices 1-3 + coverage fix + release-prep) +
  the helper's release commits (4ddd9334, 360d81c7).
- Gates: broad read-only 73/0; release-mode 73/0; changed-line mutation coverage
  ok over merge-base origin/main..HEAD (9 pool files, fresh fingerprint).
- Release: v0.29.0 verified (origin/main 0/0; tag on remote; GitHub release not
  draft; 5 surfaces at 0.29.0, no drift). On-machine: charness update
  0.28.0->0.29.0; installed HEAD 360d81c7 == repo; doctor 16 checks, 0 not-ok;
  installed validate_debug_artifact.py byte-identical to repo's.
- Three fresh-eye critiques (Slice 2 SHIP; Slice 3 HOLD->SHIP; release HOLD->SHIP).

## Waste

- The `release` SKILL.md was at the 160 core_nonempty cap, so additive Slice-1
  contract text tripped the #319 commit-boundary headroom ratchet; I compressed 9
  existing bullets to land at 158 (net headroom RESTORED). One extra editing pass.
- The first Slice-2 test subprocessed `scripts/export_plugin.py`, adding a new
  boundary-bypass-ratchet candidate that blocked the commit; rewrote the test to
  use the already-synced in-repo plugin mirror as the installed-like tree. One
  commit-retry cycle.
- New commits invalidated the prior changed-line coverage fingerprint, so the
  broad gate warned; running the producer over merge-base origin/main..HEAD then
  flagged one genuinely-uncovered changed line (the preamble-not-found branch),
  which I covered. A warn->produce->cover round-trip.
- NOT waste: the fresh-eye critiques caught two real defects before they shipped
  (Slice-3 owner-message enforcer misattribution; release stale
  update_instructions). That is the intended function, high value.

## Critical Decisions

- Repo-local-first as a search-ORDER swap, keeping the 6 scaffold functions
  self-contained per-skill (NOT extracting a shared helper): preserved
  portability/export and verdict-equality; the existing clone family is
  intentional boilerplate.
- Portable/charness split for the install-refresh step: the rule lives in the
  portable `release` SKILL.md via the adapter-declared update path; the concrete
  `charness update` command lives only in the charness-specific reference +
  adapter. Kept the public skill host-neutral.
- Refreshing the coverage producer BEFORE pushing (not trusting the non-blocking
  stale-fingerprint skip): prevented a new #335 recurrence instance from landing.
- Running the real release + on-machine update (operator-authorized): produced
  the end-to-end proof the operator asked for instead of asserting it.

## Expert Counterfactuals

- **Gary Klein (pre-mortem / recognition-primed decision).** Would have predicted
  that new mutation-pool commits invalidate the coverage fingerprint and run the
  changed-line coverage producer as the FIRST bundle-boundary step, before the
  broad gate — collapsing the warn->produce->cover round-trip into one pass.
  Changed action: at a release/bundle boundary that added mutation-pool commits,
  refresh coverage first.
- **Atul Gawande (checklist discipline).** Would have treated the
  `update_instructions` version bump as a fixed pre-publish checklist item (it is
  required every release by the publish staleness guard), pre-empting the release
  critique's round-1 HOLD. Changed action: a release-prep step (or a
  publish-helper dry-run that EMITS the stub entry) bumps update_instructions
  before the critique, so the HOLD never fires. (The release critique DID catch
  it pre-publish — the fail-safe held — but earlier is cheaper.)

## Next Improvements

- workflow: at a release/bundle boundary where the session added mutation-pool (`scripts/**`, `skills/**`) commits, run `check_changed_line_mutation_coverage.py --write-fresh-marker` over `merge-base origin/main..HEAD` as the FIRST step, before the broad gate, because new commits invalidate the prior fingerprint and deferring it costs a warn->produce->cover round-trip. Disposition: applied: persisted to recent-lessons this run (the next-time checklist) so the precondition is a workflow signal, not memory.
- workflow: additive contract work on an at-cap SKILL.md, or a new test that subprocesses a top-level `scripts/<x>.py`, trips a no-increase ratchet (core-headroom / boundary-bypass); anticipate by compressing-to-offset or reusing an in-process / in-repo-mirror path from the start. Disposition: applied: persisted to recent-lessons this run as a pre-commit-design signal.

## Sibling Search

Transferable pattern: "additive change trips a no-increase ratchet, forcing a
rework pass." Four-axis scan for siblings of this pattern:

- by-validator: the two no-increase ratchets hit this run are
  `check_skill_surface_preflight.py` (core-headroom) and
  `check_boundary_bypass_ratchet.py`. Both are already author-time/commit-boundary
  surfaced (they blocked at the right time, pre-merge) — the gap is anticipation,
  not a missing gate. Decision: no new gate.
- by-surface: other at-cap SKILL.md cores could trip core-headroom on the next
  additive edit; the ratchet already grandfathers + blocks erosion, so it is
  self-surfacing. Decision: recent-lessons signal (applied above) is sufficient.
- by-test-idiom: new tests subprocessing top-level `scripts/<x>.py` add
  boundary-bypass candidates; the in-process / in-repo-mirror idiom avoids it.
  Decision: recent-lessons signal (applied above).
- by-recurrence: this is a workflow-anticipation lesson, not a code defect class;
  no fresh narrow issue warranted. Decision: none — handled by the two applied
  recent-lessons signals.

## Persisted
