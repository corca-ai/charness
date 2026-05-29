# Session-Start Routing

`find-skills` owns the decision of *what to do after the inventory* when a
session opens. A `SessionStart` hook — installed at **user level**
(`~/.claude/settings.json` for Claude Code, `~/.codex/config.toml` for Codex),
not committed into a repo — can only inject a directive to call this skill. It
cannot invoke a Skill tool or run a workflow on the agent's behalf. So the
routing intelligence has to live here, not in the hook text. (`charness update`
does not auto-wire this hook; it is a manual user-level install.)

## The miss this prevents

The recurring failure (retro 2026-05-28, confirmed again 2026-05-29): the agent
runs `find-skills`, emits the capability inventory, and then reacts to the raw
`@docs/handoff.md` mention content instead of continuing the workflow the
handoff names. `find-skills` ran; `handoff` did not. The fix is not "ensure
find-skills runs" — that already happened. The fix is that `find-skills` must
**drive the routed workflow from its result**.

## Pickup decision path

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

- The hook stays dumb: it triggers `find-skills`, nothing more.
- This skill does not reimplement `handoff`; it routes into it.
- Honest ceiling: a SessionStart hook strengthens routing via context-recency
  but does not hard-force a Skill invocation. Only a design where the hook runs
  the inventory script and front-loads its output would be fully deterministic,
  and that was deliberately not chosen so this skill's routing guidance still
  applies.
