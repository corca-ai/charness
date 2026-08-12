# Charness Handoff

## Workflow Trigger

- Run the `issue` workflow to re-inventory the remaining open tracker items and
  select a new bounded scope. The five-issue repair sequence is complete.

## Continuation Capability

- [Issue closeout discipline](../skills/public/issue/references/closeout-discipline.md) — owns the per-issue carrier, behavioral disposition, and tracker-readback floor.
- [Release surface record](../charness-artifacts/release/latest.md) — owns public release, distinct-channel, and installed-readback evidence for the current release.

## Current State

- [Five-issue repair goal](../charness-artifacts/goals/2026-08-12-repair-quality-planner-and-closeout-surface.md) — owns the completed local fixes and their per-slice proof.
- [Published release record](../charness-artifacts/release/latest.md) — holds the verified branch/tag, GitHub release, HTTP observation, release quality, fresh-checkout probes, and installed `version`/`doctor` readback.
- [Post-publication closeout critique](../charness-artifacts/critique/2026-08-12-post-publication-issue-closeout-carriers.md) — owns the independently reviewed manual carriers for [#603](https://github.com/corca-ai/charness/issues/603), [#604](https://github.com/corca-ai/charness/issues/604), [#581](https://github.com/corca-ai/charness/issues/581), [#594](https://github.com/corca-ai/charness/issues/594), and [#593](https://github.com/corca-ai/charness/issues/593); every carrier and GitHub readback verified `CLOSED`.
Refresh kept: the published-release proof and the per-issue closure evidence because they delimit the completed scope.

Refresh non-claims: hosted CI, consumer-runtime behavior, and provider-backed adapter execution are not implied by the release or local tests.

## Next Session

1. Use the [issue workflow](../skills/public/issue/SKILL.md) to read the current open-issue inventory from GitHub before choosing another repair scope.
2. Treat the release-preflight ordering improvement in the [session retro](../charness-artifacts/retro/2026-08-12-session-retro.md) as a valid deferred follow-up, not an active change; if selected, start with the `release` workflow and keep the quality gate unchanged.

## Discuss

- No new product decision is pending. Do not treat the local-only closeout
  dispositions as hosted consumer or provider proof.

## References

- [Session retro](../charness-artifacts/retro/2026-08-12-session-retro.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
