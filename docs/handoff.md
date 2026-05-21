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

- Current shipped slice resolves #183's mutation-testability regression; #183 is
  verified closed and release `v0.7.8` is published.
- Python mutation sampling now uses coverage contexts and Cosmic Ray work-item
  probes, rewrites the selected sample's pytest nodeids, enforces workload
  budgets by executable mutants and nodeids, and treats partial timeout success
  as diagnostic only. Details: [debug latest](../charness-artifacts/debug/latest.md).
- Follow-up hardening expands Python sampling to root CLI/bootstrap, immediate
  `scripts/*.py`, and skill helper scripts, with pool counts in the sample manifest.
- JS mutation is a separate StrykerJS command-runner slice using
  `npm run test:agent-runtime` for [agent runtime modules](../scripts/agent-runtime),
  deterministic target sampling, mutant-count weights, and blocking
  `NoCoverage`, timeout, stale-report, and missing-report signals.
- Default deterministic quality/coverage no longer depends on or cleans up
  ambient `agent-browser` orphan daemons. Real runtime hygiene remains an
  explicit opt-in gate (`CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE=1` or selected
  labels); when explicitly run, hygiene failure still triggers cleanup.

## Next Session

1. If picked up for this slice, treat #183 as closed and released unless a new
   GitHub run regresses. Re-check `gh issue view 183`,
   `gh run view 26196843109`, and `gh release view v0.7.8` before reopening.
2. The remaining release-side caveat is real-host verification for the
   integrations/control-plane seam recorded in
   [release latest](../charness-artifacts/release/latest.md); it is not a #183
   mutation-testability blocker.
3. Watch the first hosted mutation run after the JS-native agent-runtime slice
   lands. A focused local Stryker full run on [contract-versions.mjs](../scripts/agent-runtime/contract-versions.mjs)
   now reports 100% (5 killed) from Stryker's temp sandbox.

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
  `filelock` + `pytest-xdist`; sibling imports via runtime bootstrap; seed-cache
  LRU eviction; subprocess coverage for CLI-only mutation targets.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md):
  mutation scope-gap RCA, detection gap, sibling search, and prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
