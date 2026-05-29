# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`** (do not just
  read this file; manual reading is the recurring miss — see Discuss) → read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` == `origin/main`; `v0.11.0` released + verified** ([release latest](../charness-artifacts/release/latest.md)).
  The #240/#238/#239 session-start-routing bundle is shipped and the three
  issues are **CLOSED**.
- **Session-start routing is gated, installed at USER level** (the recurring
  prose-fails miss). A dumb SessionStart hook (Claude `~/.claude/settings.json`,
  Codex `~/.codex/config.toml`) injects a directive to invoke `find-skills`,
  which now owns driving the routed workflow (pickup → `charness:handoff`).
  Honest non-claim: the hook strengthens routing via context-recency but does
  not hard-force a Skill call, and was not observed firing live yet.
- **Host hooks deduped**: each host now has exactly 1 usage-episode hook +
  1 find-skills hook (both → the installed plugin source `~/.agents/src/charness`).
- **Open issues**: #233, #232, #235, #219, #236/#237 (achieve/quality UX),
  #184/#185. (`gh issue list` for live.)
- **#233 — kept OPEN, partial.** F1 binding LANDED for `achieve`. **Open:** F2
  narration enforcement (judgment-bound) + issue/release sibling bindings →
  [closeout contract](./prescribed-skill-closeout-contract.md).
- **#235** live mutation regression (73.7% < 80%); **#219** superseded.
- **v0.11.0 real-host proof pending** (Cautilus clean-machine smoke).

## Next Session

1. **Live-confirm the user-level SessionStart hook**: open a fresh Claude Code
   session, check the injected "charness session-start routing" directive lands
   and a bare handoff-doc mention pickup routes through find-skills into
   `charness:handoff` without re-asking. Codex: same (host: Codex).
2. **usage-episodes follow-ups** (see Discuss): no consumer/report yet; the
   find-skills hook is not auto-wired by `charness update`; cross-checkout
   episode-hook duplication is structural. File issues if pursuing.
3. **#233 remainder.** F2 narration enforcement; wire `evidence_binds_to_context`
   into `issue` + `release` (still presence-only).
4. **#235** mutation regression — triage survivors; auto-close #219 when the run clears.
5. **#232** issue-skill `gh issue create` body shell-quoting; **v0.11.0 real-host proof**.
6. **#184/#185** deferred product / AI-ML direction.

## Discuss

- **usage-episodes is collected but its purpose is unrealized.** 200 episodes/7d,
  ~98% session-grouped, `t_status` rich — but **no consumer/report** turns it into
  the maintainer's answer ("used usefully? value compounding?"), and capture only
  fires on explicit `run_slice_closeout` (inconsistent; daily counts decay). The
  dedup stopped the ongoing 2× start-record duplication; ~30 historical orphan
  session dirs remain (gitignored local cruft). Decision taken: **B (hygiene) +
  release**; building the consumer + reliable capture is deferred (worth an issue).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [closeout contract](./prescribed-skill-closeout-contract.md),
  [release surface](../charness-artifacts/release/latest.md)
