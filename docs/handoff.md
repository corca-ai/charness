# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **v0.65.0 is released, pushed, and installed on the maintainer machine**
  (tag `v0.65.0` at `b8930138`; HTTP-200 distinct-channel readback recorded
  in [release proof](../charness-artifacts/release/latest.md)).
- **The #428 follow-up cluster is closed**: #430 (envelope probe recorded
  `envelope-unbound`, [probe artifact](../charness-artifacts/probe/2026-07-10-issue-430-bounded-reviewer-envelope-probe.json)),
  #429 and #431 (carrier `3c01f8ad`), and #432 (carrier `a0816ce7`,
  `verify-closeout` state CLOSED).
- **#432 shipped the identity guard**:
  [check_git_identity.py](../scripts/check_git_identity.py)
  refuses a `.invalid` effective git identity at the pre-commit gate plan and
  (unconditionally, duplicated + parity-tested) in the release publish plan;
  hotl proof-rules rule 7 owns the scoped-identity authoring contract. See
  the [resolution critique](../charness-artifacts/critique/2026-07-10-432-resolution-critique.md).
- **Mutation Tests on `4b7ba6ca` concluded SUCCESS** (run 29068762905). #421
  stays open and machine-owned: only a *scheduled* green run auto-closes it
  (#358); do not close manually.
- Dogfood state remains honest: feedback events and coverage remain zero; no
  product-success signal is claimed.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done).

## Next Session

1. **Resolve [#433](https://github.com/corca-ai/charness/issues/433) via
   `issue`** (publish helper `--close-issue` generates a commit the
   commit-msg gate rejects — two wasted release-quality runs).
2. **Record the first legitimate feedback observation when one exists** via
   [record_usage_feedback.py](../scripts/record_usage_feedback.py) dry-run
   first.
3. **80-site argparse-help debt runs LAST, alone.** Preserve trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **Handoff closeout-vocabulary demotion stays DEFERRED** pending explicit
  live-capture approval.
- Feedback append locking and rotated-stream reconciliation remain deferred
  seams (reopen on concurrent writers / stream growth).
- 62 pushed commits keep the `hotl proof` placeholder author permanently;
  history is not rewritten (#432 shipped the forward guard; misattribution
  detection for non-`.invalid` synthetic identities is a recorded non-goal).

## References

- [goal](../charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md) · [retro](../charness-artifacts/retro/2026-07-10-428-reviewer-boundary-enforcement-release.md) · [release proof](../charness-artifacts/release/latest.md) · [#432 critique](../charness-artifacts/critique/2026-07-10-432-resolution-critique.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [deferred decisions](./deferred-decisions.md)

- Refresh kept: the [#433](https://github.com/corca-ai/charness/issues/433)
  backlog pick as the first action, the
  [#421](https://github.com/corca-ai/charness/issues/421) machine-owned watch
  (scheduled-run close only), feedback-observation and argparse-debt
  ordering, and the permanent placeholder-author non-claim.
- Refresh non-claims: proof for the completed #430/#429/#431/#432 items lives in [#432 critique](../charness-artifacts/critique/2026-07-10-432-resolution-critique.md)
  and the linked carriers, so those next-session items and the now-read
  Mutation Tests conclusion were dropped as completed; rail-2 envelope
  binding remains unproven on this host (`envelope-unbound` recorded); no
  satisfaction signal exists.
