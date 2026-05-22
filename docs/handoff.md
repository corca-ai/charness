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

- Current shipped release is `v0.7.10`; local `main` is 5 commits ahead of
  origin pending push.
- Bug-pattern sibling scan complete: helper, scanner, gitignore-aware standing
  scans, and the adapter-resolved hitl writer migration all landed.
- Issue #190 (mutation regression on main) resolved: nested pytest probe was
  inheriting `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` from the parent step env;
  the vulnerable test now scrubs both keys.
- Generated reference docs separated under `docs/generated/` with an enforced
  GENERATED header.
- PR CI mirror absence documented in
  [operating-contract.md Local Enforcement Policy](./conventions/operating-contract.md)
  as intended under the single-maintainer push model.
- Deferred decision D19 records the current-pointer scanner generalization
  posture (defer until a second adapter-resolved sibling appears).
- Usage episodes adapter remains `enabled: false`. Spec for completing the
  H-LAM/T loop (session grouping + T signal) landed at
  [charness-artifacts/spec/usage-episodes-h-lam-t-completion.md](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md);
  implementation is split into two slices not yet executed.

## Next Session

1. Implement Slice A from the usage-episodes spec: schema extension
   (`session_id`, `t_evidence`, `classification_skipped`) plus
   `classify_t_signal` helper, emitter wiring, validator relaxation
   (`no_records` warning), and fixture updates — all in one atomic commit.
2. Implement Slice B from the same spec. Start with Step 0 (resolve Codex
   `hooks.json` vs `config.toml` precedence as a Fixed Decision via the
   existing [codex hooks gather](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md)),
   then build the SessionStart hook script, install lib, and
   `charness session-capture status` subcommand.
3. After both slices ship, flip
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
