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

- **`main` is 20 commits ahead of `origin/main`, locally green, not yet pushed.**
  Carries the #230 + #229 closeout (8 slices) and the handoff-chunked-routing
  goal (draft + 7 slices + closeout-narration follow-up). Pre-push will run as
  `full-gate-required` (touches `.githooks/`, `scripts/`, `skills/`, `tests/`).
- **handoff-chunked-routing goal: COMPLETE locally** — chunker behind a
  deterministic trigger gate on the `handoff` skill
  ([goal](../charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md),
  [closeout](../charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md)).
- **#229 + #230 LOCALLY RESOLVED, still OPEN on GitHub** (gh-close pending push;
  [goal](../charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md)).
- **v0.10.0 published**; real-host release proof (Cautilus install/doctor on a
  clean machine) NOT yet run. See [release latest](../charness-artifacts/release/latest.md).
- **#219 still OPEN** — fix `a0b8de0e` on `main` awaiting next scheduled mutation
  run to validate + auto-close (do not hand-close). See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-224-219-mutation-annotation-filter.md).
- **New issues**: #234 (mutation regression on main), #233 (closeout-gate
  hardening: F1 binding + F2 user-message surfacing), #232 (issue skill
  shell-quoting body corruption).

## Next Session

1. **Push the 20 commits.** Pre-push runs as `full-gate-required`. A
   preexisting find-skills inventory schema drift (integration IDs renamed
   but file basenames unchanged in
   [integrations/tools](../integrations/tools/)) will fire under
   `validate-current-pointer-freshness` and likely block — either rename the
   JSON files to match the new IDs or teach the validator to follow the
   id-to-path mapping. After push, gh-close #229 + #230 against the local
   closeout retro evidence.
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

- PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen
  unless outside PRs become recurring.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
