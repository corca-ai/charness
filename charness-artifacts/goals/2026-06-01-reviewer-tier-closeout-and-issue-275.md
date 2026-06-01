# Achieve Goal: Reviewer tier closeout and issue 275

Status: draft
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, tests/proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Deliver the four reviewer-tier waste-prevention improvements and resolve GitHub issue #275 without losing the existing unreleased reviewer-tier commits.

## Non-Goals

- Do not publish or release the accumulated commits unless the user separately
  asks for release/push.
- Do not close #275 until the fix is present in a pushed carrier and GitHub
  verifies the issue state.
- Do not make broad verification run before fresh-eye Act Before Ship findings
  are dispositioned.
- Do not turn adapter scaffold parity into exact field equality; intentional
  evidence-only defaults must remain expressible.

## Boundaries

- Existing local commits `45e4d51`, `9362288`, and `1180991` are in scope and
  must be preserved.
- Issue #275 is the tracked bug source of truth:
  <https://github.com/corca-ai/charness/issues/275>.
- The four improvement requests are:
  1. add a fresh-eye blocker disposition checklist before broad verification,
  2. strengthen reviewer-tier direct-spawn scanning,
  3. add adapter scaffold/example/resolver parity for policy-bearing fields,
  4. make live-state handoff tests avoid exact backlog cardinality.
- #275 must cover installed plugin layout paths where public skills live under
  `skills/<id>/`, not only source-tree `skills/public/<id>/`.

## User Acceptance

- Run the final named verification commands from `## Final Verification`.
- Inspect #275 and see a closeout carrier with explicit `Close #275` semantics
  after push/release is requested.
- In an installed plugin layout, `parse_handoff_entries.py --with-issues` can
  find the configured issue backend and `draft_goal_from_chunk.py --help` no
  longer fails from a source-tree-only sibling import.
- See that broad verification is gated by fresh-eye blocker disposition rather
  than by convention.

## Agent Verification Plan

### Low-Cost Checks

- Targeted unit tests for #275 import resolution and diagnostics.
- Targeted tests for fresh-eye blocker disposition checklist behavior.
- Targeted tests for reviewer-tier direct-spawn scanner.
- Targeted tests for adapter scaffold policy-bearing parity.
- `ruff check` and `py_compile` on changed Python files.

### High-Confidence Checks

- `python3 scripts/check_changed_surfaces.py --repo-root .` and all listed
  planned sync/verify commands for changed surfaces.
- `pytest -q` on affected targeted test modules after each slice.
- Final broad pytest after all fresh-eye Act Before Ship findings have a
  disposition and targeted regression.

### External Or Live Proof

- `gh issue view 275 --repo corca-ai/charness` before and after closeout.
- If a release/push is requested, verify GitHub issue #275 reaches `CLOSED`.
- Installed-layout reproduction should be fixture-backed locally; a real
  consumer-repo proof is preferred only if the activation run has enough time
  and does not mutate that repo unexpectedly.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Fresh-eye blocker checklist | Prevent the just-observed broad-gate waste before more verification-heavy work | helper/gate tests and integration into closeout flow | planned |
| 2 | Reviewer-tier direct-spawn scanner | Make new direct fresh-eye reviewer surfaces fail closed when they omit `high-leverage` tier application | scanner plus tests covering current direct surfaces | planned |
| 3 | Adapter scaffold parity | Catch policy-bearing drift between examples, init output, and resolver-consumed fields | parity helper/tests with explicit intentional-difference allowances | planned |
| 4 | Issue #275 installed-layout fix | Restore handoff issue source and goal draft imports in installed plugin layout | fixture proving `skills/<id>/` layout works and fallback diagnostics surface | planned |
| 5 | Verification, critique, retro, closeout | Prove the bundle without premature broad gates | final validators, broad pytest, critique artifact, retro, issue closeout draft | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

## Slice Log

- Before-phase shaped on 2026-06-01. User asked to achieve all four proposed
  improvements and resolve #275. Execution is intentionally inert until the
  activation command is run.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`
- `charness-artifacts/debug/2026-06-01-reviewer-tier-sibling-scan.md`
- `charness-artifacts/critique/2026-06-01-reviewer-tier-sibling-scan-critique.md`
- GitHub issue #275: <https://github.com/corca-ai/charness/issues/275>
- Existing local commits: `45e4d51`, `9362288`, `1180991`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode: user asked "어치브 해주세요"; chosen value is shaped goal artifact now,
  activation-required execution next. Rejected auto-execution because `achieve`
  explicitly keeps Before-phase artifacts inert until `/goal`.
- Scope: bundle all four proposed improvements plus #275. Rejected splitting
  #275 into a separate goal because the issue and the improvements both touch
  handoff/skill closeout reliability and share final verification cost.
- Release/push: out of scope until explicitly requested. Rejected implicit
  publish because current branch is already ahead of `origin/main` and release
  guardrails require explicit confirmation.
- Issue classification: #275 is bug-class. Rejected feature/deferred-work
  classification because observed installed-layout behavior diverges from the
  expected handoff issue-source contract.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Not yet run. First active slice should run a bounded plan critique before
  implementation if the changed-surface map grows beyond the planned scripts and
  tests.
- Known risk folded in: broad verification must wait until fresh-eye blockers
  are dispositioned.
- Known risk folded in: #275 has an installed-layout path dimension, so tests
  must include `skills/<id>/`, not only source-tree `skills/public/<id>/`.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- None yet.

## Final Verification

- Not run; goal is draft and inactive.

## User Verification Instructions

- Activate with
  `/goal @charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`.
- After activation completes, inspect this file's `## Final Verification` and
  #275 closeout ledger before requesting push/release.

## Auto-Retro

- Not run; goal is draft and inactive.
