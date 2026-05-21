# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
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
- Mutation #189 is closed on GitHub after the worktree/eval-registry survivor
  fixes and subprocess coverage collection; the remaining mutation watch item is
  fail-closed changed-file discovery when `git diff` cannot compute the sample
  delta.
- Release publishing now fails closed when unreleased-path diff, real-host proof
  config, or previous-tag base-ref lookup/fetch fails; remaining proof caveat is
  post-create verification recovery after external mutation.
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
4. Mutation changed-file eligibility is still the active watch item: add direct
   tests for the current-pointer slice until a `b882398..HEAD` sample reports
   no file-coverage-floor or mutation-line changed-file exclusions.
5. The remaining release-side caveat is post-create verification recovery after
   tag push and release creation; `_release_base_ref()` lookup/fetch failures now
   fail closed.

## Discuss

- Mutation selection lessons: sampler predicates must be at least as strict as
  fatal downstream closeout predicates, and runtime is executable mutants times
  selected test command cost, not just file count.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets; `filelock`
  plus `pytest-xdist`; seed-cache LRU eviction; changed-file mutation
  eligibility; usage episodes; CLI docs ownership; release proof suppression.

## References

- [charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md](../charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md):
  mutation #189 survivor and subprocess coverage RCA.
- [charness-artifacts/debug/2026-05-22-release-diff-failure-suppression.md](../charness-artifacts/debug/2026-05-22-release-diff-failure-suppression.md),
  [real-host config suppression](../charness-artifacts/debug/2026-05-22-release-real-host-config-suppression.md),
  and [base-ref fallback suppression](../charness-artifacts/debug/2026-05-22-release-base-ref-fallback-suppression.md):
  release proof suppression RCAs and fail-closed proof.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
