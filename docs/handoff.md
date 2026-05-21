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
- Latest quality slices promoted `inventory-gitignore-scan-hygiene` into
  `run-quality`, kept copy-heavy tests out of ordinary pre-push, and refreshed
  [quality latest](../charness-artifacts/quality/latest.md).
- Usage episodes are now intentionally configured but disabled in
  [.agents/usage-episodes-adapter.yaml](../.agents/usage-episodes-adapter.yaml).
  Validation should report `disabled`, not `no_adapter`.

## Next Session

1. Decide the Charness-owned usage-episode vocabulary for
   `selected_job`, `core_action`, `agent_action.surface`, `first_value_ref`,
   and `feedback_signal`; then flip `enabled: true` only with the runtime
   emitter or an explicit follow-up contract for
   `.charness/usage-episodes/usage_episode.jsonl`.
2. For docs ergonomics, do not add a broad gate yet: first separate generated
   reference noise ([docs/cli-reference.md](./cli-reference.md)) from
   first-touch prose, then reduce [README.md](../README.md) by moving
   route/procedure detail to the owning docs while
   preserving Quick Start and Skill Map discoverability.
3. Copy-heavy repo/home/plugin tests are now guarded as `release_only` by
   [check_test_repo_copy_invariants.py](../scripts/check_test_repo_copy_invariants.py);
   if pytest temp looks large,
   first separate retained release/full-test sessions from current pre-push work.
4. Keep PR CI mirroring paused unless the maintainer changes policy; local
   pre-push plus scheduled mutation deeper-check remain the current stance.
5. The remaining release-side caveat is real-host verification for the
   integrations/control-plane seam recorded in
   [release latest](../charness-artifacts/release/latest.md).

## Discuss

- Mutation selection lessons: sampler predicates must be at least as strict as
  fatal downstream closeout predicates, and runtime is executable mutants times
  selected test command cost, not just file count.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets;
  `filelock` plus `pytest-xdist`; seed-cache LRU eviction; subprocess
  coverage for CLI-only mutation targets; usage-episode vocabulary/emitter;
  README vs generated CLI reference docs ownership.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md):
  mutation scope-gap RCA, detection gap, sibling search, and prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
