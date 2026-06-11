# Critique: Achieve Timebox Early-Close Gate

Execution: completed
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: n/a (no adapter sections)
Target: code-critique

## Reviewer Tier Evidence

- Requested tier: default inherited model, explorer role
- Requested spawn fields: agent_type=explorer; fork_context=false
- Host exposure state: applied
- Application state: host-confirmed: spawn_agent returned subagent
  `019eb87e-8148-7350-8f6c-f81eaa8e0aed`; wait_agent returned completed
  findings, including two actionable test/gate concerns that were addressed.

## Change

`achieve` timeboxed closeout now blocks completion before the reserve window
unless `## Final Verification` records an early-close reason, at least two
distinct `Next slice candidate:` decisions, and an `Outcome sufficiency check:`.

## Success Criteria

- A one-line `No safe next slice:` / `Early close rationale:` no longer closes a
  long timeboxed goal early.
- The gate proves at least two concrete continuation candidates were considered.
- `upsert_goal(... status="complete")` exercises the same early-close path.
- Public skill docs, dogfood review, and plugin exports stay synchronized.

## Out Of Scope

- Reworking the entire `achieve` lifecycle.
- Changing host goal-slot behavior.
- Running live Cautilus proof; planner returned `next_action: none`.

## Fresh-Eye Findings

Reviewer: Feynman (`019eb87e-8148-7350-8f6c-f81eaa8e0aed`)

- Act Before Ship: `tests/quality_gates/test_goal_artifact_timebox.py` did not
  exercise the new early-close ledger through `upsert_goal`; it only proved a
  future activation refused completion. Fixed by adding one blocked and one
  allowed `upsert_goal(... status="complete")` integration test with an
  activation in the past but before the reserve window.
- Bundle Anyway: duplicate `Next slice candidate:` names could satisfy the
  count. Fixed by requiring at least two distinct normalized candidate names and
  adding a duplicate-name regression test.
- Over-Worry: no public/plugin export drift; reviewer checked changed
  `achieve` files with `cmp`.
- Valid But Defer: no broader lifecycle rewrite in this slice.

## Counterweight Triage

- The integration-test gap was real because the user's observed failure was the
  closeout helper accepting an underspecified early stop, not merely an invalid
  activation timestamp.
- Distinct-name enforcement is cheap and prevents a low-effort ledger from
  satisfying the letter of the rule.
- Keeping the detailed rule in `references/lifecycle.md` instead of the root
  `SKILL.md` is intentional; the root must retain reference-index headroom.

## Verification

- `pytest -q tests/quality_gates/test_goal_artifact_timebox.py` -> 11 passed.
- Focused regression bundle -> 94 passed.
- Broad pytest -> 2806 passed, 4 skipped, 26 deselected.
- Validators: packaging, committed packaging, skill validation, public skill
  dogfood, Cautilus proof policy, docs, markdown, secrets, ruff, py_compile,
  Python length, boundary-bypass ratchet, attention-state visibility, copy
  invariants, and gitignore scan hygiene passed.

## Deliberately Not Doing

- Not adding generated placeholders to every goal artifact template for the
  early-close ledger; the ledger is conditional on early close before reserve,
  and the canonical rule lives in the lifecycle/reference docs plus the helper.

## Next Move

Commit the strengthened `achieve` early-close gate, then create the next active
quality-improvement goal requested by the user.
