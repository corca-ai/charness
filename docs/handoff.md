# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the new draft goal, then continue with `achieve` for
  [the post-push operational-proof goal](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md).
- First read the [goal](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md),
  [quality posture](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md), and the governing North Star.
  Do not reactivate the completed all-open-issue goal.
- Release `v3.3.0` is published; read the [release record](../charness-artifacts/release/latest.md)
  for publication and installed-host evidence before starting the next slice.

## Continuation Capability

- The active umbrella sequence is complete: all 17 scoped issues are CLOSED;
  the eight final carrier/state pairs are in the goal ledger.
- The published release is `v3.3.0`; verify live branch/tag state with commands
  rather than treating this handoff as a current-state database.
- The one-push boundary is closed. Do not push again as part of lifecycle
  closeout; any future publish needs its own explicit final phase and gate.
- Keep local quality, GitHub issue state, GitHub Actions, installed-host,
  provider, and Cautilus claims separate.

## Current State

- The final release quality gate, fresh-checkout probes, public release page,
  and installed version/doctor readbacks are recorded in the release record;
  re-run commands when a current fact is needed.
- The remote open-issue query after publish returned empty; #508 and #509 were
  already independently CLOSED before the final eight-carrier bundle.
- The active goal now covers the full structural set: slice manifest, premise
  preflight, final-bundle preflight, runtime attribution, mutation producer
  discovery, immutable publish-ledger reconciliation, and the integrated
  closeout.
- Slice 7 closeout is recorded in the active goal and quality artifact; the
  final-bundle dry run is ready with zero blockers; recount the neighboring
  proof suites with `python3 -m pytest -q
  tests/quality_gates/test_premise_preflight.py
  tests/quality_gates/test_slice_manifest.py
  tests/quality_gates/test_final_bundle_preflight.py
  tests/quality_gates/test_publish_state_ledger.py`. The verification-locked
  closeout emitted fresh coverage whose clean changed-line consumer passed for
  the declared Python pool at the manifest-declared `ff3029…` slice base. The
  ledger remains offline and source-claim bound; provider refresh, the optional
  `nose` tool proof, Cautilus, and broader cross-host evidence remain unclaimed.
- Detailed evidence lives in the [completed goal](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md),
  [session retro](../charness-artifacts/retro/2026-08-06-session-retro.md), and
  [claims review](../charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"7eed13ec9b819e6d581ea08ea244820579c08935","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T09:08:00Z"}
```

## Next Session

1. Read the completed goal's Slice 7 closeout frame, quality posture, recent
   lessons, and North Star if resuming this work.
2. Treat the local slice and `v3.3.0` publication as complete. Any future
   provider, installed-host, release, tag, Cautilus, issue-write, or publish
   work needs its own explicitly gated phase.
3. Do not infer provider or broader cross-host behavior from this closeout.

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
- [Published release record](../charness-artifacts/release/latest.md)
- [Release notes](../charness-artifacts/release/v3.3.0-notes.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Session retro](../charness-artifacts/retro/2026-08-06-session-retro.md)
- [North Star](./design-north-star.md)

- Refresh kept: the exact [next-goal path](../charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md), published-head address, CI readback command, and runtime/mutation first actions because each changes the next operator's first move.
- Refresh non-claims: provider freshness, private consumer/provider roundtrip,
  live-agent behavior, optional `nose` proof, and Cautilus execution remain
  unproven or out of scope; see the [completed goal](../charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md).
