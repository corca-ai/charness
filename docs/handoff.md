# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the new draft goal, then continue with `achieve` for
  [the post-push operational-proof goal](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md).
- First read the [goal](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md),
  [quality posture](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md), and the governing North Star.
  Do not reactivate the completed all-open-issue goal.

## Continuation Capability

- The active umbrella sequence is complete: all 17 scoped issues are CLOSED;
  the eight final carrier/state pairs are in the goal ledger.
- The published head is `e7c3e1b3`; verify live state with commands rather than
  treating this handoff as a current-state database.
- The one-push boundary is closed. Do not push again as part of lifecycle
  closeout; any future publish needs its own explicit final phase and gate.
- Keep local quality, GitHub issue state, GitHub Actions, installed-host,
  provider, and Cautilus claims separate.

## Current State

- The final local and pre-push quality gate passed 86/0; GitHub Quality Core run
  `31062451122` for the published head completed successfully in both jobs.
- The remote open-issue query after publish returned empty; #508 and #509 were
  already independently CLOSED before the final eight-carrier bundle.
- The next goal now covers the full structural set: slice manifest, premise
  preflight, final-bundle preflight, runtime attribution, mutation producer
  discovery, and immutable publish-ledger reconciliation.
- Detailed evidence lives in the [completed goal](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md),
  [session retro](../charness-artifacts/retro/2026-08-06-session-retro.md), and
  [claims review](../charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md).

## Next Session

1. Activate the expanded post-push operational-proof goal after reading its
   boundaries and the current quality/recent-lessons surfaces.
2. Freeze the current head, issue/CI readback, reader-root matrix, and first
   slice manifest; use premise preflight before designing any remedy.
3. Run final-bundle preflight in dry-run mode and verify it selects sync,
   artifact, critique, behavior, and gate surfaces without manual reconstruction.
4. Measure isolated versus contended runtime with repeated unit-labelled
   samples, and make mutation producer discovery emit a complete command set.
5. Implement the immutable publish ledger and reconcile its output into goal and
   handoff state. Keep issue/CI/provider ownership separate.
6. Run source/plugin parity, fresh-eye review, and the full applicable gate
   before considering any separately authorized publish.

## Discuss

- No decision is needed to read or measure. Stop for explicit direction if the
  next slice would require a release, tag, version bump, PR, Cautilus run, or
  external write beyond the normal gated workflow.
- If runtime evidence is mixed, preserve the current floor and record the
  uncertainty rather than converting an advisory signal into a blocker.

## References

- [Next-session goal](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md)
- [Completed goal and issue ledger](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Session retro](../charness-artifacts/retro/2026-08-06-session-retro.md)
- [North Star](./design-north-star.md)

- Refresh kept: the exact [next-goal path](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md), published-head address, CI readback command, and runtime/mutation first actions because each changes the next operator's first move.
- Refresh non-claims: installed-machine behavior, private consumer/provider roundtrip, live-agent behavior, release/tag/version claims, and Cautilus execution remain unproven or out of scope; see the [completed goal](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md).
