# Release Goal Shaping Session Retro

Date: 2026-08-20
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md

## Context

This artifact reviews the reshaping of an inactive single-issue goal into the
next-release operating contract. The user first required all current issues to
inform urgency, then explicitly rejected a narrow goal and said a lower-capacity
model would execute it. Strong local evidence covers the resulting artifact,
issue reads, source probes, validators, and reviewer findings; future issue
qualification and release behavior remain planned rather than proven.

## Window

From shaping HEAD `38775dfeb` through the pursue-ready goal and handoff update,
before activation or implementation.

## Evidence Summary

- All 29 open issue bodies/comments through `#680` were read through the resolved
  issue backend; source probes established `#679` and scoped the `#680` refutation.
- Release and quality planners established current `6.2.0` / `v6.2.0`, planner-
  owned gates, and the two-stage semantic/release candidate boundary.
- Two broad-goal angle reviews, a counterweight, and two execution-readiness
  reviews used bound packets and clean or parent-attributed-clean fingerprints.
- `check_goal_artifact.py --pursue-ready` passed after the runbook repairs.
- Packet Consumed: `charness-artifacts/retro/2026-08-20-093708-packet.md`.

## Waste

- The first reshape narrowed to `#679` even though the original request allowed
  a full structural redesign. Reviewer consensus answered urgency but not the
  user's release-sized intent; the user had to restate the scope.
- A shape-valid draft still left decisions a weaker executor could not safely
  make: fixed-version residue, candidate identity, close-carrier timing, a mixed
  `#669` package, and finally one enum mismatch. The validator checks section
  shape, not operational completeness, so the execution-readiness reads were
  load-bearing rather than ceremonial.

## Critical Decisions

- Chosen: activation-time full backlog with evidence qualification and an intake
  lock. Rejected: ticket quota and one-issue urgency goal. This makes every ready
  repair mandatory without pretending every report is live.
- Chosen: prescriptive per-issue work packages, fixed entry files/tests and safe
  branches, plus append-only amendments. Rejected: leaving implementation
  mechanism entirely to the next model. Current evidence can still override a
  branch, but only visibly.
- Chosen: isolated parallel authoring and serialized integration, with semantic
  and post-bump release candidates bound separately. This constrains version,
  export, release record, publication, and issue closure to parent-owned phases.

## Trends vs Last Retro

The prior adapter-debt retro recorded second-round reviewers repeatedly finding
repairs carrying their own class. This session moved that pressure before
activation: reviewers found contradictions in the plan and then read the repaired
runbook. The remaining one-line enum repair is accepted-unreviewed, explicitly
rather than silently treated as covered.

## North Star Alignment

The work followed `docs/design-north-star.md` by keeping deterministic teeth at
the issue-ledger, proof-surface, release-lock, and publication boundaries, while
leaving issue qualification and product policy to judgment. The first narrow
draft mis-applied the capable-judge facet: it optimized the reviewers' local
urgency answer over the operator's larger release objective. The repaired goal
uses different observers and evidence channels at the irreversible boundary and
does not turn every planning preference into a blocker.

## Expert Counterfactuals

- An Ousterhout-style complexity lens would have asked for the execution
  interface first: exact state machine, ownership, and failure transitions. That
  would have exposed semantic-candidate versus release-candidate identity before
  the first broad draft.
- A Klein pre-mortem for a lower-capacity executor would ask “which ambiguous
  sentence produces a plausible but wrong action?” Applying it yielded the enum,
  close-carrier, version, and mixed-package checks; use that question before the
  first critique packet on future broad goals.

## Sibling Search

- same layer: broad achieve goals | decision: same waste, fix now | proof: this goal now carries an Execution Runbook, closed decision table, path ownership, and failure states
- abstraction up: achieve Before-phase template | decision: valid follow-up outside the slice | proof: the current validator reports pursue-ready while explicitly not checking section content | follow-up: deferred docs/handoff.md#discuss
- specialization down: release and issue work packages | decision: diagnostic-only | proof: the release/issue skills already own their irreversible transitions; this goal binds rather than duplicates them
- mental-model siblings: handoffs to lower-capacity executors | decision: intentional boundary | proof: repo handoff stays compact and points to the canonical goal instead of copying its runbook

## Portable Candidate

- Abstract pattern: a structurally valid plan can remain non-executable when its
  state transitions, ownership, and enum values are only implicit.
- Triggering evidence: two readiness rounds found six semantic ambiguities and
  one closed-enum contradiction after pursue-ready was already green.
- Intended consumer: repos handing a broad multi-lane goal to a less capable or
  less context-rich agent.
- Destination: `create-skill` enhancement to achieve/spec planning, deferred via
  `docs/handoff.md#discuss` rather than added to this release train.
- First-prompt acceptance: given a multi-lane release goal, the skill emits one
  closed state machine, per-lane entry files/tests/stop conditions, and no value
  outside its declared enums.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":6,"session_id":"2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b","status":"effect-recorded"}

## Next Improvements

- workflow: ask for executor capacity and irreversible target before the first
  scope critique; then review the exact state machine, not only goal coherence.
- capability: teach achieve/spec an optional lower-capacity execution runbook
  shape with closed enums and candidate-transition checks.
- memory: keep the detailed runbook in the goal and only the activation pointer,
  release grant, and first slice in `docs/handoff.md`.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-20-release-goal-shaping.md
