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

- Current shipped release is `v0.7.10`; local `main` is 7 commits ahead of
  origin pending push.
- Bug-pattern sibling scan complete; the adapter-resolved hitl writer
  migration and gitignore-aware standing scans landed alongside the
  generated reference docs split under `docs/generated/`.
- Usage episodes adapter remains `enabled: false`. Slice A of the
  [H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md)
  landed in commit `33a5c57`: episode schema gained `session_id`,
  `t_evidence`, and `classification_skipped` with the conditional clause;
  the new [classify_t_signal helper](../scripts/classify_t_signal.py) runs
  the diff-rule catalog; the slice-closeout emitter attaches `session_id`
  from
  `.charness/usage-episodes/sessions/current` plus the classifier's
  `t_status`/`t_evidence` (or `classification_skipped` on skip); validator
  returns `no_records` warning when `enabled:true` with no records yet.
- Slice B (host SessionStart hook surface + `charness session-capture status`
  CLI) is not yet executed.

## Next Session

1. Implement Slice B from the usage-episodes spec. Start with Step 0
   (resolve Codex `hooks.json` vs `config.toml` precedence as a Fixed
   Decision via the existing
   [codex hooks gather](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md)),
   then build the SessionStart hook script and host-hook install library
   under `scripts/`, wire `charness init`/`charness update` to read
   `host_hooks.{claude,codex}`, and add the `charness session-capture status`
   subcommand.
2. After Slice B ships, flip
   [usage-episodes adapter](../.agents/usage-episodes-adapter.yaml)
   `enabled: true` as a separate intentional commit.

## Discuss

- Static `check-current-pointer-writes` scanner only catches string-literal
  writes; future adapter-resolved writers must adopt the helper by convention
  until D19's reopen trigger fires.
- Step-env leakage into nested test-command coverage probes is a class of bug;
  subprocess tests that build `env={**os.environ, ...}` must scrub
  workflow-controlled `MUTATION_*` keys before invoking the script under test.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets; `filelock`
  plus `pytest-xdist`; seed-cache LRU eviction; release proof suppression.

## References

- [usage-episodes H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md):
  fixed decisions and two-slice implementation plan.
- [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  Codex SessionStart/Stop/UserPromptSubmit/PreToolUse/PostToolUse hook surface.
- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
