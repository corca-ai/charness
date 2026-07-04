# Achieve Phase-Brief Demote Code Critique

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Packet Consumed: `charness-artifacts/critique/2026-07-04-015218-packet.md`.
Target: `code-critique.md`.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- host exposure state: unsupported
- application state: host exposes `model` only; angle + counterweight
  reviewers spawned as bounded fresh-eye subagents on `sonnet` (operator
  standing instruction: lower-power models for delegated work)

## Diff Scope

achieve phase-keyed dispatch demote: `check_goal_artifact.py` emits an
advisory `phase_brief` (status → `references/lifecycle.md` phase section +
`references/goal-artifact.md` sections); SKILL.md Workflow intro routes
section reads through it; claim-fidelity spec rationales updated; new test
file guards the section names against fenced-example false matches.

## Capability at Stake

Cutting the 52KB+16KB always-load a compliant achieve run pays, without
stranding phase depth or introducing a new fidelity overclaim.

## Angles

- Michael Jackson (framing), Gerald Weinberg (diagnostic), Atul Gawande
  (operational) — bounded fresh-eye subagents; separate counterweight pass.

## Findings

### Act Before Ship (all applied pre-commit)

- spec.json rationales overclaimed "a representative run engages the
  phase-scoped section" while the Slice-7 capture showed faithful runs may
  open ZERO docs — rewritten to advisory-honest wording (routes a run that
  opens the doc; RSF token stays the teeth).
- spec.json `_comment` still asserted the deleted "full contract" co-routing
  — marked HISTORICAL with the 2026-07-04 supersession.
- SKILL.md routing sentence never named `closeout_handoff`, so an
  active-status closeout run had no cue to read `## After` — one clause
  added.
- Closeout economics honesty: the real win is Before-phase (~11KB vs 51KB);
  an active-status closeout run still reads ~40KB (## During + ## After).
  Stated here and to be stated in the A/B finding — no blanket "cut 52KB"
  claim.

### Bundle Anyway (applied)

- Test `_heading_present` dropped its `startswith` clause (latent
  rename-mask) — exact-line match only.

### Over-Worry

- "lifecycle.md has a 5th real H2 `## Remaining Boundary Matrix` the brief
  drops" — REFUTED twice independently: line 350 is inside a ```md fence;
  the real matrix subsection is an H3 under `## During`, which blocked/active
  already route to.
- Unguarded module import crash risk — matches the 4 existing sibling
  imports' convention exactly; the module's "never a blocking floor" wording
  uses the repo's established verdict-scoped sense of floor.
- pursue-ready vs main-branch status divergence — refuted: same pure
  function on the same string.

### Valid but Defer

- SKILL.md lines ~101/~162 still cite whole-file lifecycle.md — context-
  scoped/attribution prose, no test pins them, lower leverage than the
  applied clause given 14-line core headroom; revisit only if a capture
  shows over-reading from those lines.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` Repeat Traps: "edited the
generated mirror, not the source" — avoided; all edits went to
`skills/public/` and were mirror-synced via `sync_root_plugin_manifests.py`.

## Capability Gap

None — the brief reuses the existing every-invocation bootstrap script; no
new gate, planner, or integration is implied.

## Pre-Merge Action

All Act-Before-Ship edits applied; JSON validated; mirrors re-synced;
focused pytest (21) green. Ship.

## Next Move

Commit slice A, then run the pre/post A/B
(`run_skill_efficiency_ab.py`, n=3 per arm, `--judge-cmd`) to check outcome
parity and measure any real efficiency delta — expecting the honest result
may be "no token delta on faithful runs (they already skip the docs); the
gain is contract honesty + a cheap compliant path," which the finding must
state plainly if observed.
