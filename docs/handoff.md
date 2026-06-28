# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- No loop is pre-queued. For the next quality loop, start with `quality` for gate
  posture, then `impl` one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **#406 CLOSED (resolved this session): achieve closeout authoring churn.**
  Carrier `2ec82fd1` (pushed; `gh issue view 406` CLOSED/COMPLETED). Shipped all
  four levers — template `Routing:`/`Discuss before activation:` stubs, the shared
  `join_soft_wraps` floor-parser fix (via a `joined_section_body` seam), the
  Operator-Decision-Queue describe surfacing, describe-first rejection messages
  (operator_queue + critique validator), and the unified aggregate-preflight
  principle. Fresh-eye critique SHIP-WITH-NITS (one accepted, documented
  over-join shadow); 2449 quality_gates tests pass; dup-ratchet re-baselined for
  the resulting span-content changes.
- **v0.56.9 published; #405 CLOSED.** The #405 quality-lens doctrine shipped
  ([release notes](../charness-artifacts/release/notes-v0.56.9.md)). v0.56.8
  (D30) remains published; D30 residuals deferred, not urgent.

## Next Session

- **No pinned pickup.** #406 was resolved this session (see Current State). For
  the next quality loop, start with `quality` for gate posture, then `impl` one
  narrow slice. D30 follow-on residuals reopen only on observed re-baseline
  friction.

## Discuss

- A `nose v0.16.0` upgrade is advisory-available; bumping the installed nose would
  regroup families and trigger the scanner-version skew WARNING -> a one-time
  lockstep re-baseline (by design, not a defect).

## References

- [#406 resolution critique](../charness-artifacts/critique/2026-06-28-issue-406-closeout-churn-resolution-critique.md)
- [release notes v0.56.9](../charness-artifacts/release/notes-v0.56.9.md)
- [deferred-decisions D30 (resolved)](./deferred-decisions.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
