# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this
  file, [quality latest](../charness-artifacts/quality/latest.md), and
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- **v0.9.0 is published and verified** on `main` + tag; no version drift.
- **#226 CLOSED** (this session, via `achieve`): centralized a portable
  fresh-eye reviewer-tier policy. `high-leverage`/`standard` tier in
  [the shared fresh-eye reference](../skills/shared/references/fresh-eye-subagent-review.md)
  (no provider names); a validated `reviewer_tiers` critique-adapter field
  carries the concrete **host-plural** mapping (Codex gpt-5.5/medium/priority,
  Claude Code sonnet-4.6) in the critique adapter example + contract; `release`
  now cites the shared policy; pinned by
  [a new policy test](../tests/quality_gates/test_reviewer_tier_policy.py). Goal
  artifact: [2026-05-27-226-reviewer-tier-policy](../charness-artifacts/goals/2026-05-27-226-reviewer-tier-policy.md).
- **#219 still OPEN**: the annotation-union filter fix (`a0b8de0e`) is on `main`;
  waiting for the next scheduled mutation run to validate + auto-close. Do not
  hand-close. (#224, #225 closed.) See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-224-219-mutation-annotation-filter.md).

## Next Session

1. **#229 — immediate next slice (run `achieve` or `impl`).** Add a Before-phase
   anti-anchoring probe to `achieve` (its `lifecycle` reference): test whether a
   user-confirmed or issue-inherited value is a single point or one instance of
   a system axis (host/provider/environment) before locking the design; consider
   a matching `critique` angle. Small, fully in charness, derived from the #226
   run (a Codex-only policy nearly shipped before host-plurality was caught).
2. **#227** — larger user-requested survey-reliability retro; scope partly in
   ceal. Run `spec` first to carve the charness-only part (turn-policy
   execution-vs-approval, source-reuse, external-write verification taxonomy,
   template fidelity) before `impl`.
3. **#184/#185** remain deferred product/AI-ML direction work.
4. **Mutation residuals** (only if the scheduled gate goes red on HEAD; not
   filed as issues): real test-strength survivors #224 named (`build_payload`
   comparisons, worktree `timeout` numbers) the filter fix does not touch, and
   the latent `Annotated[...]` metadata over-skip. Re-confirm against current
   HEAD first; they may be stale.

## Discuss

- Current PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen unless
  outside PRs become recurring.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
