# Achieve Goal: Execute operator rulings 2, 3, 5, and 6

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md`

## Active Operating Frame

- Current slice: rulings 2, 3, and 5 completed locally; ruling 6 is next.
- Current slice intent: re-key boundary-bypass identity on normalized call-site content without losing membership or multiplicity.
- Next action: shape and implement ruling 6 / `#585`, then prove its path-invariant and multiplicity-sensitive semantics.
- Verification cadence: focused deterministic checks at commit boundaries; fresh-eye critique and stronger slice proof at each irreversible proof-surface or exported-contract boundary; final bundle proof only after all four slices.
- Gate cadence: obtain `quality` recommendations before slow-gate or verdict-surface work; do not run Cautilus without a later explicit approval.
- Slice review packet: state the ruling, changed and generated surfaces, preserved boundaries, proof, non-claims, and reviewer questions before each fresh-eye review.
- History boundary: this frame stays current; completed evidence belongs in `## Slice Log` and owning artifacts.

## Goal

Execute rulings 2, 3, 5, and 6 from [Six operator rulings](../spec/2026-08-11-six-operator-rulings.md), in that order. Each slice must establish its own implementation contract, preserve the ruling's rejected alternatives, and update that ruling's per-section execution status only after its evidence exists. Ruling 5 is executed only because its scenario received the later approved evaluation run; scenario construction alone was preparatory evidence, not completion.

## Non-Goals

- Ruling 1, ruling 4's future release-note obligation, score-policy work, and unrelated open issues.
- A release, version bump, push, remote CI claim, issue close, or Cautilus run without the separately required approval.
- Extending `regenerable-facts` to decision documents; adding a timing-layer pre-push label; manufacturing score or Cautilus evidence; or deduplicating ruling 6 member hashes with `set()`.

## Boundaries

- Ruling 2 makes D47's measurement immutable through dated/hash-bound evidence and source invariants, not a heuristic content detector.
- Ruling 3 adds the existing timing-layer check to CI only; commit-time coverage remains the local owner and the fast pre-push lane remains unchanged.
- Ruling 5 may create a runnable scenario and update its stated waivers, but it may call Cautilus only after the planner and an explicit user grant for that run.
- Ruling 6 is a proof-surface schema change: normalized call-site content must be path-invariant and preserve content, membership, and multiplicity. It always receives round 1; round 2 reads the repaired surface only when round 1 produces repairs, and a no-repair round 1 records its discharge.
- No slice turns local evidence into hosted or consumer behavior claims.

## User Acceptance

- The ruling source records an evidence-backed execution status for 2, 3, and 6, and for 5 only after its approved evaluation; without that approval, the goal remains active with an explicit scenario-ready/evaluation-pending state.
- D47 no longer depends on a corpus-sensitive measurement pin; CI reaches the timing-layer check; the judge-intent scenario is runnable and either has approved evaluation evidence or remains explicitly pending; and boundary-bypass identity is content-based without losing multiplicity.
- The final record distinguishes local proof from any unapproved hosted, release, or consumer proof.

## Agent Verification Plan

### Low-Cost Checks

- Inspect each ruling's owning sources and run targeted unit/contract checks after its edits.
- Run generated-surface/mirror checks whenever a public skill or payload schema has a projection.

### High-Confidence Checks

- Route slow gates and changed verdict logic through `quality` before implementation.
- Run `critique` for every substantial slice; for a changed proof verdict, run round 1 and run round 2 only when round 1 repairs the surface.
- After slice 2, run the distinct goal-claims midpoint review before slice 3; preserve reviewer-boundary fingerprint receipts around every bounded reviewer.
- Run the final documented bundle quality proof and bind closeout claims to its fixed target.

### External Or Live Proof

- Cautilus for ruling 5 is approval-required and planner-mediated; scenario creation alone is not a successful evaluation.
- Push, remote CI readback, release, consumer observation, and issue closure are out of scope unless separately authorized.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Execute ruling 2 / `#596`: stamp D47 and replace equality pins with invariants. | Removes a stale-measurement failure without widening a weak detector. | Dated SHA-256 snapshot, focused provenance/headline/invariant proof, and two bounded review rounds. | completed 2026-08-12 |
| 2 | Execute ruling 3: add `check-timing-layer-completeness` to Quality Core CI. | Commit hooks do not cover web edits or unhooked contributors. | Exact CI command, static workflow proof, existing commit trigger, unchanged docs-only labels, and two bounded review rounds. | completed 2026-08-12 |
| 3 | Execute ruling 5: add the route-undetermined judge-intent scenario and run its one approved Cautilus evaluation. | The planner's least-certain branch lacks a scenario. | Registered scenario, waiver dispositions, deterministic checks, and approved Cautilus evidence. | completed 2026-08-12 |
| 4 | Execute ruling 6 / `#585`: re-key boundary-bypass identity on normalized call-site content. | Its path-pair key is the largest remaining schema defect and the ruling fixes its known descendant class. | Schema/baseline reader coverage: identical content moved by path preserves identity; changed content or membership changes identity; duplicate member hashes remain multiplicity-sensitive; and algorithm version is stamped and validated. | pending |

## Backlog Recount

- Activation count: four ordered ruling items were not executed in the dated ruling record when this goal began; `#596` and `#585` are tracked identifiers within that fixed scope. One remains unexecuted: ruling 6.
- Claims: this goal plans local execution and proof only; it does not claim the live issue backlog, a release, or hosted success.
- Not claimed: issue closure, Cautilus evaluation result, and every ruling outside 2, 3, 5, and 6.

## Operator Decision Queue

- Decision: completed — the operator approved one evaluation and its durable
  `operator-log` records that authorization.
- Owner: operator (decision), parent workflow (execution).
- Evidence: [Cautilus proof](../cautilus/latest.md) and its named durable bundle.

## Coordination Cues

- Phases: spec, impl, quality, critique.
- Routing: installed workflow metadata and the ruling-specific boundary choose the owner skill at each slice; `achieve` remains the goal record, not the implementation path.
- Gather: n/a — the goal starts from checked-in local ruling and probe records.
- Release: n/a — no release surface is in scope.
- Issue closeout: n/a — `#596` and `#585` are context identifiers; this goal has no authorized close carrier.

## Discuss Before Activation

- Discuss before activation: resolved — the user authorized activation and local execution of all four slices in order. Push, release, issue close, hosted readback, and Cautilus evaluation remain separately approved boundaries; slice 3 pauses to request the evaluation grant rather than treating scenario creation as proof, and the goal remains active if that grant is withheld.

## Slice Log

- Shaping: the user selected the four not-executed operator rulings as one ordered goal.
- Slice 1 / ruling 2 (`#596`): replaced D47's mutable live-corpus equality pin with `2026-08-12-inventory-marker-rule-snapshot.json`, bound it by SHA-256, retained four dated headlines, and changed focused proof to provenance/document/invariant checks. `pytest -q tests/test_inventory_marker_rule_measurement.py tests/test_probe_drift_message.py` passed (39); `check_regenerable_facts.py` passed. The document preflight remains blocked only by pre-existing inline-code findings at D47-unrelated lines 1078 and 1082. Two bounded review rounds found and repaired stale live wording, headline-to-payload binding, provenance checks, and new-snapshot instructions; round-2 repairs are accepted-unreviewed under the two-round cap. The initial full gate exposed an accidentally omitted historical handoff publish-state claim; restoring its exact captured block made its 27 focused ledger tests pass, and the rerun of `./scripts/run-quality.sh --read-only` passed 90 checks (0 failed). Critique: [r596 D47 snapshot](../critique/2026-08-12-r596-d47-snapshot-critique.md). Non-claims: no live corpus proof, CI, push, release, consumer, or issue-closeout claim.
- Slice 2 / ruling 3: added `python3 scripts/check_timing_layer_completeness.py --repo-root .` as a Quality Core step. Focused timing, staged-commit, and CI/local-parity tests passed (99); `check_github_actions.py` and the timing checker passed. Round 1 repaired a substring-only test into an actual YAML-step and exact 14-label docs-only-list proof; round 2 found no further issue. Critique: [r3 timing-layer CI](../critique/2026-08-12-r3-timing-layer-ci-critique.md). Non-claims: static local CI configuration proof only; no push or hosted CI readback.
- Midpoint claims review: a bounded read-only reviewer compared the completed ruling-2 and ruling-3 claims against their owning records and commits. It found two stale progress statements in this goal (the activation-time `not-executed` count and the final-verification statement); both were repaired. At the time, ruling 5 correctly remained evaluation-pending; its later approved evaluation is recorded in slice 3. Critique: [operator-rulings midpoint claims](../critique/2026-08-12-operator-rulings-midpoint-claims-critique.md). Non-claim: this review is not final bundle proof.
- Slice 3 / ruling 5: registered `handoff/judge-intent`, whose prompt explicitly leaves the route undecided and requires `plan_handoff_run.py --intent auto` before any route declaration. Its two engage-always references, `workflow-trigger.md` and `state-selection.md`, now use `requiredOpenedReferences`, so only a `Read` or parsed shell read (not a basename mention, `Edit`, or `Write`) satisfies the verdict. The two matching historical waiver lines remain as stale advisories; the unhealthy-adapter `adapter-contract.md` waiver remains live. Focused pytest passed (36); Node observation tests passed (34); claim-fidelity registry and conditional-read validators passed. Two review rounds repaired auto-route enforcement, name-drop matching, and edit/write bypasses; the final round-2 repair is accepted-unreviewed under the cap. Critique: [r5 judge-intent scenario](../critique/2026-08-12-r5-judge-intent-scenario-critique.md). With the operator's explicit one-run approval and `operator-log`, an isolated capture then `cautilus evaluate observation` passed 1/1 with 0 failed; [the durable Cautilus bundle](../cautilus/handoff-judge-intent-2026-08-12/) preserves the authorization, packet, summary, and trace. Non-claim: local evaluator evidence only; no hosted, release, or consumer proof.

## Context Sources

1. [Design north star](../../docs/design-north-star.md) — limits teeth to observable form and irreversible escapes; CI and boundary-bypass verdict work need distinct review rather than terminal green.
2. [Six operator rulings](../spec/2026-08-11-six-operator-rulings.md) — authoritative outcomes, rejected alternatives, and current execution statuses.
3. [Harness-improvement thesis](../spec/2026-08-11-harness-improvement-thesis.md) — records the completed memory-improvement work that is explicitly outside this goal.
4. [Cautilus on demand](../../skills/public/quality/references/cautilus-on-demand.md) — planner-first, ask-before-run evaluation boundary for ruling 5.
5. [Remote CI reconciliation contract](../spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md) — preserve the existing local/hosted proof distinction while changing CI or quality surfaces.

## Interview Decisions

- One ordered goal versus four unrelated changes: chosen one goal with four independent slices, because the ruling record explicitly groups them and the user requested all four; rejected a monolithic implementation because each has a different owner and proof boundary.
- Implement now versus make another decision document: chosen activation for local implementation, because the operator rulings already fix the relevant policy; rejected re-triage because it would reopen decided alternatives.
- Cautilus evaluation now versus later approval: chosen a later explicit grant after scenario construction, because repository policy makes evaluation ask-before-run; rejected an implicit grant from goal activation.
- Push or release after local proof: chosen no publication action, because the prior grant does not carry forward; rejected treating a green local gate as a push grant.

## Plan Critique Findings

- [Activation critique](../critique/2026-08-12-operator-rulings-goal-activation-critique.md) received two independent angle reviews and a counterweight pass; all three reviewer windows verified clean before parent edits.
- Folded before activation: no unapproved Cautilus run may advance ruling 5 to executed; round 2 is conditional on a round-1 repair; slice 4 covers path, content, membership, multiplicity, and algorithm-version semantics; slices 1 and 2 name their exact proof obligations; and the goal-claims midpoint review follows slice 2.
- [Midpoint claims critique](../critique/2026-08-12-operator-rulings-midpoint-claims-critique.md) found and repaired two stale progress statements; it confirmed the remaining completed-slice claims and preserved the ruling-5 approval boundary.
- [R5 judge-intent critique](../critique/2026-08-12-r5-judge-intent-scenario-critique.md) required two review rounds for the changed observation verdict; the round-2 edit/write bypass repair is accepted-unreviewed under the mandatory cap.
- Over-worry rejected: predeclaring every implementation owner and adding a pre-push timing label would reopen or broaden decisions already fixed by the ruling record.

## Closeout Binding Plan

- Reviewed inputs: this goal, the ruling source, per-slice contracts/critique records, and the final quality record; no reviewer packet or retro is treated as a semantic input.
- Frozen target: freeze the four completed semantic slices at a committed SHA before composing the final packet; later semantic edits require a new packet and lock.
- Fresh-eye: a bounded distinct reviewer reads final claims against ruling evidence and the fixed tree; proof-surface slices separately use the required code-review rounds.
- Verification lock: run the documented final quality/closeout lock for the frozen target and retain its durable record.
- Complete flip: only after each ruling status, review/lock evidence, remaining external non-claims, retro dispositions, and successor decision are recorded.

## Off-Goal Findings

- None at shaping time.

## Final Verification

- Not started — slices 1 and 2 have completed locally, but final bundle proof has not started.

## User Verification Instructions

- Follow the ruling source's four execution-status lines and the linked per-slice proof records. Before approving Cautilus, inspect the scenario and its planner output; before any publication, grant that boundary separately.

## Auto-Retro

- Deferred until closeout — per-slice findings are captured in their critique records; cross-slice efficiency and structural dispositions wait for the final bundle.
