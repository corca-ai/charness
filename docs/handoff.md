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

- **`main` ahead of `origin/main` by 1** (commit `e3493cf`, not yet pushed):
  the #240/#238/#239 session-start-routing goal is COMPLETE. Verify the push
  before new work.
- **Session-start routing is now gated** (was the recurring prose-fails miss):
  a dumb SessionStart hook (wired for Claude + Codex) injects a directive to
  invoke `find-skills`, which now owns driving the routed workflow (pickup ->
  `charness:handoff`). Honest non-claim: the hook strengthens routing via
  context-recency but does not hard-force a Skill call, and was not observed
  firing live yet. See the
  [completed goal](../charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md).
- **Open issues**: #240/#238/#239 resolved this run; still open: #233, #232,
  #235, #219, #236/#237 (achieve/quality UX), #184/#185. (`gh issue list` for live.)
- **#233 — kept OPEN, partial.** F1 binding LANDED for `achieve` (cited evidence
  must bind to the goal; fails closed; tested). **Open:** F2 narration enforcement
  (judgment-bound) and issue/release sibling bindings deferred →
  [closeout contract](./prescribed-skill-closeout-contract.md).
- **#235** live mutation regression (73.7% < 80%); **#219** superseded.
- **v0.10.0 published**; real-host proof pending
  ([release latest](../charness-artifacts/release/latest.md)).

## Next Session

1. **Push `e3493cf`** (the completed #240/#238/#239 routing work) to
   `origin/main`, then **live-confirm the SessionStart hook**: open a fresh
   Claude Code session here and check the injected "charness session-start
   routing" directive lands and a bare handoff-doc mention pickup routes through
   find-skills into `charness:handoff` without re-asking. Codex: confirm the
   repo hook fires the same directive (host: Codex).
2. **#233 remainder.** Decide F2 narration enforcement (judgment-bound), then
   wire `evidence_binds_to_context` into `issue` (`issue_verify_closeout.py`)
   and `release` (`publish_release_preflight.py`) — both still call the
   presence-only `helper.check` and inherit the F1 shape.
3. **#235** mutation regression — triage current survivors; auto-close #219 once
   the scheduled run clears (do not hand-close).
4. **#232** issue-skill `gh issue create` body shell-quoting corruption.
5. **Real-host release proof for v0.10.0** when a clean machine + Cautilus slot
   are available; **Codex host smoke** of the After-phase gate.
6. **#184/#185** deferred product / AI-ML direction work.

## Discuss

- **Routing miss now gated, awaiting live proof.** The recurring miss
  (`find-skills` ran, `handoff` did not) was converted to a gate this run
  (SessionStart hook + find-skills routing-drive contract + reciprocal handoff
  pickup pin), RCA-recorded as `session-start-routing-prose-not-gated`. The
  remaining open question is purely live confirmation: does the new hook
  reliably change behavior on a real session open? First proof lands next
  session. See [routing closeout retro](../charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [closeout contract](./prescribed-skill-closeout-contract.md),
  [release surface](../charness-artifacts/release/latest.md)
