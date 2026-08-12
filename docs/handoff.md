# Charness Handoff

## Workflow Trigger

- Run the `issue` closeout workflow in this order: [#603](https://github.com/corca-ai/charness/issues/603) → [#604](https://github.com/corca-ai/charness/issues/604) → [#581](https://github.com/corca-ai/charness/issues/581) → [#594](https://github.com/corca-ai/charness/issues/594) → [#593](https://github.com/corca-ai/charness/issues/593).
  Re-read each tracker record first; publication is proven, but closure remains
  an issue-owned irreversible boundary. Begin with source reads and draft
  validation only: a PR or direct-commit carrier needs a new phase-scoped push
  grant; a manual close is allowed only after that issue's closeout floor and
  behavioral disposition are recorded.

## Continuation Capability

- [Issue closeout discipline](../skills/public/issue/references/closeout-discipline.md) — owns the per-issue carrier, behavioral disposition, and tracker-readback floor.
- [Release surface record](../charness-artifacts/release/latest.md) — owns public release, distinct-channel, and installed-readback evidence for the current release.

## Current State

- [Five-issue repair goal](../charness-artifacts/goals/2026-08-12-repair-quality-planner-and-closeout-surface.md) — owns the completed local fixes and their per-slice proof; it deliberately did not close tracker issues before publication.
- [Published release record](../charness-artifacts/release/latest.md) — holds the verified branch/tag, GitHub release, HTTP observation, release quality, fresh-checkout probes, and installed `version`/`doctor` readback.
- [Issue #603](https://github.com/corca-ai/charness/issues/603), [#604](https://github.com/corca-ai/charness/issues/604), [#581](https://github.com/corca-ai/charness/issues/581), [#594](https://github.com/corca-ai/charness/issues/594), and [#593](https://github.com/corca-ai/charness/issues/593) — remain open; a post-publication carrier must bind each issue, with an individual behavioral disposition and GitHub `CLOSED` readback.
Refresh kept: the published-release proof and the five issue-owned closure boundaries because they determine the next workflow.

Refresh non-claims: hosted CI, consumer-runtime behavior, provider-backed adapter execution, and tracker closure are not implied by the release or local tests.

## Next Session

1. Re-read [#603](https://github.com/corca-ai/charness/issues/603), [#604](https://github.com/corca-ai/charness/issues/604), [#581](https://github.com/corca-ai/charness/issues/581), [#594](https://github.com/corca-ai/charness/issues/594), and [#593](https://github.com/corca-ai/charness/issues/593) in that order for their current bodies, comments, and state.
2. For each issue, draft and validate its carrier plus behavioral disposition under the [issue closeout discipline](../skills/public/issue/references/closeout-discipline.md). Do not publish a PR/direct-commit carrier without a new phase-scoped push grant; mutate manually only when that issue's closeout floor is met.
3. After each permitted mutation, independently read back GitHub `CLOSED` and record that issue's final disposition. [Issue closeout discipline](../skills/public/issue/references/closeout-discipline.md) specifies the required evidence.
4. [Published release record](../charness-artifacts/release/latest.md) supplies public-release evidence that a closeout carrier may cite without restating.

## Discuss

- No new product decision is pending. If tracker readback exposes a live residue
  for any selected issue, leave that issue open and record the exact disposition
  instead of treating the release as a substitute for closure evidence.

## References

- [Session retro](../charness-artifacts/retro/2026-08-12-session-retro.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
