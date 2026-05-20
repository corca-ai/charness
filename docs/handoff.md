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

- Current local slice resolves #183's mutation-testability regression. RCA:
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
  coverage risk were fixed. #183 remains open until the hosted mutation workflow
  succeeds on the pushed fix.
- Public release `v0.7.7`; release is still needed after hosted proof.

## Next Session

1. If picked up mid-run, confirm [cosmic-ray.toml](../cosmic-ray.toml) is
   restored to its default non-release test command, rerun changed-surface
   closeout if needed, then commit and push.
2. After push, watch the hosted mutation workflow. #183 is closable only when
   the full hosted run succeeds and the issue state verifies as `CLOSED`.
3. Cut/publish the next Charness release after hosted proof so plugin users get
   the updated quality/testability contract.

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
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md):
  current release surface.
- [.github/workflows/mutation-tests.yml](../.github/workflows/mutation-tests.yml): #183 validation workflow.
