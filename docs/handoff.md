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
- The active goal now covers the full structural set: slice manifest, premise
  preflight, final-bundle preflight, runtime attribution, mutation producer
  discovery, and immutable publish-ledger reconciliation.
- Slice 6 is implemented and reconciles the captured snapshot through
  `python3 scripts/publish_state_ledger.py --repo-root .`; source/plugin
  validator files are byte-identical, and the focused ledger behavior is
  covered by `python3 -m pytest -q
  tests/quality_gates/test_publish_state_ledger.py`. The ledger is offline and
  source-claim bound; it does not refresh providers or perform writes.
- Detailed evidence lives in the [completed goal](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md),
  [session retro](../charness-artifacts/retro/2026-08-06-session-retro.md), and
  [claims review](../charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Read the active goal's Slice 7 closeout frame, quality posture, recent
   lessons, and North Star.
2. Run the final-bundle preflight dry run and the strongest applicable local
   quality gate over the integrated six-slice state.
3. Validate the ledger in human and JSON modes, inspect the closeout/retro
   dispositions, and refresh this handoff with the final proof paths.
4. Do not push, release, tag, run Cautilus, or claim installed/provider
   behavior; any future publish needs its own explicit gated phase.

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
