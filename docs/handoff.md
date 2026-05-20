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
- `run-quality.sh` now starts with assert-only fail-fast
  `agent-browser-runtime-baseline` and ends with
  `agent-browser-runtime-hygiene`; both unset the orphan-ignore waiver so the
  standing gate cannot silently bless dirty runtime state.
- `check_cli_skill_surface.py` and `validate_integrations.py` block risky
  bare or wrapper-mediated `agent-browser` probes; web-fetch degrades rather
  than reports success when browser session close fails.
- Startup probes, CLI side-effect probes, and `run_cautilus_eval.py` now have
  explicit wall-clock timeouts so executable probes cannot hang a standing gate.
- Pytest sessionfinish cleanup retries agent-browser cleanup until clean or
  timeout; final `run-quality` hygiene remains the whole-gate proof.
- Public release `v0.7.6`. No version bump pending unless the next release
  slice decides to publish this hardening immediately.
- Prior pushed slice `f14a1df` taught public `quality` structure-first testability.
  Mutation follow-up #183 remains open until GitHub proves corrected semantics.

## Next Session

1. If picked up mid-run, finish generated-surface sync, changed-surface tests, full closeout, and pre-push.
2. Confirm the new baseline/final runtime hygiene phases leave
   `orphan_daemon_count=0` after the full standing gate.
3. Continue #183 watch if needed: next summary should show covered sample pool,
   excluded changed files, separated scope gaps, executable-mutant completion,
   and no under-proven `PASS-partial`.

## Discuss

- Lesson: pytest cleanup is not a quality-gate lifecycle contract; external runtimes need gate ownership.
- Similar-pattern scan found arbitrary adapter probe commands, startup probes,
  Cautilus forwarding, and raw doctor lock output as adjacent risks. This
  slice adds timeouts and agent-browser-specific lifecycle enforcement first;
  broader runtime-family metadata is deferred until another external runtime
  shows the same pressure.
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
