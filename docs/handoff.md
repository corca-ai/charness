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
- **Open issues** (`gh issue list`): #247 (achieve: `/goal`=pursue vs shape —
  #246 follow-up), #245/#244/#243 (usage-episodes), #242+#219 (mutation
  regression), #233, #232, #241 (create-skill), #237/#236 (achieve/quality UX),
  #184/#185. (#246 closed.)
- **#233 — kept OPEN, partial.** F1 binding LANDED for `achieve`. **Open:** F2
  narration enforcement (judgment-bound) + issue/release sibling bindings →
  [closeout contract](./prescribed-skill-closeout-contract.md).
- **#242** live mutation regression (#235 now closed; **#219** still open).
- **v0.11.0 real-host proof pending** (Cautilus clean-machine smoke).

## Next Session

1. **Live-confirm the user-level SessionStart hook**: open a fresh Claude Code
   session, check the injected "charness session-start routing" directive lands
   and a bare handoff-doc mention pickup routes through find-skills into
   `charness:handoff` without re-asking. Codex: same (host: Codex).
   **/achieve skeleton drafted (unshaped)** → shape first: `/achieve @charness-artifacts/goals/2026-05-29-live-confirm-the-user-level-sessionstart-hook.md` (Before-phase fills acceptance/verification/slices); `/goal @…` activates the run only after shaping (#246).
2. **usage-episodes follow-ups (filed): #243** (no consumer/report + inconsistent
   capture → purpose unrealized), **#244** (find-skills hook not auto-wired by
   `charness update`), **#245** (cross-checkout episode-hook dup). See Discuss.
3. **#233 remainder.** F2 narration enforcement; wire `evidence_binds_to_context`
   into `issue` + `release` (still presence-only).
4. **#242** mutation regression (#235 closed) — triage survivors; reconcile #219 when the run clears.
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
