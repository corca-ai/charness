# Achieve Goal: Repair the quality-planning and closeout-surface backlog

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-repair-quality-planner-and-closeout-surface.md`
Timebox: no user-supplied limit; stop only at a real decision or external-proof boundary
Activation time: 2026-08-12T08:58:29Z
Closeout reserve: reserve the final slice for frozen-state proof, critique, and lifecycle records
Done-early policy: continue_next_improvement

## Active Operating Frame

- Current slice: #604 — decide canonical-gate recognition before changing shipped default matching.
- Current slice intent: obtain the queued operator policy choice, then bound any recognition repair to that decision.
- Next action: choose whether default canonical patterns may widen for consumer repos or must remain override-only; do not mutate #604 defaults before this answer.
- Verification cadence: focused deterministic checks at commit boundaries; fresh-eye critique and stronger proof at each quality or closeout verdict slice; final lock only after the five slices are frozen.
- Gate cadence: obtain `quality` recommendations before slow gates or any change to a gate, validator, or generated quality packet; do not run Cautilus unless newly approved.
- Slice review packet: state the issue JTBD, changed/generated surfaces, preserved consumer boundary, expected invariants, proof, non-claims, and reviewer questions before each fresh-eye review.
- History boundary: keep this frame current; move completed detail to `## Slice Log` and owning evidence artifacts.

## Goal

Complete the ordered backlog slices [#603](https://github.com/corca-ai/charness/issues/603), [#604](https://github.com/corca-ai/charness/issues/604), [#581](https://github.com/corca-ai/charness/issues/581), [#594](https://github.com/corca-ai/charness/issues/594), and [#593](https://github.com/corca-ai/charness/issues/593). The outcome is an executable quality-planning path for adapter-owned consumer repositories, deliberate canonical-gate recognition, a valid shipped issue adapter example, and closeout guidance/floors that agree with their enforced scope.

## Non-Goals

- No push, release, version bump, remote-CI claim, consumer-runtime claim, or closure of the five tracked issues without a later phase-scoped grant and their individual issue closeout floor.
- Do not bundle the already-completed #585, #596, or #598 closeouts into these implementation slices.
- Do not broaden `#604` into a new consumer enforcement default before its explicit policy decision and release-note obligation are recorded.
- Do not use a generic gate to solve #593 or #594; preserve their narrow target-binding and live-floor ownership.

## Boundaries

- #603 may use only adapter-declared quality commands or return a typed unavailable result; it must not invent a repository command or treat a non-equivalent command as a substitute.
- #604 changes a shipped proof surface: a first bounded review is mandatory, and a second review reads repairs only if the first found a repair.
- #581 is a shipped consumer example; validate the complete example against the real adapter operation grammar rather than only deleting the known bad token.
- #594 and #593 change closeout verdict/guidance behavior at an irreversible issue-close boundary. Their acceptance requires distinct fresh-eye review and a behavior/evidence channel separate from a validator's own pass.
- Local proof remains local. GitHub issue state, publication, and hosted CI are separate evidence channels.

## User Acceptance

- A consumer with an explicit quality adapter and no generic runner receives an executable, adapter-supported packet or a precise typed unavailable result.
- Canonical-gate recognition covers the form Charness scaffolds only if the recorded policy decision selects that expansion, and its tests prove the default tuple.
- A copied issue adapter example resolves every declared operation without an unknown-placeholder refusal.
- The consolidated closeout draft describes only allowed carriers/keywords and the HOTL floor ignores quoted or non-target issue entries.

## Agent Verification Plan

### Low-Cost Checks

- Re-read each selected GitHub issue including comments before its design; inspect the exact adapter, validator, and generated/mirrored surfaces it names.
- Run focused unit, fixture, schema, and projection checks after each slice; use `git diff` and source-to-plugin mirror checks where applicable.

### High-Confidence Checks

- Use `quality` to select slow gates before #603/#604 and the closeout-floor slices.
- Run a bounded fresh-eye critique per completed slice. For #604, #594, and #593, use the proof-surface two-round rule when the first review drives a repair.
- Freeze the semantic commits, run the documented final quality lock, and bind the final critique/disposition evidence to that frozen state.

### External Or Live Proof

- No remote or consumer execution is presumed. If the user later grants publication, perform distinct GitHub/hosted readback before claiming the five issues resolved.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #603: resolve adapter-owned quality packets or report typed unavailability. | Restores an operator's ability to begin quality work. | Adapter-present/runner-absent regression fixture, planner result, focused tests, and critique. | completed 2026-08-12 (`470aae9a`) |
| 2 | #604: decide then repair the scaffolded `./scripts/run-quality.sh` canonical-gate gap. | It can produce a clean parity verdict over an unanchored job. | Recorded policy choice, default-pattern tests, release-note obligation, and proof-surface review. | pending decision |
| 3 | #581: repair and validate the shipped issue adapter example. | It is a direct copy/paste consumer failure with a bounded repair. | Every example operation resolves against real placeholder allowlists; source/plugin projection proof. | pending |
| 4 | #594: make the consolidated closeout draft shape reflect its live enforced rules. | Authors otherwise draft a carrier the tool refuses. | Consolidated draft-shape tests and fresh-eye verdict-surface review. | pending |
| 5 | #593: bind HOTL disposition parsing to the issue numbers being closed. | Quoted unrelated discussion must not block a close. | Target/non-target and quote-form tests plus fresh-eye verdict-surface review. | pending |

## Backlog Recount

- Counted: the GitHub open-issue inventory contains 29 issues as of 2026-08-12; this goal intentionally scopes five selected open items.
- Claims: #603, #604, #581, #594, and #593 remain OPEN in GitHub and each has a concrete implementation residue.
- Not claimed: tracker state does not establish consumer behavior, completion, publication, or the closability of any other open issue.

## Operator Decision Queue

- Decision: whether #604 widens the default canonical-gate patterns to newly judge scaffolded consumer jobs, or preserves the documented override-only posture.
- Owner: operator.
- Why deferred: slice 1 is independently actionable; #604's effect is a shipped enforcement-floor change.
- Unblock action: choose the default-recognition policy after its pre-mutation resolution brief identifies affected consumers and release-note wording.
- Revisit trigger: before editing #604's default patterns or tests that assert their consumer scope.

## Coordination Cues

- Phases: issue, quality, impl, critique, prove, retro.
- Routing: `issue` owns GitHub source-of-truth reads and eventual closeout; `quality` owns verdict-surface and gate cadence; `impl` owns bounded code/config slices; `critique` owns fresh-eye review; `prove` owns slice/final lock; `retro` owns closeout learning.
- Gather: n/a — GitHub issue data is read through the selected issue backend; no separate public source is being adopted as working context.
- Release: deferred — no release phase is authorized by this activation.
- Issue closeout: deferred — #603/#604/#581/#594/#593 remain open until their own carrier and distinct behavior evidence exist.

## Discuss Before Activation

- Discuss before activation: resolved — the user explicitly selected and activated this five-issue scope. This activation authorizes local shaping and implementation in the stated order, but does not choose #604's consumer-enforcement policy, publish, release, hosted proof, or closure of the five issues; the #604 decision is deliberately queued before its mutation.

## Slice Log

- Activated 2026-08-12 with no implementation slices yet completed.

### Slice 1: #603 adapter-owned quality packet routing

- Objective: Stop advertising a missing generic runner to a valid adapter-owned consumer repository.
- Why this approach: A planner packet must be executable from declared consumer evidence, not a Charness-local assumption.
- Commits: 470aae9a Repair adapter-owned quality packet routing
- What changed: Added native catalog-gate applicability filtering, a typed catalog_gate_unavailable lifecycle gap, adapter-present/runner-absent and clean-interpreter loader regressions, plugin projection sync, and debug/quality/critique records.
- Alternatives rejected: Did not infer a read-only substitute from arbitrary adapter commands; non-native catalog run_when prose remains advisory.
- Targeted verification: 87 focused tests passed; packaging and all pre-commit checks passed; plugin planner ran; fresh-eye rounds 1 and 3 approved, while round 2's import finding was repaired and re-reviewed.
- Test duplication pressure: One behavior-level fixture covers the consumer-visible missing-runner route; existing unconfigured coverage preserves the default catalog packet.
- Critique: full charness-artifacts/critique/2026-08-12-issue-603-quality-packet-critique.md; final reviewer approved and boundary fingerprints were clean.
- Off-goal findings: No adapter command execution, consumer runtime or hosted proof, publication, or GitHub issue closure; #604 policy choice remains queued.
- Lessons carried forward: A direct module loader needs an import-isolated test; planner tests can accidentally preload dependencies.
- Metrics: Focused suite: 87 passed in 5.29s; pre-commit completed with one non-blocking RCA-ledger advisory.

## Context Sources

1. [Design north star](../../docs/design-north-star.md) — #604, #594, and #593 are proof/closeout surfaces, so a wrong pass or refusal at their public boundary needs distinct review rather than a terminal gate claim.
2. [Handoff](../../docs/handoff.md) — no prior active goal governs; completed operator-rulings work and its non-claims stay outside this goal.
3. [Recent lessons](../retro/recent-lessons.md) — derive rather than hand-edit operational facts, and name other readers before interpreting a green result.
4. GitHub issue records #603, #604, #581, #594, and #593 — source-of-truth JTBD, comments, and lifecycle state through the selected `issue` backend.

## Interview Decisions

- One goal versus five unconnected fixes: one ordered goal, because the user explicitly grouped the reviewed top five and their shared boundary is quality/closeout truthfulness; each remains its own slice to avoid conflating acceptance conditions.
- #603 first versus starting with the strongest proof-surface issue: #603 first, because it restores the ability to execute the planning path and has a direct observed consumer failure; #604 remains immediately next because it is a masking proof-surface gap.
- Decide #604 now versus at its slice: defer only its enforcement-floor choice, because this activation is a scope decision rather than evidence that newly judged consumer jobs are acceptable.
- Close the five issues from local implementation alone versus keep lifecycle separate: keep closure separate; their GitHub state and eventual consumer/host behavior need their own evidence and authorization.

## Plan Critique Findings

- Pending before slice 1: fresh-eye review will check that #603 does not substitute an undeclared command and that its fixture proves advertised-command reachability rather than only planner internals.
- Preserved concern: #604's broadening can expose previously unanchored consumer CI jobs; this is a policy/release decision, not an implementation detail to smuggle through a regex change.

## Closeout Binding Plan

- Reviewed inputs: this goal, the five GitHub records, per-slice implementation/quality/critique evidence, and the final quality record; reviewer packets and retro records are terminal evidence, not semantic inputs.
- Frozen target: commit all semantic slices, capture the exact SHA, and regenerate any packet after a semantic edit.
- Fresh-eye: bounded reviewers independently inspect each slice; for proof surfaces the reviewer reads the repaired whole surface, and final behavior claims use tests or observable artifacts distinct from GitHub state.
- Verification lock: run the repository's documented final local quality lock on the frozen SHA and retain its receipt; later publish/hosted proof stays a separate phase.
- Complete flip: only after final packet, fresh-eye/disposition evidence, verification lock, retro, and external non-claims are recorded.

## Off-Goal Findings

- #585, #596, and #598 are being handled as separate already-shipped issue closeouts in the activating session; they are not evidence that this goal's five slices are complete.

## Final Verification

Retro: pending until the five-slice goal reaches closeout.
Host log probe: unavailable until a goal-window record can be honestly captured.
Disposition review: pending until final semantic inputs are frozen.

## User Verification Instructions

- Follow each slice's issue link and its bound tests/critique evidence. At completion, verify the final local lock against the frozen SHA; treat any later GitHub, release, CI, or consumer readback as separately reported evidence.

## Auto-Retro

Retro dispositions: pending until closeout; no improvement is claimed before the run has produced evidence.
Structural follow-up: pending until the retro determines whether any transferable pattern survives the five slices.
