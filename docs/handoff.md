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
- **Open issues**: #235, #233, #232, #219, #185, #184. (#229, #230, #234 closed.)
- **#233 — kept OPEN, partial.** F1 binding LANDED for `achieve`:
  `check_complete_evidence` binds each cited `Retro:`/`Host log probe:` file to
  the goal (basename/content must carry the goal slug or issue cluster from the
  `Activation:` line), fails closed on underivable identity, boundary-anchors
  the numeric token. Blocks the demonstrated stale-retro attack; tested;
  resolution critique caught + fixed a fail-open bypass pre-ship. **Still open:**
  F2 narration is a non-blocking affordance + prose only (hard enforcement
  deferred — judgment-bound); issue/release sibling bindings deferred. Remainder
  home: [closeout contract](./prescribed-skill-closeout-contract.md).
- **#235 is the live mutation regression** (73.7% < 80%); **#219 superseded**
  (its `artifact_closeout_status` survivors no longer appear in #235).
- **v0.10.0 published**; real-host release proof not yet run
  ([release latest](../charness-artifacts/release/latest.md)).

## Next Session

1. **Routing-enforcement hook (user request 2026-05-29).** A
   `SessionStart`/`UserPromptSubmit` hook — Claude Code (settings.json, via
   `update-config`) **and** the Codex equivalent — that forces
   `find-skills → named-workflow-skill` on `@artifact`/pickup-shaped first
   messages, plus an `AGENTS.md` rule that the next action is driven by the
   skill's output, not the `@`-mention content. This is the gate-not-exhortation
   fix for the recurring routing miss (Discuss).
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

- **Routing miss CONFIRMED recurring (2026-05-29).** Again this session the
  `handoff` skill did not auto-trigger on a `@docs/handoff.md` pickup
  (`find-skills` ran, `handoff` did not — manual read), and the user expected
  `achieve` where `issue` was chosen for #233. Per the
  [routing-miss retro](../charness-artifacts/retro/2026-05-28-find-skills-handoff-no-auto-trigger.md)
  this is the confirming recurrence — act via the Next-Session hook + a
  setup-skill issue. Same "prose fails under stimulus, need a gate" pattern as
  #230/#233.

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [closeout contract](./prescribed-skill-closeout-contract.md),
  [release surface](../charness-artifacts/release/latest.md)
