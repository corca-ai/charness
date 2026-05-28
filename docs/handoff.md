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

- **`main` tracks `origin/main`.** The #233 achieve-F1 binding fix is committed
  on `main` (see commit log); verify it is pushed before new work.
- **Open issues**: routing goal bundles #240/#238/#239; also #233, #232, #235,
  #219, #236/#237 (achieve/quality UX), #184/#185. (`gh issue list` for live.)
- **#233 — kept OPEN, partial.** F1 binding LANDED for `achieve`: cited
  `Retro:`/`Host log probe:` files must now bind to the goal (slug/issue from
  the `Activation:` line); fails closed; numeric token anchored; stale-retro
  attack blocked + tested. **Open:** F2 narration is advisory+prose only
  (enforcement deferred — judgment-bound) and issue/release sibling bindings
  deferred → [closeout contract](./prescribed-skill-closeout-contract.md).
- **#235 is the live mutation regression** (73.7% < 80%); **#219 superseded**
  (its `artifact_closeout_status` survivors no longer appear in #235).
- **v0.10.0 published**; real-host release proof not yet run
  ([release latest](../charness-artifacts/release/latest.md)).

## Next Session

1. **Activate the session-start-routing goal** (designed this session, inert
   until activated):
   `/goal @charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md`.
   Scope: a **simple** `SessionStart` hook (Claude Code + Codex) that only
   triggers `find-skills`, with the routing-to-workflow responsibility moved
   **into the `find-skills` skill** (drive the workflow from its result;
   `handoff` on a pickup). Bundles **#240** (routing miss), **#238** (setup
   names `find-skills` as a skill, not a bare command), **#239** (achieve
   before-phase question + activation-closeout clarity). Run a fresh plan
   critique at activation before slice 1. (`UserPromptSubmit` was rejected as
   over-fire — see the goal's Interview Decisions.)
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

- **Routing miss CONFIRMED recurring (2026-05-29):** the `handoff` skill again
  did not auto-trigger on a `@docs/handoff.md` pickup (`find-skills` ran,
  `handoff` did not), and `achieve` was expected where `issue` was chosen. The
  confirming recurrence per the
  [routing-miss retro](../charness-artifacts/retro/2026-05-28-find-skills-handoff-no-auto-trigger.md);
  acted on via the Next-Session routing goal. Same "prose fails under stimulus,
  need a gate" pattern as #230/#233.

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [closeout contract](./prescribed-skill-closeout-contract.md),
  [release surface](../charness-artifacts/release/latest.md)
