# Achieve Goal: 3h Quality Test Economics

Status: active
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-3h-quality-test-economics.md`

This file is the living goal scratchpad for the active run.

## Active Operating Frame

- Current slice: 1 — refresh the current quality and pytest-economics posture.
- Next action: collect current runtime, standing-test economics, and nose
  advisory data; then select the first implementation target.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Run a three-hour post-release quality improvement goal focused on reducing Charness pytest and lifecycle-test cost while preserving behavior proof. Use nose advisory output to find refactoring candidates, but do not chase clone-count reduction when test economics or proof clarity is the higher-value quality move.

Discuss before activation: RESOLVED in-thread on 2026-06-05. The user selected
the three-hour quality goal, clarified that closeout may finish after the
timebox once started, and asked to continue to the next improvement if the
planned goal closes with meaningful time remaining. No live, provider, release,
or external proof is expected unless a selected slice unexpectedly requires it.

## Non-Goals

- Do not mechanically chase nose clone counts, especially bootstrap and plugin
  portability patterns whose duplication may be cheaper than shared coupling.
- Do not remove slow or long tests unless equivalent behavior proof remains at
  a cheaper layer or as one intentionally thin boundary smoke.
- Do not change release versions, publish a release, or edit install manifests.
  Version `0.18.0` was already released before this goal.
- Do not broaden into unrelated product, issue, or documentation cleanup merely
  because quality inventory surfaces it.

## Boundaries

- Timebox active improvement work to three hours from activation. If closeout
  begins before the timebox expires, finish closeout even if that crosses the
  three-hour wall.
- If the planned goal closes early and meaningful time remains, continue with
  the next highest-value quality improvement under the same boundaries.
- Primary quality target: pytest and lifecycle-test economics, especially
  duplicated subprocess, fixture-copy, or source-guard proof.
- Secondary target: nose-surfaced refactoring only when it removes real
  maintenance burden without weakening plugin portability or public support
  independence.
- Proof preservation: every deleted, demoted, or split expensive test must leave
  helper-level, in-process, or representative CLI smoke proof for the same
  user-visible behavior.
- Commit discipline: each meaningful slice ends with focused checks, surface
  sync when relevant, critique when non-trivial, and a clean commit before
  moving to the next slice.
- Broad proof: run broad non-release pytest at final closeout if standing test
  behavior changed; run release-specific quality only if release-only tests or
  release surfaces changed materially.

## User Acceptance

- Inspect the final commit list and see at least one committed quality
  improvement that reduces expensive or duplicated pytest proof while preserving
  representative behavior checks.
- Re-run the listed focused checks and broad/substitute checks from `## Final
  Verification`.
- Review nose and test-economics before/after notes and see why chased or
  rejected candidates were chosen.
- Confirm any skipped broad, release, live, or provider proof is explicitly
  called out as a non-claim.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch` before and after each slice.
- `python3 scripts/check_python_lengths.py --paths <touched python files>` for
  Python edits, plus repo-native formatting/lint on touched files where
  available.
- Focused `pytest` for touched tests and their owning helpers.
- Nose advisory inventory with `NOSE_BIN=/home/hwidong/codes/nose/target/release/nose`
  when selecting or validating duplication refactors.

### High-Confidence Checks

- Broad non-release `pytest` at final closeout when the standing pytest surface
  changes.
- Release quality only if release-only tests or release/install surfaces change.
- `python3 scripts/check_changed_surfaces.py --repo-root .` before committing
  meaningful repo work.
- Fresh-eye critique for any non-trivial test deletion, demotion, public helper
  extraction, or quality-contract change.

### External Or Live Proof

- No external, provider, or live proof is planned. If a candidate unexpectedly
  requires it, stop and record the proof gap instead of substituting local tests.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Refresh the current quality and pytest-economics posture. | The target must come from current runtime, duplicate, and test surface data, not yesterday's intuition. | Runtime summary, standing-test economics, nose advisory sample, selected target rationale. | in_progress |
| 2 | Convert one duplicated expensive pytest proof cluster into cheaper helper-level proof while keeping one boundary smoke. | This best matches the user's preference for equal confidence with less code and time. | Focused before/after test commands, retained representative boundary proof, critique notes. | pending |
| 3 | Apply one nose-surfaced refactor only if it is clearly extractable and low risk. | Nose should guide real simplification, not become the objective. | Before/after nose excerpt, focused tests, plugin/support sync if relevant. | pending |
| 4 | Finalize and close out. | The goal must leave audited evidence, committed artifacts, and honest non-claims. | Broad or substitute proof, final artifact status complete, retro dispositions, clean committed tree. | pending |

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

Routing: `find-skills` was already used for this task-oriented session; the
active route is `achieve` for the goal lifecycle and `quality` for current gate,
test-economics, and nose-advisory decisions.
Gather: n/a — no external URLs, Slack, Notion, Docs, Drive, or other external
source is being used as working context.
Release: n/a — this goal intentionally follows the completed `0.18.0` release
and must not bump or publish.
Issue closeout: n/a — no tracked GitHub issue is being closed by this goal.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-05: run a three-hour quality goal after the first
  release, use nose actively but not exclusively, prefer shorter/faster pytest
  when confidence is unchanged, finish closeout even if it crosses the timebox,
  and continue to the next improvement if the primary goal closes early.
- Repository pickup state: `main` clean except for this draft artifact and ahead
  of `origin/main` by two post-release quality commits.
- Recent runtime posture from the prior quality pass: `check-coverage` around
  42s with a 45s budget, pytest around 21-27s median with a 140s budget,
  `check-current-pointer-writes` around 13s, `check-duplicates` around 10s, and
  `check-test-completeness` around 8s.
- Recent standing test economics: 244 Python test files, 107 nested
  CLI/subprocess fanout files, and clean pytest temp footprint.
- Recent nose advisory posture: top candidates included runtime bootstrap,
  adapter init/resolve blocks, `_string`/`optional_string`, `_mask_fences`, and
  `_git_paths`; these are advisory candidates, not automatic refactor orders.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Timebox: chose three hours because the user requested it. Closeout may cross
  the wall if already started; this prevents incomplete artifacts from saving a
  few minutes at the cost of trust.
- Primary target: chose pytest/lifecycle economics over pure clone-count
  reduction because the user wants less code and time when proof strength stays
  equal.
- Nose role: advisory. Nose can identify refactoring candidates, but the win is
  maintainability or cheaper proof, not a lower duplicate score.
- Jscpd role: out of scope for this run. Markdown duplicate gating stays on the
  existing document-only checker; code clone gating is deferred until after
  nose-led refactoring.
- Proof shape: prefer moving proof down to helper/in-process seams while keeping
  one boundary smoke. Rejected wholesale deletion because it can hide CLI,
  adapter, or packaging regressions.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Risk folded: reducing long pytest files can accidentally delete the only CLI
  or mutation-boundary proof. Boundary now requires a retained representative
  smoke or cheaper equivalent proof.
- Risk folded: nose can encourage noisy clone-count chasing. Non-goals and slice
  plan now require real maintenance or test-economics value before refactoring.
- Risk folded: broad pytest can consume a large share of a three-hour window.
  Verification cadence reserves broad proof for final closeout or substantial
  behavior surface changes.
- Over-worry not folded: coverage runtime may be the largest current quality
  hot spot, but the user explicitly prioritized pytest economy and proof design.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- None at shaping time.

## Final Verification

- Not run yet; the goal is not complete.

## User Verification Instructions

- After completion, review the final verification commands and re-run the
  commands that match the changed surface. If final proof lists only focused
  checks, treat broad/release/live proof as an explicit non-claim.

## Auto-Retro

- Not run yet; the goal is not complete.
