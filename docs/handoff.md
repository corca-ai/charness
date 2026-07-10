# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **v0.64.0 is released, pushed, and installed on the maintainer machine.** Tag
  `v0.64.0` points at `ad673083`; `origin/main` includes the release proof commit
  `2fe1e046`; public release URL is
  [v0.64.0](https://github.com/corca-ai/charness/releases/tag/v0.64.0).
- **Repo-wide quality/speed release goal is closed out, not a pickup item.**
  The durable proof lives in the goal, quality, release, and retro artifacts;
  do not redo the sweep unless a new task asks for it.
- **Dogfood state remains honest:** delivery records exist, while legitimate
  observer-owned feedback events and feedback coverage remain zero. The release
  shipped the evidence path and counting fixes, not product-success proof.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08 test-debt rotation](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Resolve the recurring reviewer-boundary follow-up #428 through `issue`.**
   It is OPEN and was not fixed or closed by v0.64.0. Start by reading the
   GitHub issue source and comments, then use the `issue` workflow for causal
   review, resolution design, and any subsequent closeout proof.
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

- [repo-wide release goal](../charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md) · [latest release proof](../charness-artifacts/release/latest.md) · [latest quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [deferred decisions](./deferred-decisions.md)

- Refresh kept: v0.64.0 release/install state, OPEN [#428 follow-up](https://github.com/corca-ai/charness/issues/428) (not fixed or closed by this release), #421 machine-owned watch, first-feedback observation path, argparse-help debt ordering, and deferred locking/rotation triggers.
- Refresh non-claims: [release goal](../charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md) remains honest that old v0.63.1/local-unpushed state was stale, #428 is open and unresolved, the repo-wide sweep is not a next-session task, and no real satisfaction signal or concurrent-writer locking proof is claimed.
