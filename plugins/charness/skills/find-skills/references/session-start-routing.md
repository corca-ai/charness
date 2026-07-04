# Session-Start Routing

A `SessionStart` hook — installed at **user level**
(`~/.claude/settings.json` for Claude Code, `~/.codex/config.toml` for Codex),
not committed into a repo — injects a routing directive at session open. It
cannot invoke a Skill tool or run a workflow on the agent's behalf; it can only
inject context the model must still act on. (`charness update` does not
auto-wire this hook; it is a manual user-level install.)

## The miss this prevents (issue 240 history)

The recurring failure the original session-start-routing fix (issue 240)
targeted: the agent runs `find-skills`, emits the capability inventory, and
then reacts to the raw `@docs/handoff.md` mention content instead of
continuing the workflow the handoff names. `find-skills` ran; `handoff` did
not. The fix at the time was not "ensure find-skills runs" — routing every
`SessionStart` open through `find-skills` and having it **drive the routed
workflow from its result**.

## 2026-07-04 revision: front-load adopted, issue 240 protections carried over

The issue 240 fix deliberately rejected front-loading the routing rule into
the hook directive itself, reasoning that a hook cannot hard-force a Skill
invocation, so encoding the rule only in hook text risked the same silent drop
the fix existed to prevent (the "Honest ceiling" note below). That rejection
held until real session-cost data showed `find-skills` running on effectively
every session open just to re-confirm an already-cached inventory. The
operator then approved front-loading the routing rule directly into the hook
directive, carrying over three protections from the issue 240 analysis.
The cost arithmetic behind the adoption: the front-loaded directive adds
roughly +85 tokens per session over the old pointer, while a `find-skills`
invocation costs a ~199-line SKILL.md (~2.5k tokens) plus bootstrap script
runs and inventory output — so any session that no longer invokes the skill
nets a large saving (no per-session traffic dataset is cited yet; the claim
is the arithmetic, not a measured mix). Carried-over protections:

1. A pickup must still deterministically drive into the handoff-named
   workflow: the hook directive itself now names `docs/handoff.md`'s
   `Workflow Trigger` and `charness:handoff` directly, rather than delegating
   that decision to `find-skills`.
2. Recommendation-shaped discovery stays owned by `find-skills`: a named
   skill/support/integration mention, or a "which skill handles X" question,
   still routes to `charness:find-skills` instead of being answered inline.
3. When `find-skills` IS invoked — for discovery, a missing/stale capability
   map, or a genuinely unclear route — it still drives the routed workflow
   from its result per `SKILL.md`'s `## Drive The Routed Workflow`; the
   routing-miss class this skill exists to prevent (inventory runs, routed
   workflow does not) still applies whenever this skill is the invoked path.

## Pickup decision path

This is now executed directly by the hook's front-loaded directive for the
common no-explicit-task case, and re-applied by `find-skills` whenever a
pickup surfaces from an invocation that started as discovery or an unclear
route:

1. Is there an explicit task directive in the opening message?
   - Yes -> route to the matched durable work skill and start it.
   - No (bare mention of the handoff doc, or a SessionStart-only open) -> treat
     it as a **pickup** and continue to step 2.
2. Read the handoff's `Workflow Trigger` (default `docs/handoff.md`).
3. Invoke the workflow it names. For the default charness handoff that is
   `charness:handoff` — invoke the skill, do not just re-read the file. The
   handoff skill then classifies pickup-vs-refresh and continues from its own
   `Workflow Trigger`.
4. A pure capability-discovery question ("which skill handles X?") is the
   exception: the inventory answer is the deliverable; do not invent a workflow
   to run.

## Boundary

- The hook now carries the pickup, capability-discovery, and otherwise routes
  directly; `find-skills` is invoked only for capability discovery, a
  missing/stale capability map, or a genuinely unclear route — not on every
  session open.
- Map staleness is judgment-only: nothing refreshes
  `charness-artifacts/find-skills/latest.*` automatically anymore (the old
  every-session invocation was the de-facto refresher), and no deterministic
  staleness check exists. If rot recurs in practice, the named follow-up is
  extending the `validate_find_skills_integration_claims` pattern in
  `validate_current_pointer_freshness.py` to diff the recorded skill ids
  against the live listing — a floor added on recurrence, not on first sight.
- This skill does not reimplement `handoff`; it routes into it.
- Honest ceiling: a `SessionStart` hook strengthens routing via
  context-recency but does not hard-force a Skill invocation. That ceiling now
  applies to the front-loaded rule text itself, which is why `find-skills`
  still owns and drives the routed workflow whenever it is the invoked path.
