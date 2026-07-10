# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **v0.65.0 is released, pushed, and installed on the maintainer machine.** Tag
  `v0.65.0` points at `b8930138`; the public release URL is
  [v0.65.0](https://github.com/corca-ai/charness/releases/tag/v0.65.0)
  (HTTP-200 distinct-channel readback). The goal
  [428-reviewer-boundary-enforcement-release](../charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md)
  is complete.
- **#428 is CLOSED with a verified carrier** (`0528718e`): reviewer boundary
  enforcement shipped as rail 1 (the live-proven worktree+index
  [fingerprint script](../skills/shared/scripts/reviewer_boundary_fingerprint.py)) plus
  rail 2 (read-only `bounded-reviewer` envelope, live binding NOT yet proven —
  see #430). The mutation-CI baseline credentials failure is fixed
  (`3c25073c`).
- **Mutation Tests on the released HEAD was dispatched and still running at
  closeout** (workflow run on `4b7ba6ca`); its conclusion decides whether the
  machine-owned #421 goes green. Quality Core concluded success there.
- Dogfood state remains honest: feedback events and coverage remain zero; no
  product-success signal is claimed.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done).

## Next Session

1. **Run the #430 envelope probe FIRST (new session = the proof window).**
   Spawn a `bounded-reviewer` subagent, ask it to run a shell command, and
   record the concrete denial (or non-denial) on
   [#430](https://github.com/corca-ai/charness/issues/430); this also clears
   the goal's operator decision queue item.
2. **Read the Mutation Tests conclusion on `4b7ba6ca`** before touching the
   #421 gate or baseline; #421 stays machine-owned (do not close manually).
3. **Backlog picks via `issue`:** #431 (rail-1 wiring at reviewer-spawn steps
   of quality/release/issue/critique — four gated public surfaces, own release
   train), #429 (shared-script lint/length gate scope), #432
   (`.invalid`-identity guard + hotl identity restore), #433 (publish helper
   close-path vs commit-msg gate mismatch — two wasted release-quality runs).
4. **Record the first legitimate feedback observation when one exists** via
   [record_usage_feedback.py](../scripts/record_usage_feedback.py) dry-run
   first.
5. **80-site argparse-help debt runs LAST, alone.** Preserve trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **Handoff closeout-vocabulary demotion stays DEFERRED** pending explicit
  live-capture approval.
- Feedback append locking and rotated-stream reconciliation remain deferred
  seams (reopen on concurrent writers / stream growth).
- 62 pushed commits keep the `hotl proof` placeholder author permanently;
  history is not rewritten (#432 owns the forward guard).

## References

- [goal](../charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md) · [retro](../charness-artifacts/retro/2026-07-10-428-reviewer-boundary-enforcement-release.md) · [release proof](../charness-artifacts/release/latest.md) · [resolution critique](../charness-artifacts/critique/2026-07-10-428-resolution-critique.md) · [release critique](../charness-artifacts/critique/2026-07-10-v0-65-0-release-critique.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [deferred decisions](./deferred-decisions.md)

- Refresh kept: [#430](https://github.com/corca-ai/charness/issues/430) probe
  as the first pickup, v0.65.0 release/install state, the #421 watch with the
  in-flight run, backlog #429/#431/#432/#433, and argparse-help ordering.
- Refresh non-claims: per the [goal](../charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md),
  rail-2 binding is unproven, the Mutation Tests conclusion on `4b7ba6ca` was
  unread at closeout, no satisfaction signal exists, and the pushed identity
  placeholder is permanent.
