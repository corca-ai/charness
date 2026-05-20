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

- Current local slice hardens agent-browser runtime hygiene after a green quality/push cycle
  still left a PPID=1 browser daemon tree. RCA: [debug latest](../charness-artifacts/debug/latest.md).
- `run-quality.sh` now starts with barriered `agent-browser-runtime-baseline`
  cleanup and ends with `agent-browser-runtime-hygiene` using
  `agent_browser_runtime_guard.py --assert-no-orphans`; cleanup fails if a
  stale launcher recreates a daemon after the cleanup snapshot.
- `check_cli_skill_surface.py` blocks direct risky `agent-browser` probes in
  `cli_skill_surface_probe_commands`; web-fetch closes its named browser
  session after render/network recon; doctor lock payloads truncate volatile
  command output.
- Public release `v0.7.6`. No version bump pending unless the next release
  slice decides to publish this hardening immediately.
- Prior pushed slice `f14a1df` taught public `quality` structure-first testability.
  Mutation follow-up #183 remains open until GitHub proves corrected semantics.

## Next Session

1. If picked up mid-run, finish generated-surface sync, changed-surface tests, full closeout, and pre-push.
2. Confirm the new `agent-browser-runtime-hygiene` phase leaves
   `orphan_daemon_count=0` after the full standing gate.
3. Continue #183 watch if needed: next summary should show covered sample pool,
   excluded changed files, separated scope gaps, executable-mutant completion,
   and no under-proven `PASS-partial`.

## Discuss

- Lesson: pytest cleanup is not a quality-gate lifecycle contract; external runtimes need gate ownership.
- Similar-pattern scan found arbitrary adapter probe commands and raw doctor
  lock output as adjacent risks. This slice adds agent-browser-specific
  enforcement first; broader runtime-family metadata is deferred until another
  external runtime shows the same pressure.
- Watch list (deferred): Yarn Berry hook idiom; pnpm+lefthook stale snippets;
  `filelock` + `pytest-xdist`; sibling imports via runtime bootstrap; seed-cache LRU eviction.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md):
  agent-browser runtime hygiene RCA, detection gap, sibling search, and
  prevention.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md):
  current quality posture and commands for this slice.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md):
  current release surface.
- [.github/workflows/mutation-tests.yml](../.github/workflows/mutation-tests.yml):
  mutation workflow for the separate #183 validation thread.
