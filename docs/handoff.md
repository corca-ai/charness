# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **v0.63.1 is released and its host proof is on `origin/main`.** Tag
  `v0.63.1` points at `e9eac274`; host proof `e5862b10` is also an ancestor of
  `origin/main`.
- **#427 is CLOSED.** Its trace-command-marker fix is already on main; the old
  “local/unpushed” baton was stale and must not be revived.
- **Outcome-driven feedback goal is locally implemented and closing.** The
  branch adds an append-only, privacy-safe `usage_feedback` event; validator and
  reporter share one semantic record reader, and delivery is never counted as
  acceptance. Current dogfood state remains honest: 1,331 deliveries, zero
  feedback events, zero feedback coverage.
- Local quality proof after the feedback hardening: 104 focused tests passed;
  `run-quality.sh --read-only` passed 81 gates with zero failures; dup-ratchet
  passed without accepting a new baseline. Final verification-lock evidence is
  owned by the active goal artifact.
- Local commits are ahead of `origin/main`; no push, release, issue close, live
  capture, or Cautilus spend was authorized in this goal.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08 test-debt rotation](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Operator decision: push the completed local bundle.** If authorized, run
   the normal pre-push/remote proof over the final bundle once; do not infer
   consumer feedback from a green push.
2. **Watch #421 (machine-owned; do not close manually).** It remains OPEN; read
   the latest scheduled-run summary before changing the gate or baseline.
3. **Record the first legitimate feedback observation when one exists.** Start
   with [record_usage_feedback.py](../scripts/record_usage_feedback.py) dry-run,
   then use `--execute` only
   for an authoritative operator/issue/release observation; validate and report
   the appended event through the existing commands.
4. **80-site argparse-help debt runs LAST, alone.** Preserve trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **Handoff closeout-vocabulary demotion is DEFERRED.** The N=2 refresh pilot
  ranked it first, but its own policy requires a blinded integrated ship-config
  live rerun and tripwire window. Reopen only with explicit live-capture approval;
  do not delete or demote from the current evidence.
- Feedback append locking and rotated-stream reconciliation are real deferred
  seams. Reopen locking when concurrent/automatic writers exist, and rotation
  when stream growth makes multi-file target reconciliation necessary.
- No actual satisfaction signal exists yet. The new capability closes an
  evidence-path gap, not the product-success veto gap itself.

## References

- [active outcome-driven goal](../charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md) · [latest quality review](../charness-artifacts/quality/latest.md) · [mutation disposition](../charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [deferred decisions](./deferred-decisions.md)
