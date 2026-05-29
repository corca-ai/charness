# Achieve Goal: Make session-start routing reliable: simple SessionStart find-skills trigger + find-skills owns workflow drive (#240)

Status: complete
Created: 2026-05-29
Activation: `/goal @charness-artifacts/goals/2026-05-29-240-session-start-routing-enforcement.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Make session-start routing reliable across hosts so that when a session opens —
especially a pickup where the first signal is a bare `@docs/handoff.md` mention
or just an opened session — the agent goes through `find-skills` and then
actually executes the routed workflow (e.g., `handoff` on a pickup) instead of
reacting to the `@`-mention content. Achieve this with a **simple SessionStart
hook** that only triggers a `find-skills` call, while the **routing-to-workflow
responsibility moves into the `find-skills` skill's own contract**. This is the
gate-not-exhortation fix for the recurring routing miss (#240); it is the same
"prose-under-stimulus fails" pattern that #230/#233 closed at other layers.

Bundled related issues:

- **#238** — the setup-rendered AGENTS.md Skill Routing text must name
  `find-skills` as a *skill*, not a bare PATH command (it misread as a binary in
  a Ceal Codex session). Shares slice 4's surface (setup's AGENTS.md routing
  rendering).
- **#239** — `achieve`'s before-phase/activation operator experience: ask ≥1
  high-leverage question on real mode ambiguity (artifact-only vs.
  implementation-continuation), and make the activation line + inert-until-`/goal`
  status hard to miss. Adjacent achieve-skill surface; folded per the user so
  the operator-handoff gap is handled in the same run (slice 5). Classified by
  its reporter as a workflow-contract regression.

## Non-Goals

- No per-message `UserPromptSubmit` hook. Rejected this session (fires every
  prompt = noise; over-fires on mid-session `@file` mentions). Revisit only if
  mid-session routing drift is later observed and measured.
- Not the #233 remainder (F2 narration enforcement; `issue`/`release` sibling
  bindings). Separate track.
- No broad skill refactor; touch only the routing-relevant surfaces.
- Do not change the find-skills capability-discovery algorithm; only add the
  "drive the routed workflow from the result" contract on top.
- Do not modify host runtimes; host wiring stays in adapters/presets/settings.

## Boundaries

- The SessionStart hook stays dumb: it triggers `find-skills`, nothing more. All
  routing intelligence lives in the `find-skills` skill, not in hook text.
- Honest ceiling (NON-CLAIM, see Final Verification): a hook injects context the
  model must still honor — hooks cannot invoke a Skill tool directly. This is
  much stronger than always-loaded `CLAUDE.md` prose (session-recency) but is
  NOT hard execution-forcing. The fully-deterministic alternative (hook runs the
  find-skills script and front-loads its output) is explicitly NOT chosen
  because the user wants the SKILL invoked so its routing guidance applies, not
  bypassed.
- Portability stop: any host-specific behavior must live in adapters/presets/
  integration manifests (`update-config` owns Claude Code `settings.json`); no
  Claude-Code-only branch baked into a portable skill.
- Codex parity is in-scope but investigation-gated: if the Codex session-start
  mechanism turns out to be materially different or unavailable, record that as
  a blocker and ship the Claude Code half rather than faking parity.

## User Acceptance

- Opening a fresh session and mentioning only `@docs/handoff.md` reliably routes
  through `find-skills` → `handoff` (the workflow named by the trigger), without
  the user re-asking.
- The SessionStart hook is visible in the repo's `.claude/settings.json` (and
  the Codex equivalent) and demonstrably fires on session start.
- `find-skills`' SKILL.md states the "drive the routed workflow from your result"
  contract, with a deterministic self-test pinning the prescribed path.
- A maintainer can read the change set and see the host-portable split (skill
  owns routing; hook is dumb; AGENTS.md carries the durable rule).
- (#238) The setup-rendered Skill Routing block names `find-skills` as a skill
  and no longer uses bare-command syntax that reads as a PATH binary, while
  staying compact and still telling agents to use it before ad hoc discovery.
- (#239) Invoking `achieve` on an ambiguous selector asks at least one
  high-leverage question (or states the assumption used), and the final response
  makes the activation line + inert-until-`/goal` status impossible to miss.

## Agent Verification Plan

### Low-Cost Checks

- `validate_skills.py` + skill-contract gates pass after the find-skills and
  handoff SKILL.md edits.
- New deterministic self-test for the find-skills prescribed routing path passes
  and fails when the contract line is removed.
- `check-markdown` / `check-doc-links` pass for AGENTS.md / CLAUDE.md / handoff.
- Expected proof cost: low. Expected test-duplication pressure: low (one new
  focused self-test; reuse existing skill-validation fixtures).

### High-Confidence Checks

- Manually fire the Claude Code SessionStart hook (open a session / `--resume`)
  and confirm the injected `find-skills` directive lands in context.
- Dry-run the pickup scenario: fresh session + `@docs/handoff.md` mention →
  observe find-skills → handoff routing actually occurs.

### External Or Live Proof

- Codex host smoke: confirm the Codex session-start mechanism fires the
  equivalent trigger (host: Codex). If unavailable, record as a non-claim.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Upgrade `find-skills` SKILL.md: add "drive the routed workflow from the inventory result; on a pickup follow the handoff Workflow Trigger to `charness:handoff`" contract + deterministic self-test | This is the load-bearing change — it fixes the 2026-05-29 miss (find-skills ran, handoff did not) that a hook-only trigger cannot catch | SKILL.md contract line; self-test passes and fails-on-removal; validate_skills green | done |
| 2 | Claude Code SessionStart hook via `update-config` (`.claude/settings.json`, `startup`/`resume` matcher), simplest find-skills trigger | The gate that makes slice 1 fire reliably at session open | Hook present in settings.json; fires on session start (observed); injects the find-skills directive | done (live in-session fire not observed — see Final Verification non-claim) |
| 3 | Investigate Codex session-start hook mechanism; wire the equivalent parity through adapter/preset | Host axis is multi-host; parity must land in the same goal, not drift | Codex hook config + smoke that it fires, or a recorded blocker if the mechanism differs | done (confirmed real parity; local smoke; live Codex run is an external non-claim) |
| 4 | AGENTS.md durable rule via the `setup` skill; align CLAUDE.md/handoff.md; improve the `handoff` skill's pickup contract; **resolve #238** — setup Skill Routing text names `find-skills` as a skill (not a bare command), stays compact, no rerun drift | The durable contract behind the gate; setup owns the AGENTS.md/CLAUDE.md surface — same surface #238 fixes | AGENTS.md rule; #238 acceptance criteria met; handoff skill pickup contract; gates green | done |
| 5 | **Resolve #239** — tighten `achieve`'s before-phase/activation contract: require ≥1 high-leverage question on real mode ambiguity (artifact-only vs. implementation-continuation), state the assumption when skipping, and make the activation line + inert-until-`/goal` status operationally hard to miss (closeout checklist for `Goal file:`/`Activation:`) | Folded per user; this very run exposed the gap (a no-question before-phase) so the lesson is live | `achieve` SKILL.md / lifecycle contract updated; self-test or fixture pinning the activation-closeout shape; gates green | done |

## Slice Log

### Slice 1: Plan Critique (activation)

- Objective: Run the deferred fresh-eye plan critique before slice 1, per Plan Critique Findings.
- Why this approach: Goal deferred a bounded angle+counterweight pass to activation; this is the prescribed Before->During critique.
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Two bounded subagents: general-purpose plan critic + claude-code-guide SessionStart-mechanism check.
- Test duplication pressure:
- Critique: BLOCKER1 (.claude/settings.json surface ownership) resolved: validators do not flag repo-root dotfiles; no surfaces.json obligation; hook script lives in owned+synced scripts/. BLOCKER2 (#238 renderer<->AGENTS.md<->pin-test) folded into slice 4 as one coordinated edit. WATCH1 resolved: use structured hookSpecificOutput.additionalContext JSON (confirmed via claude-code-guide). WATCH2: matcher startup|resume|clear, exclude compact (mid-session over-fire). WATCH3: slice-1 self-test = SKILL.md contract-substring pin (test_handoff_skill.py idiom), not duplicative of script tests. SYNC=python3 scripts/sync_root_plugin_manifests.py --repo-root .
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Slice 1 — find-skills owns workflow-drive

- Objective: find-skills SKILL.md states 'drive the routed workflow from your result; pickup -> handoff Workflow Trigger -> charness:handoff', with a deterministic self-test.
- Why this approach: Load-bearing fix: the 2026-05-29 miss had find-skills run but handoff skipped; a hook-only trigger cannot catch that, so the skill must own driving the routed workflow.
- Commits:
- What changed: skills/public/find-skills/SKILL.md (Drive section + Workflow step 7 + guardrail + ref); new references/session-start-routing.md; new tests/quality_gates/test_find_skills_routing_drive.py
- Alternatives rejected: Rejected a brand-new standalone grep test that would duplicate skill-validation fixtures (recent-lessons test-duplication trap); reused the SKILL.md contract-substring idiom instead.
- Targeted verification: validate_skills rc=0 (SKILL.md trimmed to the 200-line cap); test_find_skills_routing_drive 2 passed; check_doc_links rc=0. Fails-on-removal is inherent (asserts exact contract substrings).
- Test duplication pressure: Low: 1 new focused contract-pin test (test_handoff_skill.py idiom); not duplicative of test_find_skills.py (which tests the script).
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Slice 2 — Claude Code SessionStart hook

- Objective: Dumb SessionStart hook in the repo's .claude/settings.json that injects a directive to invoke charness:find-skills.
- Why this approach: The gate that makes slice 1 fire reliably at session open; routing intelligence stays in find-skills (slice 1).
- Commits:
- What changed: new scripts/session_start_find_skills.py (silent-failing, emits hookSpecificOutput.additionalContext); new .claude/settings.json (SessionStart matcher startup|resume|clear); new tests/test_session_start_find_skills.py
- Alternatives rejected: Excluded matcher 'compact' (mid-session auto-compaction) to avoid re-routing mid-task — same over-fire reasoning that rejected UserPromptSubmit. Did NOT overload the usage-episodes host_hook_install_lib (silent recorder, different concern); repo-level dogfood config kept separate from home-level consumer install.
- Targeted verification: 6 tests pass; ruff clean; settings.json valid JSON; LIVE demo: firing the script with a SessionStart payload emits the exact additionalContext directive Claude Code injects. Confirmed CC contract via claude-code-guide (stdout additionalContext + project/user hooks coexist).
- Test duplication pressure: Low: 1 new focused hook test file; no overlap with usage-episodes host-hook tests (different script, different settings file/level).
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics: Honest ceiling recorded: hook strengthens routing via context-recency but cannot hard-force a Skill invocation; live 'fires on a brand-new session open' is a high-confidence check pending a fresh session.

### Slice 4: Slice 3 — Codex session-start parity

- Objective: Wire the Codex equivalent of the Claude Code SessionStart find-skills trigger via repo .codex/config.toml.
- Why this approach: Multi-host axis: parity must land in the same goal, not drift; investigation-gated per Boundaries.
- Commits:
- What changed: new .codex/config.toml ([[hooks.SessionStart]], git-root resolution, --host codex); render_output now emits structured additionalContext for codex too; refreshed charness-artifacts/gather/2026-05-22-codex-hooks-surface.md (context-injection + repo-local resolution); tests/test_session_start_find_skills.py extended (codex structured output + .codex/config.toml wiring).
- Alternatives rejected: Investigation outcome: NOT a blocker. Fresh fetch of the Codex hooks doc (2026-05-29) confirmed Codex SessionStart supports hookSpecificOutput.additionalContext + plain-stdout-to-context, the same startup|resume|clear|compact matcher set, and recommends git-root resolution for repo-local hooks (no ). So parity is real — same script, same payload; only the script-resolution seam differs ($CLAUDE_PROJECT_DIR vs $(git rev-parse --show-toplevel)).
- Targeted verification: 8 hook tests pass; ruff clean; .codex/config.toml valid TOML; LIVE smoke: --host codex emits the same additionalContext directive. check_doc_links rc=0 after disambiguating deferred-decisions.md:212 (config.toml basename collision).
- Test duplication pressure: Low: extended the existing hook test file (no new file); tomllib/tomli fallback for Py3.10.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics: Honest ceiling unchanged: a Codex hook also only injects context, not a forced Skill invocation. Live 'fires in a real Codex session' is a high-confidence external check (host: Codex), not run here.

### Slice 5: Slice 4 — AGENTS.md durable rule + #238 setup fix + handoff pickup contract

- Objective: Resolve #238 (setup Skill Routing names find-skills as a skill, not a bare command); align AGENTS.md/CLAUDE.md; tighten the handoff pickup contract reciprocal with slice 1.
- Why this approach: The durable contract behind the gate; setup owns the AGENTS.md Skill Routing surface that #238 fixes.
- Commits:
- What changed: render_skill_routing.py line 56 (bare 'find-skills --recommend-for-task' -> 'ask the find-skills skill to recommend a route'); AGENTS.md:22 regenerated to match (CLAUDE.md symlink follows); test_setup_render_skill_routing.py updated + #238 regression guards (no 'find-skills --'); handoff/SKILL.md guardrail (find-skills->handoff pickup loop, invoke-not-read); test_handoff_skill.py pins it.
- Alternatives rejected: Regenerated AGENTS.md to match the renderer (single-line edit) rather than letting the rendered block drift from the checked-in artifact.
- Targeted verification: render_skill_routing+handoff_skill tests 4 passed; validate_skills rc=0; doc-links rc=0; renderer recommended_action=leave_as_is + matches_compact_block=True (no rerun drift). #238 acceptance met: find-skills named as a skill, no bare-command syntax, block stays compact.
- Test duplication pressure: Low: strengthened two existing contract-pin tests in place (added #238 regression guard + handoff pickup pin); no new test files.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 6: Slice 5 — achieve #239 before-phase question + activation clarity

- Objective: Require >=1 high-leverage question on real mode ambiguity (artifact-only vs implementation-continuation), state assumption when skipping, and make activation line + inert-until-/goal status hard to miss.
- Why this approach: Folded per user; this very run's activation exposed the gap. #239 is a workflow-contract regression in achieve's Before phase.
- Commits:
- What changed: achieve/SKILL.md Before phase (mode-ambiguity question bullet + Goal file:/Activation:/inert closeout bullet); references/lifecycle.md (Mode disambiguation + Activation-closeout clarity subsections); new tests/quality_gates/test_achieve_before_activation.py.
- Alternatives rejected: Kept the existing check_goal_artifact.py Activation:-line hard gate as the artifact-side counterpart; added the response-side closeout checklist as prose contract rather than a new transcript gate (a hard narration gate would over-fire, per the #233 F2 precedent).
- Targeted verification: test_achieve_before_activation 2 passed; validate_skills rc=0 (SKILL.md 130 lines); doc-links rc=0. Contract pinned in both SKILL.md and lifecycle.md; fails-on-removal inherent.
- Test duplication pressure: Low: 1 new focused contract-pin test (test_handoff_skill.py idiom).
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. This 2026-05-29 session conversation (the routing-miss diagnosis and the
   converged design: simple SessionStart hook + find-skills owns routing).
2. Issue [#240](https://github.com/corca-ai/charness/issues/240) — the filed
   routing-miss problem and tentative direction.
3. [Routing-miss retro 2026-05-28](../retro/2026-05-28-find-skills-handoff-no-auto-trigger.md)
   — the prior occurrence and "open an issue if recurring" instruction.
4. [Prescribed-skill closeout contract](../../docs/prescribed-skill-closeout-contract.md)
   — the #230/#233 "gate-not-exhortation" precedent this goal mirrors.
5. `skills/public/find-skills/SKILL.md` — the skill that gains the routing-drive
   contract.
6. `skills/public/handoff/SKILL.md` — the pickup-contract surface to improve.
7. The `setup` skill — owner of the AGENTS.md/CLAUDE.md Start Here surface.
8. Issue [#238](https://github.com/corca-ai/charness/issues/238) — bundled:
   setup Skill Routing text must name `find-skills` as a skill, not a bare
   command (misread as a PATH binary in a Ceal Codex session).
9. Issue [#239](https://github.com/corca-ai/charness/issues/239) — bundled:
   `achieve` before-phase question discipline + activation-closeout clarity.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **Hook trigger point** (axis: host hook lifecycle). Family: {SessionStart,
   UserPromptSubmit, no-hook/prose-only}. Chosen: **SessionStart**. Rejected:
   UserPromptSubmit (fires every prompt → noise + over-fires on mid-session
   `@file`; observed misses were all first-message); prose-only (already failed
   twice — 2026-05-28, 2026-05-29).
2. **Where routing responsibility lives** (axis: ownership layer). Family: {hook
   injection text carries routing logic, find-skills skill owns it, CLAUDE.md
   prose owns it}. Chosen: **find-skills skill owns "drive workflow from
   result"**. Rejected: hook-carries (keeps the hook dumb is cleaner, and
   find-skills is the natural owner); prose-only (failed).
3. **Hook realization** (axis: determinism vs. skill-fidelity). Family: {inject
   a directive to call find-skills, hook runs the find-skills script and
   front-loads its output}. Chosen: **inject a directive** (simplest; preserves
   the skill's own routing guidance). Rejected: front-load output (bypasses the
   skill's guidance, token-heavy) — but recorded as the only fully-deterministic
   option and thus the honest ceiling.
4. **Host scope** (axis: host — multi-host, NOT single-point). Family: {Claude
   Code only, both Claude Code + Codex, host-agnostic abstraction}. Chosen:
   **both Claude Code + Codex** (CC now; Codex investigation-gated parity in the
   same goal).
5. **AGENTS.md rule ownership** (axis: contract surface owner). Family: {setup
   skill owns it, handoff skill, ad hoc edit}. Chosen: **setup skill** (owns the
   AGENTS.md/CLAUDE.md Start Here surface).

## Plan Critique Findings

This plan was refined conversationally with the user this session, which
functioned as iterative critique (the user themselves rejected UserPromptSubmit,
narrowed to SessionStart, then moved the routing role into find-skills). Folded
findings:

- **find-skills-only trigger is insufficient** (folded into slice 1): the
  2026-05-29 miss had find-skills run but handoff skipped. So the fix cannot be
  "ensure find-skills runs"; find-skills must own driving the routed workflow.
- **Over-fire avoidance** (folded into Non-Goals + Boundaries): no per-message
  hook; SessionStart only.
- **Honesty ceiling** (folded into Boundaries + planned Final Verification
  non-claim): a hook-injected directive is strong-but-not-forcing; do not claim
  hard enforcement.
- **Codex parity risk** (folded into Boundaries + slice 3): investigation-gated;
  ship CC half + record blocker rather than fake parity.

Deferred: a fresh bounded **plan critique** (angle + counterweight) should run at
activation, before slice 1 begins — this draft records the converged design, not
a substitute for the prescribed Before→During critique pass.

## Off-Goal Findings

- #233 remainder (F2 narration enforcement + `issue`/`release` sibling bindings)
  is tracked on #233; not absorbed here.

## Final Verification

**Post-completion adjustment (2026-05-29, same day):** the find-skills
SessionStart hook was moved from the repo dogfood (`.claude/settings.json` /
`.codex/config.toml`, removed) to a **user-level** install
(`~/.claude/settings.json` / `~/.codex/config.toml`) pointing at the released
plugin script, so it fires in every session on the machine rather than only
inside this repo, and does not double-fire alongside a repo copy. The
load-bearing achievement is unchanged (dumb hook triggers `find-skills`;
`find-skills` owns driving the routed workflow); only the install *location*
changed. The portable mechanism (`scripts/session_start_find_skills.py` + its
behavior tests + the find-skills routing contract) stays in the repo;
User Acceptance bullet 2 ("visible in the repo's `.claude/settings.json`") is
superseded by this user-level decision. This adjustment also resolved a related
finding: usage-episodes SessionStart hooks were duplicated per checkout, and the
episode telemetry has no consumer/report yet — tracked separately (see handoff).

All five slices shipped and verified locally; #238 and #239 resolved. Closeout
evidence:

- Retro: charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md
- Host log probe: charness-artifacts/probe/2026-05-29-240-session-start-routing-enforcement.json

Proven (local, deterministic):

- find-skills SKILL.md states the "drive the routed workflow from your result;
  pickup -> handoff Workflow Trigger -> `charness:handoff`" contract, pinned by
  `tests/quality_gates/test_find_skills_routing_drive.py` (fails on removal).
- The dumb `SessionStart` hook (`scripts/session_start_find_skills.py`) emits the
  `hookSpecificOutput.additionalContext` directive — demonstrated live by firing
  the script with a SessionStart payload for both `--host claude` and `--host
  codex`. Pinned by `tests/test_session_start_find_skills.py`. Installed at user
  level (see post-completion adjustment above), not committed into the repo.
- #238: the setup-rendered Skill Routing block names `find-skills` as a skill,
  not a bare PATH command; AGENTS.md is an exact byte-match to the renderer (no
  rerun drift); regression guard in `test_setup_render_skill_routing.py`.
- #239: achieve's Before phase requires a mode-disambiguation question
  (artifact-only vs implementation-continuation) or a stated assumption, and an
  activation-closeout checklist; pinned by `test_achieve_before_activation.py`.
- All gates green: validate_packaging(_committed), validate_skills,
  validate_surfaces, validate_cautilus_proof (deterministic owns 6 prompt paths),
  ruff, check-markdown, check-secrets, check_doc_links, check_command_docs;
  103 touched/adjacent tests pass; RCA ledger event appended and valid.

Honest non-claims (NOT proven):

- **The hook strengthens routing via context-recency but does NOT hard-force a
  Skill invocation.** A SessionStart hook injects context the model must still
  honor; it cannot call a Skill tool. The fully-deterministic alternative
  (hook runs the find-skills script and front-loads its output) was deliberately
  NOT chosen, because the user wants the skill invoked so its routing guidance
  applies. This is the strongest honest ceiling.
- **Not observed firing on a brand-new live session open.** The hook was absent
  at this session's start (it is new this session), so I could not observe it
  fire in-session. The deterministic proof is the script's emitted payload + the
  valid settings wiring + the confirmed host contracts. First real proof lands
  the next time a session opens in this repo (Claude) / a Codex session opens.
- **Codex parity confirmed by docs + local smoke, not a live Codex run.** A
  fresh 2026-05-29 fetch of the Codex hooks doc confirmed SessionStart supports
  `hookSpecificOutput.additionalContext` and the same matcher set; the `--host
  codex` payload was smoked locally. A live Codex session-open smoke is a
  high-confidence external check, not run here (host: Codex).
- The second SessionStart hook (repo find-skills) coexists with the home-level
  usage-episodes hook; the usage-episodes hook emits no stdout context, so no
  dilution today — worth a one-time live confirmation if it ever starts emitting.

## User Verification Instructions

1. Open a fresh Claude Code session in this repo (or `--resume`) and confirm the
   injected context line "charness session-start routing: ... invoke the
   `charness:find-skills` skill" appears, and that the agent then routes a bare
   `@docs/handoff.md` pickup through find-skills into `charness:handoff` without
   you re-asking.
2. Codex: open a session in this repo and confirm the `.codex/config.toml`
   SessionStart hook fires the same directive.
3. Inspect the wiring: `.claude/settings.json` and `.codex/config.toml` both
   reference `scripts/session_start_find_skills.py`.
4. Confirm #238: AGENTS.md "## Skill Routing" reads "ask the `find-skills`
   skill to recommend a route for the task" (no bare `find-skills --…` command).

## Auto-Retro

Persisted: `charness-artifacts/retro/2026-05-29-240-session-start-routing-closeout.md`
(recent-lessons.md + lesson-selection-index.json refreshed; RCA event appended,
class `session-start-routing-prose-not-gated`).

- **Waste**: find-skills SKILL.md sat exactly at the 200-line cap, so the
  load-bearing slice-1 contract forced several trim cycles; a self-test broke on
  a line-wrapped phrase (fixed via whitespace-normalization); adding
  `.codex/config.toml` made `config.toml` a unique basename and tripped
  check_doc_links on a pre-existing unrelated backtick.
- **Critical Decisions**: running the plan critique before slice 1 caught the
  #238 renderer<->AGENTS.md<->test coupling early; verifying the injection
  mechanism (claude-code-guide + live Codex-doc fetch) instead of copying the
  silent usage-episodes hook flipped Codex from likely-blocker to confirmed
  parity; keeping the hook dumb with routing owned by find-skills is what
  catches the exact miss a hook-only fix cannot.
- **Next Improvements**: warn on SKILL.md files at the line cap before edits;
  run check_doc_links early when a slice adds a collision-prone basename; the
  "hook dumb, skill owns routing" pattern now lives in
  find-skills/references/session-start-routing.md.
- **Sibling Search**: the "prose-under-stimulus -> gate" family (#230/#233/#240)
  was scanned; the one open sibling (#233 F2 narration + issue/release sibling
  bindings) is already tracked on #233 and is a Non-Goal here. No new un-gated
  sibling surfaced.
