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

- Current shipped release is `v0.7.8`; #183's mutation-testability regression is
  closed unless a new hosted run regresses.
- Latest quality slice promoted `inventory-gitignore-scan-hygiene` into
  `run-quality` and refreshed [quality latest](../charness-artifacts/quality/latest.md).
- Usage episodes are now intentionally configured but disabled in
  [.agents/usage-episodes-adapter.yaml](../.agents/usage-episodes-adapter.yaml).
  Validation should report `disabled`, not `no_adapter`.

## Next Session

1. Keep PR CI mirroring paused unless the maintainer changes policy; local
   pre-push plus scheduled mutation deeper-check remain the current stance.
2. Before enabling usage episodes, define the Charness-owned vocabulary for
   `selected_job`, `core_action`, `agent_action.surface`, `first_value_ref`,
   and `feedback_signal`; then flip `enabled: true` and add or wire a runtime
   emitter for `.charness/usage-episodes/usage_episode.jsonl`.
3. For standing-test economics, investigate whether packaging/tool tests still
   materialize full repo/home/plugin copies or merely leave retained pytest temp
   sessions; reduce repeated nested CLI proof before changing budgets.
4. The remaining release-side caveat is real-host verification for the
   integrations/control-plane seam recorded in
   [release latest](../charness-artifacts/release/latest.md).

## Discuss

- Lesson: a sampler predicate must be at least as strict as the downstream
  score/closeout predicate when the downstream signal is fatal.
- Fresh-eye valid-but-defer: make missing/malformed sample manifests a full-run
  invariant if the summary is reused outside the current workflow shape; monitor
  long focused pytest commands before adding another abstraction.
- Lesson: mutation runtime is executable mutants times selected test command
  cost. File caps are not workload caps.
- Lesson: command-runner JS mutation has coarser test selection than the Python
  coverage-derived sampler; budget it separately and treat `NoCoverage` as a
  scope gap.
- Watch list (deferred): Yarn Berry hook idiom; pnpm+lefthook stale snippets;
  `filelock` + `pytest-xdist`; seed-cache LRU eviction; subprocess coverage
  for CLI-only mutation targets; usage-episode vocabulary and emitter design.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md):
  mutation scope-gap RCA, detection gap, sibling search, and prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
