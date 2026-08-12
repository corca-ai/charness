# R5 Judge-Intent Scenario Critique

Date: 2026-08-12

## Execution

Two bounded, read-only fresh-eye rounds reviewed the new handoff
`judge-intent` scenario and the repaired observation floor. Both reviewer
boundary fingerprints verified clean. Round 2 found one additional bypass in
the repaired proof; the parent fixed it and records that final repair as
accepted-unreviewed under the mandatory two-round cap.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- Requested tier: n/a — host inherited the session model.
- Requested spawn fields: unnamed bounded read-only reviewer scope, exact
  scenario/registry/validator/runtime/test paths, and blocker/major/minor
  reporting through the host agent interface.
- Host exposure state: metadata-hidden
- Application state: the host returned no reviewer-tier application metadata.
- Delivery state: findings-received

## Boundary Ownership

- Producer: the `judge-intent` fixture owns the route-undetermined handoff
  scenario declaration; `build-skill-execution-observation.mjs` owns its
  run-observation verdict.
- Consumer: the Cautilus observation packet and the conditional-reads
  cross-check consume the fixture's actual-read evidence.
- Owning surface: the handoff claim-fidelity registry plus the agent-runtime
  observation matcher.
- Verdict: owned-correctly

## Target

Proof-surface critique: a route-undetermined scenario that must exercise the
handoff planner's `judge_from_user_request` safety-net before selecting a
route.

## Change

Register `handoff/judge-intent`; require its prompt to run `--intent auto`
without preselecting pickup, refresh, or chunked routing; replace name-match
fragments with `requiredOpenedReferences`; and retain the discharged waivers as
stale advisories while preserving the unhealthy-adapter waiver.

## Capability at Stake

An evaluator can now distinguish a real safety-net reference read from a
filename mention or a mutation of that reference, so the least-certain route
cannot report coverage without the documents that govern its decision.

## Findings and Counterweight Triage

- R1-M1 | act-before-next-review | The initial neutral wording let an agent
  declare pickup or refresh directly, never entering the safety-net. Repaired
  by requiring `--intent auto` before any route declaration while leaving the
  route itself unspecified.
- R1-M2 | act-before-next-review | `requiredCommandFragments` could pass on a
  basename in an `echo`, search pattern, or explanation. Repaired with an
  explicit actual-read floor (`requiredOpenedReferences`) and a name-drop
  regression test.
- R2-M1 | act-before-commit | The first actual-read implementation trusted the
  broad activity set, where `Edit`/`Write` file paths looked opened. Repaired
  by separating `collectReadBasenames` (only `Read` and parsed shell reads)
  from the advisory activity coverage set, with `Write`/`Edit` bypass tests.
  This round-2 repair is accepted-unreviewed under the two-round cap.
- Confirmed | `workflow-trigger.md` and `state-selection.md` now have
  engage-always scenario coverage, so their historical allowlist lines are
  intentionally stale advisories; `adapter-contract.md` remains the sole live
  waiver because its unhealthy-adapter fixture is a different condition.
- Confirmed | No Cautilus invocation, captured result, hosted proof, release,
  push, or issue-closeout claim was introduced.
- Over-worry | Do not turn all declared-reference coverage into a hard verdict:
  this slice needs a strict floor only for the two route-decision references;
  broad coverage remains an advisory measurement.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — a proof surface must observe the
actual consumer action rather than a nearby textual spelling or mutation.

## Deliberately Not Doing

- No live Cautilus execution: its planner returned `next_action: none` and
  requires an explicit log-backed behavior proof request in addition to a
  scenario-specific grant.
- No ruling-5 execution-status change, push, release, hosted readback, or
  issue closure.

## Pre-Merge Action

Focused Python and Node regression tests, claim-fidelity and
conditional-read validators, and the final read-only quality gate must pass.
