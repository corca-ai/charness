# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the [closeout goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md) and [release record](../charness-artifacts/release/latest.md); the closeout/release slice is complete unless a new receipt or follow-up boundary is explicitly opened.
- First read the [current quality posture](../charness-artifacts/quality/latest.md), [goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md), [recent lessons](../charness-artifacts/retro/recent-lessons.md), and [North Star](./design-north-star.md).

## Continuation Capability

- Keep local, provider, cross-host, remote-CI, release, Cautilus, and issue claims separate.
- The closeout goal and its execution contract own packet identity, pointer freshness, pre-review authoring order, and retro-to-handoff wiring.
- The `v3.4.0` release phase recorded its pre-push quality gate, tag/publication, distinct HTTP observer, install refresh, version/doctor readbacks, and clean post-publish commit boundary.

## Current State

- The closeout bundle and retro-to-handoff validator are included in release commit `7bf3893b` for `v3.4.0`; the locked local proof target is recorded separately at [the local proof ledger](../charness-artifacts/probe/2026-08-06-closeout-local-proof.json), and the final claims/disposition identity is bound by the tracked critique carrier.
- The goal-bound retro is persisted at [the retro artifact](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md); its citation and recurrence-marker wiring, final claims review, and release critique are recorded. The post-publish verification receipt is [the release observer probe](../charness-artifacts/probe/2026-08-06-v3.4.0-release-observer.json).
- The publish-state claim below remains a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`; it is not a current version or tag claim. The release record separately binds `v3.4.0` to tag SHA `7bf3893b`, and the post-publish bookkeeping is committed at `c34b3dc0`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Read the [closeout goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md), its [quality record](../charness-artifacts/quality/latest.md), [release record](../charness-artifacts/release/latest.md), and [release notes](../charness-artifacts/release/v3.4.0-notes.md).
2. Treat `v3.4.0` publication, the unauthenticated HTTP release observation, install refresh, `charness version`, and `charness doctor` readbacks as completed receipts; do not rerun publication for this slice.
3. Keep provider, installed-consumer beyond the recorded readback, remote-CI, host-window, Cautilus, and future release claims separate; any new proof needs its own observer/channel and artifact.

## Discuss

- The user-authorized `v3.4.0` push/release completed only after the local gates, tracked critique, notes, tag/publication, and distinct readbacks; any later release is a new boundary.
- Do not run Cautilus, provider roundtrips, or live-agent proof without a separate explicit boundary.

## References

- [Active goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md)
- [Execution contract](../charness-artifacts/spec/2026-08-06-closeout-bundle-execution-contract.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md)
- [Release record](../charness-artifacts/release/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [North Star](./design-north-star.md)

- [Refresh kept](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md): the active closeout goal, prior published-state identity,
  local-gate boundary, and exact retro recurrence obligations because each
  changes the next action ([active goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md),
  [execution contract](../charness-artifacts/spec/2026-08-06-closeout-bundle-execution-contract.md),
  [goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md)).
- [Refresh non-claims](../charness-artifacts/release/latest.md): new release publication, remote CI, provider freshness,
  cross-host runtime, live-agent behavior, Cautilus execution, and issue writes
  remain unclaimed ([release record](../charness-artifacts/release/latest.md),
  [handoff](./handoff.md)).
