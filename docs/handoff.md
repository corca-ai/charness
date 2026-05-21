# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and
  `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md). Before closeout, read
  [operating contract](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather`.

## Current State

- Current shipped slice resolves #183's mutation-testability regression. RCA:
  [debug latest](../charness-artifacts/debug/latest.md).
- Mutation sampling now runs coverage with test-function contexts, probes Cosmic
  Ray work items, keeps only files whose non-skipped mutable lines are covered,
  and rewrites the mutation `test-command` to the pytest nodeids that covered
  the selected sample. It also enforces executable-mutant, per-file mutant, and
  pytest-nodeid workload budgets; file count alone is not treated as a runtime
  budget.
- Mutation scoring now treats `PASS-partial` as diagnostic only, exits non-zero
  for partial timeout success, and blocks recovery when changed files were
  excluded before mutation by coverage, mutation-line, or selection-budget
  filters.
- Workflow dependency setup now uses
  [packaging/mutation-requirements.txt](../packaging/mutation-requirements.txt)
  instead of ambient inline installs.
- Fresh-eye reviewers judged the repo's testability posture sufficient for this
  slice after the probe config leakage, workload-budget bug, and import-only
  coverage risk were fixed. Hosted run `26195933679` then found real sanitizer
  survivors; local replay and hosted run `26196843109` pass after focused test
  strengthening.
- GitHub issue #183 is verified `CLOSED` as of `2026-05-21T00:01:10Z`; public
  release `v0.7.8` is published.

## Next Session

1. If picked up for this slice, treat #183 as closed and released unless a new
   GitHub run regresses. Re-check `gh issue view 183`,
   `gh run view 26196843109`, and `gh release view v0.7.8` before reopening.
2. The remaining release-side caveat is real-host verification for the
   integrations/control-plane seam recorded in
   [release latest](../charness-artifacts/release/latest.md); it is not a #183
   mutation-testability blocker.

## Discuss

- Lesson: a sampler predicate must be at least as strict as the downstream
  score/closeout predicate when the downstream signal is fatal.
- Fresh-eye valid-but-defer: make missing/malformed sample manifests a full-run
  invariant if the summary is reused outside the current workflow shape; monitor
  long focused pytest commands before adding another abstraction.
- Lesson: mutation runtime is executable mutants times selected test command
  cost. File caps are not workload caps.
- Watch list (deferred): Yarn Berry hook idiom; pnpm+lefthook stale snippets;
  `filelock` + `pytest-xdist`; sibling imports via runtime bootstrap; seed-cache
  LRU eviction.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md):
  mutation scope-gap RCA, detection gap, sibling search, and prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
