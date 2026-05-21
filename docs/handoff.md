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

- Current shipped release is `v0.7.9`; local `main` is clean with `origin/main`.
- Current bug-pattern sibling scan added `check-current-pointer-writes`,
  migrated direct `latest.*` writers to a symlink-safe helper, and moved two
  standing Python scans onto git-visible file listing.
- Usage episodes are now intentionally configured but disabled in
  [.agents/usage-episodes-adapter.yaml](../.agents/usage-episodes-adapter.yaml).
  Validation should report `disabled`, not `no_adapter`.
- Product success and AI/ML engineering baselines are now proposed in
  [product success metrics](./product-success-metrics.md) and
  [AI/ML engineering patterns](./ai-ml-engineering-patterns.md); runtime
  `slice_closeout` emission landed through follow-up
  [#188](https://github.com/corca-ai/charness/issues/188).
- README first-touch docs ergonomics were trimmed: detailed project/existing
  repo routing moved to [workflow routes](./workflow-routes.md), while
  [docs/cli-reference.md](./cli-reference.md) remains generated reference
  material.

## Next Session

1. Usage-episode vocabulary baseline and the `slice_closeout` emitter are now
   documented in [product success metrics](./product-success-metrics.md). Keep
   [.agents/usage-episodes-adapter.yaml](../.agents/usage-episodes-adapter.yaml)
   at `enabled: false` until maintainers intentionally opt into local runtime
   capture.
2. Copy-heavy repo/home/plugin tests are now guarded as `release_only`; if pytest temp looks large,
   first separate retained release/full-test sessions from current pre-push work.
3. Keep PR CI mirroring paused unless the maintainer changes policy; local
   pre-push plus scheduled mutation deeper-check remain the current stance.
4. The remaining release-side caveat is real-host verification for the
   integrations/control-plane seam recorded in
   [release latest](../charness-artifacts/release/latest.md).

## Discuss

- Mutation selection lessons: sampler predicates must be at least as strict as
  fatal downstream closeout predicates, and runtime is executable mutants times
  selected test command cost, not just file count.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets;
  `filelock` plus `pytest-xdist`; seed-cache LRU eviction; subprocess
  coverage for CLI-only mutation targets; usage-episode vocabulary/emitter;
  generated CLI reference docs ownership; mutation sample/test-command coupling
  and release diff-failure suppression surfaced by sibling scan.

## References

- [charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
