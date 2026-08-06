# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the [active runtime-evidence goal](../charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md), then continue with `achieve` for its final closeout if it is not complete.
- First read the [current quality posture](../charness-artifacts/quality/latest.md), [goal-bound retro](../charness-artifacts/retro/2026-08-06-runtime-evidence-and-final-boundary.md), [recent lessons](../charness-artifacts/retro/recent-lessons.md), and [North Star](./design-north-star.md).
- Release `v3.3.0` is already published; no new release, tag, push, or issue phase is part of this baton.

## Continuation Capability

- Keep local quality, installed-host, provider, cross-host, remote-CI, release, Cautilus, and issue claims separate.
- The goal's host packet is the source for `nose` receipts; the quality and retro records own interpretation and lessons.
- Any provider refresh, cross-host runtime cohort, release, push, Cautilus, or external write needs its own explicitly gated phase.

## Current State

- Runtime A/B evidence is retained: isolated median `6531 ms` versus same-affinity synthetic contention median `10463 ms`; keep the `15.500s` budget unchanged.
- The installed host successfully invoked the manifest-supported `nose-cli-installer.sh` route and reports `nose 0.20.0` ready; support sync is integration-only and clone findings are advisory.
- Source `8047a614…` and installed checkout `7eed13ec…` differ; no source/install parity claim is made. The clone baseline remains stamped under `nose 0.19.0`.
- The bounded closeout reviewer received the packet, confirmed its substantive claims, and returned a clean boundary fingerprint. A final readiness review read the repaired surfaces, returned `PASS`, and returned a clean boundary fingerprint; the goal-bound retro and current-pointer refresh are recorded.

## Next Session

1. Read the goal frame, its evidence packet, current quality record, and goal-bound retro; verify the goal status before taking another action.
2. Treat runtime threshold retuning, provider freshness, live-agent behavior, remote CI, and cross-host evidence as deferred non-claims.
3. If any of those boundaries is pursued, activate a separate goal and obtain its own observer and evidence channel.

## Discuss

- No decision is needed to read or measure locally. Stop before Cautilus, release/tag/version work, provider writes, issue writes, or another push.
- If a future runtime sample is mixed, preserve the current budget and record uncertainty rather than converting an advisory signal into a blocker.

## References

- [Active goal](../charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md)
- [Runtime and installed-host packet](../charness-artifacts/probe/2026-08-06-runtime-evidence-and-nose.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Goal-bound retro](../charness-artifacts/retro/2026-08-06-runtime-evidence-and-final-boundary.md)
- [Release record](../charness-artifacts/release/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [North Star](./design-north-star.md)

- Refresh kept: the active goal path, runtime disposition, installed `nose` version and baseline skew, source/install SHA distinction, and deferred boundary list because each changes the next operator's first move.
- Refresh non-claims: provider freshness, private consumer/provider roundtrip, live-agent behavior, cross-host runtime behavior, remote CI, release parity, Cautilus execution, and issue state beyond the already-published release record.
