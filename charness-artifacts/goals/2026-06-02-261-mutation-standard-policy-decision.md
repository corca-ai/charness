# Achieve Goal: #261 mutation-standard policy decision

Status: draft
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`.
- Verification cadence: decision brief and focused issue/source reads first;
  cheap deterministic checks at commit boundaries if implementation becomes
  necessary; fresh-eye critique at the policy decision and final closeout
  boundary; broad proof only after the policy slice is stable.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files or decision artifacts, expected invariants, tests/proof, non-claims, and
  reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve GitHub issue #261 as a bounded mutation-standard policy decision: decide
whether the remaining coordination-cues mutation survivors should be closed as
accepted equivalent/low-value residue, require a repo-owned equivalent-mutant
exclusion rule, or become a smaller follow-up with explicit proof. This
Before-phase artifact is draft-only; execution starts only after `/goal`
activation.

## Non-Goals

- Do not re-run the full #261 coordination-cues survivor campaign by default.
  Prior proof already records 514/514 executed, 467 killed, 47 survived, and a
  90.9% reachable score.
- Do not lower the mutation score floor, changed-line floor, sampling budgets,
  or workflow thresholds to make the issue closable.
- Do not chase survivors already classified by prior fresh-eye critique as
  equivalent or low-value unless a new proof contradicts that classification.
- Do not fold #184 product-success work, #273/#274 regression recovery, or a
  release/version bump into this goal.
- Do not close #261 silently. If it closes, the carrier must make the policy
  decision explicit and use the `issue` closeout path.

## Boundaries

- Treat GitHub issue #261 as the live source of truth for state and current
  comments. Local handoff and older goal artifacts are context, not issue state.
- The residual question is policy/decision-needed after mechanical survivor
  hardening, not another broad coverage-fix campaign unless the first slice
  proves a real, user-visible contract gap.
- In scope: existing #261 body data, prior survivor triage artifacts, prior
  fresh-eye critique, mutation policy references, and focused implementation
  only if the decision requires a repo-owned filter/rule/test.
- Out of scope without user confirmation: new global equivalent-mutant exclusion
  policy, any threshold change, any irreversible issue close that lacks an
  explicit policy rationale, or filing broad follow-up issues.
- Stop and ask before choosing a new policy rule that changes what future
  mutation runs count or exclude. Closing #261 as "accepted equivalent/low-value
  residue" is also a policy decision and must be named in the carrier.

Discuss before activation: this goal is shaped to decide and possibly close
#261, but it must not auto-close the issue merely because prior mechanical
hardening exists. Activation should confirm that a policy decision, a narrow
follow-up, or an explicit leave-open comment are all acceptable outcomes; broad
live mutation proof and remote GitHub issue closure are non-claims until run and
verified.

## User Acceptance

- Read the final #261 carrier/comment and see one explicit disposition:
  `close as policy-resolved`, `leave open with a narrower policy question`, or
  `split/file a focused follow-up`.
- Inspect the goal artifact and issue carrier to see why the chosen disposition
  follows from current #261 evidence, prior scoped proof, and fresh-eye critique.
- If code/tests change, run the named focused tests or validators and see they
  cover the changed rule. If no code changes, see the no-change rationale and
  policy proof instead.
- After publication, verify GitHub issue #261 is in the expected state and has
  the expected close/comment text.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `gh issue view 261 --json number,title,state,body,comments,labels,url,updatedAt`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/find-skills/scripts/list_capabilities.py --repo-root . --read-only --recommend-for-task "<current boundary>"`
- Re-read prior proof anchors:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`,
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`,
  and `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`.
- If artifacts or docs change, run `python3 scripts/check_changed_surfaces.py --repo-root .`.
- If tests are added or expanded, include a cheap duplicate/length pressure
  sample before slice closeout.

### High-Confidence Checks

- A decision brief that classifies #261 as `decision-needed` unless the first
  slice finds a concrete bug-class behavior divergence.
- Fresh-eye critique of the decision packet before final closeout, focused on
  whether the chosen disposition confuses equivalent mutants, low-value
  survivors, and untested real contracts.
- If implementation is needed, focused tests for the exact changed helper/rule
  plus `ruff` or pycompile for touched Python.
- Final closeout gate after the mutation set is stable:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`, or
  a documented substitute if no code/test surface changed and the repo-local
  contract makes the full gate disproportionate.

### External Or Live Proof

- GitHub issue reads through the selected issue backend (`gh`) before and after
  closeout.
- If #261 is closed, stage the close through `issue` with an explicit close
  keyword in the carrier body or an issue-verified manual fallback.
- Do not claim a fresh scheduled mutation workflow, live GitHub Actions proof,
  or remote issue closure unless observed after publication.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape #261-only goal | User invoked `charness:achieve #261` after handoff named #261 as the live mutation-standard policy question | Goal artifact passes `check_goal_artifact.py --pursue-ready`; gathered issue snapshot exists; activation discussion names close/split/proof non-claims | done |
| 1 | Build #261 decision brief | The issue is decision-needed; decide before mutating code or re-running broad mutation proof | Brief classifies accepted residue vs rule/filter vs focused follow-up; open policy decisions are surfaced before design | planned |
| 2 | Implement only the chosen narrow outcome | Avoid another survivor-hardening campaign unless the brief proves code/tests are required | Either no-change carrier with policy proof, or focused code/tests and deterministic verification for the selected rule | planned |
| 3 | Critique, verify, and stage issue disposition | Repo closeout requires fresh-eye review, proof, and issue discipline | Fresh-eye critique; final validation or documented substitute; issue carrier/comment draft validated; goal closeout evidence bound | planned |

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

Routing: startup `find-skills` recommended public `achieve`, with `issue` and
`gh` as the supporting route for the tracked GitHub issue. During activation,
ask `find-skills` again at policy/validation boundaries rather than baking a
phase-to-skill map into this artifact.

Gather: charness-artifacts/gather/2026-06-02-github-issue-261-mutation-standard-policy.md

Release: n/a - this goal does not plan a version bump, install-manifest edit,
or release surface.

Issue closeout: planned - use the `issue` workflow before completion; replace
this line with a carrier/comment artifact or an explicit leave-open verifier
before flipping the goal to complete.

## Slice Log

No slices executed yet. This goal is draft-only until the user activates it with
`/goal @charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`.

## Context Sources

- Gathered live issue snapshot:
  `charness-artifacts/gather/2026-06-02-github-issue-261-mutation-standard-policy.md`
- GitHub issue: https://github.com/corca-ai/charness/issues/261
- Handoff route: `docs/handoff.md`
- Quality posture: `charness-artifacts/quality/latest.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Prior #261 policy critique:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
- Prior bounded goals:
  `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`
  and
  `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- Prior issue carriers:
  `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`
  and
  `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`

## Interview Decisions

- Mode: user invoked `charness:achieve #261`, so this is the Before-phase draft
  for a later implementation-continuation run. Rejected alternative:
  immediately pursuing slices in this turn, because `/goal` activation is the
  explicit execution boundary. Axis note: single-point per-goal lifecycle mode,
  not a host/provider axis.
- Scope: choose #261-only mutation-standard policy decision. Rejected
  alternatives: re-bundling #273/#274, because their goals are complete and left
  #261 open intentionally; broad survivor hardening, because prior proof and
  critique already narrowed the remaining question to equivalent/low-value
  policy. Axis note: issue tracker is GitHub for this repo run, but issue-source
  handling is host-variable; use `issue` rather than hardcoding GitHub-only
  closeout behavior into reusable surfaces.
- Acceptable outcomes: close #261 only with explicit policy proof, leave it open
  with a sharper decision question, or file/split a narrow follow-up after user
  confirmation. Rejected alternative: treating prior mechanical hardening as
  sufficient to close #261 without a policy statement. Axis note: single-point
  policy disposition for this issue, not a profile/env default.
- Proof cost: start with issue/source rereads and a decision brief; run focused
  validators if code/tests change; reserve broad closeout until the slice is
  stable. Rejected alternative: full mutation/broad pytest as readiness
  discovery, which recent retros identify as waste.

## Plan Critique Findings

- Prior fresh-eye provenance:
  `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
  found no blockers in the bounded survivor triage and said the remaining
  survivors are defensibly equivalent or low-value. This finding is folded into
  Non-Goals and the Slice Plan by making policy disposition the first real
  slice, not broad survivor hardening.
- Same-session Before-phase critique: the main failure risk is accidental issue
  closure by inertia. Folded response: `Discuss before activation:` explicitly
  names close/split/leave-open outcomes and the issue closeout cue starts as
  planned, not satisfied.
- Over-worry not folded: a fresh full scoped mutation run could give newer
  numbers, but it is not required before the policy brief because the issue's
  current comments already define the open question as policy residue. Run it
  only if the brief identifies a concrete contradiction in existing proof.

## Off-Goal Findings

N/A - none during shaping.

## Final Verification

Pending activation and execution.

## User Verification Instructions

Pending activation and execution. Before activation, inspect the draft and
confirm the consequential defaults above, especially that #261 may close only
with explicit policy proof and that live mutation/GitHub Actions proof is not
claimed unless observed.

## Auto-Retro

Pending activation and execution.
