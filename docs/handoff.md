# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather`.

## Current State

- Current shipped release is `v0.7.9`; local `main` carries unpushed bug-pattern
  hardening commits.
- Current bug-pattern sibling scan added `check-current-pointer-writes`,
  migrated direct `latest.*` writers to a symlink-safe helper, and moved two
  standing Python scans onto git-visible file listing.
- Mutation #189 is closed; mutation sampling/score, critique artifact,
  read-only quality, and shell markdown/link/secret/shell gates fail closed on
  discovery, manifest, or scan-staging failures.
- Release publishing now fails closed when unreleased-path diff, real-host proof
  config, previous-tag base-ref lookup/fetch, or post-create verification fails.
- Usage episodes are configured but disabled; validation should report
  `disabled`, not `no_adapter`.
- README first-touch routing moved to [workflow routes](./workflow-routes.md);
  [docs/cli-reference.md](./cli-reference.md) remains generated reference.

## Next Session

1. Keep usage episodes disabled until maintainers intentionally opt into local
   runtime capture.
2. Copy-heavy repo/home/plugin tests are now guarded as `release_only`; if pytest temp looks large,
   first separate retained release/full-test sessions from current pre-push work.
3. Keep PR CI mirroring paused unless the maintainer changes policy; local
   pre-push plus scheduled mutation deeper-check remain the current stance.
4. The named release suppression queue is clear through post-create verification;
   next work is a completion audit for remaining bug-pattern surfaces.
5. `_release_base_ref()` lookup/fetch and post-create release visibility failures
   now fail closed with recovery artifacts or no-mutation boundaries.

## Discuss

- Mutation selection lessons: sampler predicates must be at least as strict as
  fatal downstream closeout predicates, and runtime is executable mutants times
  selected test command cost, not just file count.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets; `filelock`
  plus `pytest-xdist`; seed-cache LRU eviction; usage
  episodes; CLI docs ownership; release proof suppression.

## References

- [charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md](../charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md):
  mutation #189 survivor and subprocess coverage RCA.
- [charness-artifacts/debug/2026-05-22-mutation-changed-diff-suppression.md](../charness-artifacts/debug/2026-05-22-mutation-changed-diff-suppression.md):
  mutation sampler changed-file diff fail-closed RCA and proof.
- [shell git file-listing](../charness-artifacts/debug/2026-05-22-shell-file-listing-suppression.md)
  and [find collector](../charness-artifacts/debug/2026-05-22-shell-find-collector-suppression.md):
  shell gate fail-closed RCAs and proof.
- [charness-artifacts/debug/2026-05-22-release-diff-failure-suppression.md](../charness-artifacts/debug/2026-05-22-release-diff-failure-suppression.md),
  [real-host config suppression](../charness-artifacts/debug/2026-05-22-release-real-host-config-suppression.md),
  [base-ref fallback suppression](../charness-artifacts/debug/2026-05-22-release-base-ref-fallback-suppression.md),
  and [post-create verification suppression](../charness-artifacts/debug/2026-05-22-release-post-create-verification-suppression.md):
  release proof suppression RCAs and fail-closed proof.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md): current quality posture.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
