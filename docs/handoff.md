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

- **v0.10.0 published** (GitHub release + tag, all surfaces synced, no drift);
  ships the #226 reviewer-tier policy. **Open:** release-time real-host proof
  (Cautilus install/doctor on a clean machine) is required and NOT yet run — see
  [release latest](../charness-artifacts/release/latest.md).
- **#230 + #229 CLOSED** (this session, via `achieve`): closed the lighter-
  self-substitution pattern across achieve/issue/release closeouts and the
  Before-phase anti-anchoring half, plus the markdown-hook flood (Waste 2)
  and the broad-gate push redundancy (Waste 3). Achieve After-phase now
  mechanically refuses `complete` without a real retro artifact + host-log
  probe; issue `verify-closeout` requires a `Critique:` carrier-body line
  for bug/feature/deferred-work; `publish_release.py` requires
  `--critique-artifact` or `--critique-blocked`; per-commit markdown stdout
  shrank from 50.6KB to 143 bytes. Goal artifact:
  [2026-05-28-230-229-self-substitution-pattern](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md).
  Closeout retro: [2026-05-28-230-229-achieve-goal-closeout](../charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md).
- **#226 CLOSED** (prior session, via `achieve`): centralized a portable
  fresh-eye reviewer-tier policy. Goal artifact:
  [2026-05-27-226-reviewer-tier-policy](../charness-artifacts/goals/2026-05-27-226-reviewer-tier-policy.md).
- **#219 still OPEN**: the annotation-union filter fix (`a0b8de0e`) is on `main`;
  waiting for the next scheduled mutation run to validate + auto-close. Do not
  hand-close. (#224, #225 closed.) See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-224-219-mutation-annotation-filter.md).

## Next Session

1. **Push the #230 + #229 commits.** The 7-commit branch is ahead of
   `origin/main` and locally green. The new pre-push hook will classify
   this very push as `full-gate-required` (touches `.githooks/`, `scripts/`,
   `skills/`, `tests/`). Note: a preexisting find-skills inventory schema
   drift (integration IDs renamed but file basenames unchanged in
   [integrations/tools](../integrations/tools/)) will fire under
   `validate-current-pointer-freshness` and likely block the push; either
   rename the JSON files to match the new IDs or teach the validator to
   follow the id-to-path mapping. See the goal artifact's Off-Goal
   Findings section.
2. **#233 — closeout-gate hardening (F1 binding + F2 user-message
   surfacing).** Filed during this session's post-closeout correction.
   Bundles the slice 3 helper accepting stale unrelated retro files with
   the layer-up pattern of prescribed-skill conclusions not being
   narrated to the user. Single design slice can address both with one
   `check_complete_evidence` extension + one achieve After-phase
   lifecycle contract update.
3. **Confirm Codex host smoke** of the After-phase gate when a Codex
   session is convenient. The gate is host-agnostic at the script level
   (only `git`, `os.stat`, and the portable shared helper) but live-refusal
   was only exercised under Claude Code this session.
4. **#227** — larger user-requested survey-reliability retro; scope partly in
   ceal. Run `spec` first to carve the charness-only part (turn-policy
   execution-vs-approval, source-reuse, external-write verification taxonomy,
   template fidelity) before `impl`.
5. **#184/#185** remain deferred product/AI-ML direction work.
6. **Mutation residuals** (only if the scheduled gate goes red on HEAD; not
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
