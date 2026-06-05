# Disposition Review — 302-305-gather-setup-release-robustness goal closeout

Date: 2026-06-05
Goal: 302-305-gather-setup-release-robustness
Reviewer: bounded fresh-eye subagent (general-purpose, read-only), rung-2 of the
improvement-disposition gate.

## VERDICT: dispositions-sound

Audited whether the goal's `## Auto-Retro` genuinely disposes each surfaced
improvement (real `applied: <what>` or real `issue #N`; no prose-only memory),
and whether the non-escalated items hide a workflow gap.

## Per-improvement

- **Improvement:** run cheap standalone structural checkers
  (`check_test_repo_copy_invariants.py` and peers) at the per-slice / pre-commit
  boundary so test-fixture drift fails at the commit boundary, not the final
  broad gate.
  - **Disposition:** `issue #307`.
  - **Real?** Yes. Issue corca-ai/charness#307 exists on the backend (OPEN,
    created 2026-06-05 during this run); its body matches the improvement. The
    reviewer independently confirmed the gap is currently true:
    `scripts/check_test_repo_copy_invariants.py` exists but is not wired into
    `scripts/run_slice_closeout.py`, so the checker runs only in the broad gate.
  - **Routing:** `issue` (not `applied`) is defensible — it is a quality-contract
    / gate-economics change with a stated latency tradeoff that should route
    through `quality`; applying it unilaterally inside a robustness-bundle goal
    would be scope creep.

## Missing improvements

None. The retro lists exactly one improvement and it is fully disposed. The two
"gates working as intended" items (attention-state reword via the real
`validate_attention_state_visibility.py` gate; the bug-class `Siblings:` ledger
field parse) each fired at the correct boundary and cost a single edit, so
non-escalation is correct, not a cover for a gap. The Final-Verification residual
risks (PID-1 headless-marker heuristic; #305 resume re-running push-time-flaky
gates) are recorded as explicit known boundaries / non-claims, not actionable
undisposed improvements.

## Notes

All four `Close #N` carriers verified in commit bodies (db66a30b #304, cb909eda
#303, 5318a9a7 #302, 4b76196f #305) plus the test-fixture follow-up 0c593e23 —
matching the goal's ledger. Bar met for the one originally-surfaced improvement.

## Extended audit (follow-up two-lens goal critique)

A later operator-requested two-subagent critique of the whole goal found that
this first review had scoped itself to the single surfaced improvement and
**rubber-stamped the retro's Waste boundary**. The critique confirmed (against
the diffs) that the persisted retro under-recorded three genuine waste items —
the #302 attention-state declare-then-revert detour (understated as a "reword"),
the #305 staleness regex→containment iteration (only in the counterfactual), and
the #302 mid-slice length-gate refactor (absent) — and that the
authoring-discipline lesson sat as undisposed prose in the Raskin counterfactual.
Reconciliation (committed): the retro `## Waste` was upgraded to record all
three honestly; **issue #308** was filed to disposition the authoring-discipline
lesson; and a #305 resume negative-path test
(`test_resume_aborts_before_push_when_revalidation_fails`) was added as an
`applied` disposition. Closeout integrity, non-claims, and scope were re-verified
clean with no blocker.
