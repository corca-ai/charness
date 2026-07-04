# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **Efficiency plan items 1-3 all DONE this session (operator-approved "123"):**
  1. **achieve phase-brief demote** (`d14ec985`): `check_goal_artifact.py` emits an
     advisory `phase_brief` routing runs to the current-phase lifecycle/goal-artifact
     sections instead of the 52KB+16KB full-doc mandate.
  2. **A/B proof** (`a5b6f9a0`): pre/post, n=3/arm, judge wired — outcome parity 3/3
     both arms; pre runs opened lifecycle.md 0/3 (silent non-compliance), post runs did
     section-scoped reads 3/3 (~11KB). Means honestly ~null at n=3; see
     [finding.md](../charness-artifacts/efficiency/achieve-phase-brief-ab/finding.md).
  3. **Session-start front-load** (`1c455ad9`): hook directive now carries the 3-branch
     routing (pickup→handoff / discovery→find-skills / otherwise→matching skill);
     find-skills is no longer a mandatory every-session invocation. #240 protections
     carried over; contract + arithmetic in find-skills `session-start-routing.md`.
- **ACTIVATION LAG (item 3): not live yet.** The user-level hook runs from the managed
  checkout at v0.60.0 — the new directive activates only after a **release +
  `charness update`**. Cutting a release is the natural next step.
- Context-tax measurement design remains CLOSED and gated (see
  [context-tax-measurement-design.md](../charness-artifacts/reference-compaction/context-tax-measurement-design.md));
  build only on a new symptom-ledger entry + operator approval.

## Next Session

1. **Cut a release** (`charness:release`) to activate the session-start front-load and
   ship the achieve demote; then `charness update` refreshes the managed checkout.
2. Optional (operator listed as item 4, not yet approved): one baseline-vs-skill
   OUTCOME contrast for a top-traffic skill (impl or quality) to test whether the
   skill beats body-only — the effectiveness question the A/B harness can now answer.
3. Deferred follow-ups (fire on recurrence/evidence, not proactively): latest.*
   staleness validator (pattern named in session-start-routing.md §Boundary);
   whole-repo-routing eval fixture new-shape case; quality inventory-dispatch doc
   single-source (4 pinning tests, mirror 87922a7e).

## Discuss

- Demote lever largely exhausted after achieve: debug's unconditional reads total
  ~11KB (not worth it); the next efficiency frontier is per-skill effectiveness, not
  reference load.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on
  any >=60-line handoff — keep THIS file under 60 lines.
- A/B lesson: the decisive evidence was the per-run trace (section-scoped awk reads),
  not the means — read trace-digests before trusting aggregate deltas at n=3.

## References

- pickup: [finding.md](../charness-artifacts/efficiency/achieve-phase-brief-ab/finding.md) · [session-start-routing.md](../skills/public/find-skills/references/session-start-routing.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
