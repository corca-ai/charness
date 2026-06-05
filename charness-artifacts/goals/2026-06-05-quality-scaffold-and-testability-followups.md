# Achieve Goal: Quality scaffold generalization and testability backlog

Status: draft
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-quality-scaffold-and-testability-followups.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (shaped, inert until `/goal`).
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-05-quality-scaffold-and-testability-followups.md`.
- Timebox: 3h. Closeout reserve: 30m. Done-early policy: continue_next_improvement.
- Activation time: (set at `/goal` activation).
- Discuss before activation: RESOLVED with the user on 2026-06-05. (a) Broad
  bundle scope: item 3 (convert the ~121 boundary-bypass "convertible"
  subprocess tests) is intentionally BOUNDED to the import-safe `inventory_*`
  cluster plus a documented pattern; remaining convertibles defer to a follow-up
  goal (chose bounded `inventory_*`-first over all-121-in-one-goal and over
  excluding item 3). (b) Live/production proof: none is claimed — no Cautilus
  run (consult `plan_cautilus_proof.py` first) and no push/remote state; closeout
  proof is local deterministic gates plus per-slice fresh-eye critique. No
  unresolved consequential activation discussion remains.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Generalize the artifact-scaffold pattern across the repo's statically-validated
artifacts and advance the test-DSL testability backlog, in three bundled items
(item 1 first): (1) build `scaffold_<skill>_artifact.py` for the four validated
artifacts that still lack one — `handoff`, `ideation`, `retro`, `critique` —
mirroring the shipped `debug` + `quality` scaffolds, each with a dogfood test
and a consumer-export portability test; (2) update
`docs/testability-dsl-initiative.md` to move the boundary-bypass ratchet from
Remaining to Done (it is now the passing `check-boundary-bypass-ratchet` gate);
(3) bounded DSL goal-1 work: convert the import-safe `inventory_*` cluster of
boundary-bypass "convertible" subprocess tests to in-process calls, skipping
targets that shell out internally, and record the baseline drop.

## Non-Goals

- Do not execute any slice during the Before phase or before `/goal` activation.
- Do not convert all ~121 boundary-bypass candidates in this goal; item 3 is
  bounded to the `inventory_*` cluster plus a documented pattern, and the rest
  is a follow-up goal.
- Do not convert targets that spawn git/subprocess internally; the boundary
  stays for those, and only genuinely import-safe targets convert.
- Do not lower the `scripts/boundary-bypass-baseline.json` baseline via
  exemptions to fake item-3 progress; baseline drops must reflect real
  in-process conversions.
- Do not edit the `validate_<skill>_artifact.py` contracts to fit the new
  scaffolds; scaffolds must match the existing validators (drift is caught by
  the dogfood test re-running the real validator).
- Do not push to origin; push stays a maintainer decision.

## Boundaries

- Reference pattern: `skills/public/debug/scripts/scaffold_debug_artifact.py` +
  `tests/test_debug_scaffold.py`, and this session's
  `skills/public/quality/scripts/scaffold_quality_artifact.py` +
  `tests/test_quality_scaffold.py` (commit `be7dec8e`). Mirror their
  adapter-resolution and 3-test shape (dogfood + symlink-pointer +
  consumer-export).
- Each new scaffold's emitted template must pass its existing
  `scripts/validate_<skill>_artifact.py` out of the box.
- Generated plugin mirrors (`plugins/charness/...`) must be synced
  (`sync_root_plugin_manifests.py`) before validators and staged with source;
  SKILL.md ceilings are tight, so surface each scaffold minimally.
- item 3 follows `docs/testability-dsl-initiative.md` Remaining item 2: start
  the import-safe `inventory_*` cluster, build on-disk fixtures with
  `Repo().build()` from `tests/dsl.py`, skip internally-spawning targets, and
  update the ratchet baseline to reflect each conversion.
- `pythonpath = [".", "scripts"]` (commit `a7449e8a`) is the test import
  baseline; in-process conversions import `scripts` modules at the top.

## User Acceptance

What the user can do to verify completion directly.

- Run each new `scaffold_<skill>_artifact.py --json` on a temp repo with the
  matching adapter and see a skeleton that passes its validator unedited.
- Confirm the 4 new scaffolds + tests are committed with synced mirrors and the
  full read-only quality gate is green.
- Inspect `docs/testability-dsl-initiative.md`: the boundary-bypass ratchet is
  under Done (shipped), not Remaining.
- For item 3: see the `inventory_*` cluster tests converted to in-process
  calls, the boundary-bypass baseline `candidate_count` dropped by the converted
  count (not by exemption), and the full gate green.

## Agent Verification Plan

### Low-Cost Checks

- Focused `pytest` per new scaffold test and per converted item-3 test module.
- `ruff` / `py_compile` on touched scripts; `check_python_lengths.py` on touched
  Python; `check-doc-links` / `check-markdown` for the doc edit.

### High-Confidence Checks

- `./scripts/run-quality.sh --read-only` at slice/bundle boundaries.
- `check_boundary_bypass_ratchet.py` after item-3 conversions, with the baseline
  regenerated to reflect real conversions.
- Bounded fresh-eye critique per substantial slice; `check_goal_artifact.py`
  before completion.

### External Or Live Proof

- No Cautilus run claimed unless explicitly requested; consult
  `plan_cautilus_proof.py` first. No push / remote state claimed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Build `scaffold_{handoff,ideation,retro,critique}_artifact.py` mirroring debug/quality | item 1; mechanical, low-risk, proven pattern | 4 new scripts + synced mirrors; per-skill dogfood + consumer-export tests green | pending |
| 2 | Move the boundary-bypass ratchet to Done in `docs/testability-dsl-initiative.md` | item 2; doc drift — the gate already ships | doc edit; check-doc-links/markdown green | pending |
| 3 | Convert the import-safe `inventory_*` boundary-bypass cluster to in-process; skip internal shell-outs | item 3; raises production testability; bounded start | converted cluster tests green; baseline candidate_count drop recorded; pattern documented | pending |
| 4 | Verify, critique, retro, complete | closeout | full gate; per-slice fresh-eye critique; retro; goal check | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

_Empty until `/goal` activation._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- This session's commits: `be7dec8e` (portable quality scaffold), `a7449e8a`
  (pythonpath + E402 sweep, suppressions 70→34), `8dcae556` (2026-06-05 quality
  posture review).
- `docs/testability-dsl-initiative.md` — DSL initiative record; the ratchet is
  still listed under Remaining (item 2 fix) and item 4/backlog framing for item 3.
- Reference scaffolds: `skills/public/debug/scripts/scaffold_debug_artifact.py`,
  `tests/test_debug_scaffold.py`,
  `skills/public/quality/scripts/scaffold_quality_artifact.py`,
  `tests/test_quality_scaffold.py`.
- Contracts to scaffold against:
  `scripts/validate_{handoff,ideation,retro,critique}_artifact.py`.
- item-3 surface: `scripts/inventory_boundary_bypass_lib.py`,
  `scripts/boundary-bypass-baseline.json`,
  `scripts/boundary_bypass_ratchet_lib.py`, `tests/dsl.py`.
- `charness-artifacts/quality/latest.md` — this session's posture review.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Execution timing: chose draft-now / execute-next-session (artifact-only).
  Rejected starting slices now because the user explicitly deferred execution.
- Scope decision: chose all three items bundled, item 1 first. Rejected
  item1+2-only (item 3 is the testability payoff the user wants tracked) and
  all-121-in-one-goal (broad-scope risk).
- item-3 bounding: chose the import-safe `inventory_*` cluster first, N per
  slice, skip internal shell-outs, done = one cluster converted + pattern
  documented. Rejected converting all 121 in this goal per the DSL doc's own
  sequenced guidance.
- Timebox: chose 3h with `continue_next_improvement` on done-early. Rejected a
  no-timebox slice-sequence-only run.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique. (Pre-activation
self-critique; full per-slice fresh-eye critique runs during execution.)

- Scaffold-drift risk: a scaffold hardcodes its validator's required structure.
  Folded into Boundaries — each scaffold's dogfood test re-runs the real
  `validate_<skill>_artifact.py`, so validator changes turn the test red.
- item-3 baseline-gaming risk: a baseline drop could be faked via exemptions
  instead of real conversion. Folded into Non-Goals — baseline drops must
  reflect real in-process conversions.
- SKILL.md ceiling risk: the quality SKILL.md edit this session landed at
  199/200; the four target skills may be similarly tight. Folded into Boundaries
  — surface each scaffold minimally and run `check_skill_surface_preflight.py`.
- Over-worry not folded: full 121-conversion completeness — deliberately
  deferred to a follow-up goal, not a blocker for this one.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

_Filled in the After phase._

## User Verification Instructions

_Filled in the After phase._

## Auto-Retro

_Filled in the After phase._
