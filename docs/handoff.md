# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Local `main` is ahead of `origin/main` (`c1f7b581`) and UNPUSHED.** The
  2026-06-12 overnight autonomous goal
  ([goal artifact](../charness-artifacts/goals/2026-06-12-autonomous-structural-quality-bundle.md))
  landed its bundle as local commits only; push approval was deliberately not
  assumed while the operator slept. Pushing is the first wake-up decision.
- **Overnight bundle content:** two new quality gates
  (`check-bootstrap-shim-consistency` with `--fix`, advisory
  `check-public-doc-coupling`; the standing gate count is now 76), the
  clone-advisory structural-signal taxonomy plus the quality-signal scorecard
  in the quality skill, the shared meaningful-slice cadence reference, a
  log-backed contract-effectiveness cautilus fixture (deterministically
  validated; intentionally NO live cautilus run — planner fence honored), and
  retirement of the second-machine release-proof arm (operator-approved;
  removed from the release adapter checklist and dispositioned in the v0.42.0
  release record).
- **Issues #356 and #357 are resolved locally** with direct-commit carrier
  `f9271594` (`Close #356. Close #357.`, `carrier_verified`); they auto-close
  on push. #184 remains the only other open issue and is an operator
  product-metrics ideation decision, not an implementation slice.
- The earlier Discuss item on historical issue references is resolved by the
  exported-reusable-guidance class in
  [provenance-placement](./conventions/provenance-placement.md): the record
  layer keeps provenance; exported guidance carries none, gate-enforced.

## Next Session

- **Push `main` (operator decision).** The pre-push hook runs the full gate;
  after push, run the issue tool's `verify-closeout` for #356/#357
  (`--commit-ref f9271594 --expect-state CLOSED`).
- Decide whether the overnight bundle warrants a release cut; release surfaces
  were not bumped overnight by design.
- Live execution of the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  stays behind the planner contract: it needs an explicit log-backed request
  naming a failing-prompt/transcript/operator-log path, then the
  [cautilus eval wrapper](../scripts/run_cautilus_eval.py).
- D28 and D29 reopen triggers live in
  [deferred decisions](./deferred-decisions.md); D29 (scorecard helper +
  metric-only closeout guard) reopens on a consumer-repo discovery failure or
  an operator request.
- **Keep #184 separate.** Schedule it only if the operator wants a product
  metrics ideation session.

## Discuss

- After #354's fix shipped, decide whether an operator announcement is still
  useful for the v0.40.0 scheduled-mutation-lane change and the v0.41.0
  YouTube/issue retrieval improvements.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.42.0 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
