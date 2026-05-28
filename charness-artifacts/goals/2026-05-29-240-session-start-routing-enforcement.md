# Achieve Goal: Make session-start routing reliable: simple SessionStart find-skills trigger + find-skills owns workflow drive (#240)

Status: draft
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
| 1 | Upgrade `find-skills` SKILL.md: add "drive the routed workflow from the inventory result; on a pickup follow the handoff Workflow Trigger to `charness:handoff`" contract + deterministic self-test | This is the load-bearing change — it fixes the 2026-05-29 miss (find-skills ran, handoff did not) that a hook-only trigger cannot catch | SKILL.md contract line; self-test passes and fails-on-removal; validate_skills green | pending |
| 2 | Claude Code SessionStart hook via `update-config` (`.claude/settings.json`, `startup`/`resume` matcher), simplest find-skills trigger | The gate that makes slice 1 fire reliably at session open | Hook present in settings.json; fires on session start (observed); injects the find-skills directive | pending |
| 3 | Investigate Codex session-start hook mechanism; wire the equivalent parity through adapter/preset | Host axis is multi-host; parity must land in the same goal, not drift | Codex hook config + smoke that it fires, or a recorded blocker if the mechanism differs | pending |
| 4 | AGENTS.md durable rule via the `setup` skill; align CLAUDE.md/handoff.md; improve the `handoff` skill's pickup contract; **resolve #238** — setup Skill Routing text names `find-skills` as a skill (not a bare command), stays compact, no rerun drift | The durable contract behind the gate; setup owns the AGENTS.md/CLAUDE.md surface — same surface #238 fixes | AGENTS.md rule; #238 acceptance criteria met; handoff skill pickup contract; gates green | pending |
| 5 | **Resolve #239** — tighten `achieve`'s before-phase/activation contract: require ≥1 high-leverage question on real mode ambiguity (artifact-only vs. implementation-continuation), state the assumption when skipping, and make the activation line + inert-until-`/goal` status operationally hard to miss (closeout checklist for `Goal file:`/`Activation:`) | Folded per user; this very run exposed the gap (a no-question before-phase) so the lesson is live | `achieve` SKILL.md / lifecycle contract updated; self-test or fixture pinning the activation-closeout shape; gates green | pending |

## Slice Log

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

_Filled at completion (next session). Must record the honest ceiling as a
non-claim: a SessionStart hook strengthens routing via context-recency but does
not hard-force a Skill invocation; only a front-load-output design would, and it
was deliberately not chosen._

## User Verification Instructions

_Filled at completion._

## Auto-Retro

_Filled at completion via the `retro` skill._
