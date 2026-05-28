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

- **`main` is at `origin/main` (push landed).** The 22-commit batch carrying
  the #230 + #229 closeout, the handoff-chunked-routing goal, and the
  pre-push gate clearing is now upstream.
- **#230 CLOSED, #229 still OPEN.** #229 close still pending against the
  [closeout retro](../charness-artifacts/retro/2026-05-28-230-229-achieve-goal-closeout.md)
  and the
  [goal artifact](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md).
- **handoff-chunked-routing goal: shipped.** Chunker behind a deterministic
  trigger gate on `handoff`; layering miss captured in
  [chunked-routing-layering-miss](../charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md).
- **v0.10.0 published**; real-host release proof (Cautilus install/doctor on a
  clean machine) NOT yet run. See [release latest](../charness-artifacts/release/latest.md).
- **#219 still OPEN** — fix `a0b8de0e` on `main` awaiting next scheduled mutation
  run to validate + auto-close (do not hand-close). See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-224-219-mutation-annotation-filter.md).
- **Open issues**: #234, #233, #232, #229, #219, #185, #184.

## Next Session

1. **gh-close #229** — re-read the closeout retro + goal artifact and verify
   the evidence actually binds to #229 before invoking `gh issue close`
   (this is the exact failure mode #233 names; do not hand-close blind).
2. **#233 closeout-gate hardening.** One design slice extends
   `check_complete_evidence` so retro evidence binds to the completing
   goal's context (slice 3 helper currently accepts stale unrelated retros)
   and adds an achieve After-phase contract update so prescribed-skill
   conclusions get narrated to the user.
3. **#234** mutation regression on `main` — triage against current HEAD and
   the #219 filter-fix path before designing.
4. **Real-host release proof for v0.10.0** when a clean machine + Cautilus
   slot are available.
5. **Codex host smoke** of the After-phase gate — host-agnostic at the script
   level but live-refusal only exercised under Claude Code.
6. **#232** issue skill shell-quoting body corruption (`gh issue create` body path).
7. **#227** survey-reliability retro — run `spec` first to carve the
   charness-only part (ceal owns the rest).
8. **#184/#185** remain deferred product/AI-ML direction work.

## Discuss

- **setup-skill improvement candidate**: `find-skills → handoff` did not
  auto-trigger on a `@docs/handoff.md` pickup this session; the `CLAUDE.md`
  Start Here prose lost to the @-mention's "react to content" affordance.
  See
  [routing-miss retro](../charness-artifacts/retro/2026-05-28-find-skills-handoff-no-auto-trigger.md).
  If recurring, open a setup-skill issue.
- PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen
  unless outside PRs become recurring.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
