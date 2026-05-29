# Retro — #240 session-start-routing goal closeout (+#238, #239)

Mode: session

## Context

Closeout of the `achieve` goal
`charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md`,
run end-to-end this session from `/goal` activation through 5 slices plus the
bundled #238 (setup names find-skills as a skill) and #239 (achieve before-phase
question + activation clarity). The fix makes session-start routing reliable: a
dumb `SessionStart` hook triggers `find-skills`, and `find-skills` now owns
driving the routed workflow (a pickup continues with `charness:handoff`).

## Evidence Summary

- Host-log probe: `charness-artifacts/probe/2026-05-29-240-session-start-routing-enforcement.json`
  (both Claude and Codex sessions detected; token/tool-call/duration metrics
  derivable from the Claude project JSONL but not narrated as exact counts).
- Two bounded fresh-eye subagent passes (plan critique pre-slice-1; closeout
  critique pre-commit) and one `claude-code-guide` mechanism check.
- A live WebFetch of the Codex hooks doc (2026-05-29) that flipped Codex parity
  from investigation-gated risk to confirmed.
- Gates: validate_packaging(_committed), validate_skills, validate_surfaces,
  validate_cautilus_proof, ruff, check-markdown, check-secrets, check_doc_links,
  check_command_docs; 103 touched/adjacent tests passing.

## Waste

- `skills/public/find-skills/SKILL.md` was already sitting at exactly the
  200-line conciseness cap, so adding the load-bearing slice-1 routing-drive
  contract forced several trim/re-edit cycles to claw back under the cap. The
  contract content was right early; the budget fight cost the iterations.
- A slice-1 self-test assertion broke on a line-wrapped contract phrase
  (`drive the routed workflow from your\nresult`); fixed by whitespace-
  normalizing the test. Avoidable had the test normalized from the start.
- Adding `.codex/config.toml` made `config.toml` a unique repo basename, which
  tripped `check_doc_links` on a pre-existing, unrelated backtick in
  `docs/deferred-decisions.md` — a side-effect surfaced only at gate time.

## Critical Decisions

- Running the deferred plan critique BEFORE slice 1 caught the #238
  renderer↔AGENTS.md↔pin-test coupling and resolved the `.claude/settings.json`
  surface-ownership question before any code was written — avoided mid-slice
  rework.
- Verifying the SessionStart injection mechanism (claude-code-guide + a live
  Codex-doc fetch) instead of pattern-matching the SILENT usage-episodes hook.
  This flipped Codex from a likely blocker to confirmed real parity, and showed
  Codex supports the same `additionalContext` field — so the hook script stayed
  a single payload across both hosts.
- Keeping the hook dumb and the routing in `find-skills` (the goal's
  load-bearing design). A hook-only "ensure find-skills runs" fix would NOT have
  caught the 2026-05-29 miss where find-skills ran but `handoff` did not.

## Expert Counterfactuals

- Gary Klein (pre-mortem lens): "what's the most likely way this hook silently
  does nothing?" The answer — a hook cannot force a Skill invocation — is exactly
  the honest ceiling, and is precisely why the fix puts the drive-the-workflow
  responsibility in find-skills rather than the hook. The lens would have led to
  the same chosen split.
- Jef Raskin / Don Norman (affordance lens, already cited inside find-skills):
  the #238 misread (`find-skills` read as a PATH binary) is an affordance
  failure. An affordance check applied at render-time would have caught the
  bare-command syntax when `render_skill_routing.py` first emitted it, rather
  than waiting for a Codex-session misread to file the issue.

## Next Improvements

- capability: SKILL.md files sitting exactly at the 200-line cap are a latent tax
  on every future contract addition (find-skills is back at exactly 200). A
  pre-edit headroom signal (e.g. validator warns at ~190) would stop a
  load-bearing contract line from forcing a trimming sub-task.
- workflow: when a slice adds a new repo file whose basename may collide
  (`config.toml`, `settings.json`), run `check_doc_links` early in the slice, not
  only at closeout, so basename-uniqueness side-effects surface immediately.
- memory: the "hook is dumb, skill owns routing" pattern now lives durably in
  `skills/public/find-skills/references/session-start-routing.md`; the goal
  artifact + this retro capture the cross-host parity reasoning.

## Sibling Search

The transferable pattern is "always-loaded prose fails under stimulus; convert
to a gate" (the #230/#233/#240 family). Four-axis scan for un-gated siblings:

- other always-loaded prose contracts: handoff pickup (now reciprocally pinned
  in `test_handoff_skill.py`), achieve activation (now has both the
  `check_goal_artifact.py` `Activation:` gate and the #239 closeout checklist),
  find-skills routing-drive (now pinned by `test_find_skills_routing_drive.py`).
- hooks/triggers: the SessionStart trigger is the gate added this run.
- render-time affordance (the #238 surface): now has a regression guard in
  `test_setup_render_skill_routing.py`.
- Decision: the one remaining sibling — #233 F2 narration enforcement +
  issue/release sibling bindings — is already tracked on #233 and explicitly a
  Non-Goal here; not absorbed. No new un-gated sibling surfaced.

## Persisted
