# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the [active closeout goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md), then continue with `achieve` for its final claims review and release preflight.
- First read the [current quality posture](../charness-artifacts/quality/latest.md), [goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md), [recent lessons](../charness-artifacts/retro/recent-lessons.md), and [North Star](./design-north-star.md).

## Continuation Capability

- Keep local, provider, cross-host, remote-CI, release, Cautilus, and issue claims separate.
- The closeout goal and its execution contract own packet identity, pointer freshness, pre-review authoring order, and retro-to-handoff wiring.
- The final release phase still needs its own pre-push gate, distinct remote observer/channel, release readback, and clean commit-boundary evidence.

## Current State

- The closeout bundle and retro-to-handoff validator are committed through `0be77d37`; the deterministic pre-lock result is time-bound to that commit. This refreshed handoff has passed its named wiring, handoff, pointer, and targeted fixture checks, but the final packet rebinding and verification lock remain open.
- The goal-bound retro is persisted at [the retro artifact](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md); its citation and recurrence-marker wiring is locally validated, while the final closeout identity is still provisional until the verification lock runs.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`; it is not a version or tag claim. The release record separately binds `v3.3.0` to its tag SHA, and neither record claims that this new closeout goal has been released.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Read the [active goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md), its [quality record](../charness-artifacts/quality/latest.md), and [goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md).
2. Run the distinct claims/disposition review and verification-locked closeout; preserve `recurrence-class: release-proof-identity-churn` and `recurrence-class: closeout-diagnostic-visibility` in the disposition evidence.
3. Only after local gates pass, derive the release version/carrier, run the conditioned push, verify remote CI through a different observer/channel, publish, and read the release back distinctly.

## Discuss

- The user-authorized final push/release remains conditional on every local and release gate; stop before any external effect when a gate, version, carrier, or distinct observer is unresolved.
- Do not run Cautilus, provider roundtrips, or live-agent proof without a separate explicit boundary.

## References

- [Active goal](../charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md)
- [Execution contract](../charness-artifacts/spec/2026-08-06-closeout-bundle-execution-contract.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Goal-bound retro](../charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md)
- [Release record](../charness-artifacts/release/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [North Star](./design-north-star.md)

Refresh kept: the active closeout goal, prior published-state identity, local-gate boundary, and exact retro recurrence obligations because each changes the next action.
Refresh non-claims: new release publication, remote CI, provider freshness, cross-host runtime, live-agent behavior, Cautilus execution, and issue writes.
