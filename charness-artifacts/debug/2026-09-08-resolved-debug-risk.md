# Debug Review: resolved debug risk lifecycle
Date: 2026-09-08

## Problem

For a new subject, the planner treats an explicitly resolved forced-risk incident as an active `risk-interrupt`, even when the named handoff is valid and implementation-allowed. This makes a closed incident block fresh work.

## Correct Behavior

Given an explicitly resolved, clearly parsed forced-risk incident, when its canonical handoff matches the interrupt and seam and chooses `impl` with `Impl Status: allowed`, the planner routes a new subject to fresh investigation with the incident as prior memory. Open, unreadable, invalid, mismatched, or blocked handoffs remain active and are read first.

## Observed Facts

- `charness-artifacts/probe/2026-09-08-resolved-debug-risk-reproduction.json` is the executed PLAN-1 source and receipt. It records the final CLI output as `mode: risk-interrupt`, `next_action: interrupt-to-spec`, `resolution: resolved`, and `requires_interrupt: true`; its canonical handoff check is `handoff-recorded` with `chosen_next_step: impl` and `impl_status: allowed`.
- Before this repair, `debug_artifact_state._artifact_summary` (lines 57-83) derived resolution and then copied `risk_summary`'s raw `requires_interrupt`; `plan_debug_run._next_action` (lines 256-308), `build_plan` (lines 333-363), and `_required_reads` (lines 67-151) independently prioritized that flag.
- The previous resolved-lifecycle repair handled ordinary resolved routing but missed this forced-risk intersection. The repeated symptom is the unresolved composition, not a new risk taxonomy.

## Reproduction

- PLAN-1: run `python3 skills/public/debug/scripts/plan_debug_run.py --repo-root . --subject coverage-yaml-output --evidence-led` against the retained resolved current incident. The source receipt records the observed risk interrupt and the separately accepted canonical handoff.

## Candidate Causes

- A bad forced-risk taxonomy or handoff verdict: disconfirmed by the canonical parser/plan recorded in the PLAN-1 receipt.
- Resolution parsing failing to recognize `resolved`: disconfirmed by the same receipt's planner observation.
- State composition allowing raw historical risk to override lifecycle and then being consumed in three places: reproduced by the pre-fix source and PLAN-1 final-consumer output.

## Hypothesis

- The failure will disappear if the existing artifact-state owner computes one effective routing result that demotes only a resolved forced risk with a valid matching `parse_debug_interrupt`/`parse_spec_interrupt_resolution` handoff; raw classes and diagnostics will remain unchanged. `disconfirmer:` run the focused lifecycle intersections, including invalid/open/unknown/fence-hidden controls, through `build_plan` and the planner CLI before declaring the repair effective.

## Verification

- PLAN-1 confirmed the hypothesis. Candidate `2506e3251` passes 42 focused planner tests and committed changed-line coverage across the original slice; earlier related controls passed 122 tests.
- The actual original planner CLI now routes to fresh prior memory. A malformed first raw declaration followed by a valid canonical section remains blocked/read-first. The initial candidate demoted that case; preserving raw diagnostics fixed it. Final integration evidence: `charness-artifacts/probe/2026-09-08-resolved-debug-risk-proof.json`.

## Root Cause

Four-whys chain:

- Why did a fresh subject receive `interrupt-to-spec`? `plan_debug_run` checked `artifact["requires_interrupt"]` before fresh/continuation routing.
- Why was that flag active? `_artifact_summary` retained the raw forced declaration after separately recognizing `Resolution: resolved`.
- Why did a valid handoff not close the historical risk? No state owner joined the lifecycle, canonical interrupt identity/seam, and allowed implementation handoff before exposing routing to consumers.
- Why was the gap shipped? Tests covered resolved lifecycle and forced risk independently, not their intersection; the structural gap is a missing single effective-routing invariant.

## Invariant Proof

- Invariant: when the artifact-state producer emits an effective historical-risk decision, `plan_debug_run` must make mode, next action, and required reads act on that same decision before routing can claim fresh work.
- Producer Proof: PLAN-1 binds the pre-fix artifact, source input hashes, and canonical handoff result; pre-fix source lines above show the conflicting raw/effective inputs.
- Final-Consumer Proof: the original CLI case now routes to fresh prior memory; the malformed raw-declaration control stays blocked. The proof record binds both results to repaired source hashes.
- Interface-Shape Sibling Scan: lifecycle, risk, and required-read consumers are the same state-to-plan boundary in `debug_artifact_state.py` and `plan_debug_run.py`; `risk_interrupt_lib.py` is the canonical parser boundary.
- Non-Claims: no installed-host, generated-mirror, provider, broad-suite, release, or eventual implementation-complete claim.

## Detection Gap

- `tests/test_debug_plan.py` resolved-pointer controls did not declare forced risk, while forced-risk controls did not declare explicit resolved lifecycle. The smallest prevention is one valid-hand-off intersection plus negative handoff/lifecycle controls asserting mode, action, and first read together; no change to the taxonomy library is justified.

## Sibling Search

- Mental model: treating a historical declaration as an active verdict after a lifecycle endpoint, then letting each consumer re-decide the combination.
- same layer: `skills/public/debug/scripts/plan_debug_run.py:256-363` | decision: same bug, fix now | proof: local payload proof.
- abstraction up: `scripts/gates_support/risk_interrupt_lib.py:253-360` has a related handoff decision but owns current-slice freshness, not historical closure | decision: same class, diagnostic-only for this slice | proof: static scan only; bounded no-action: the supplied contract explicitly keeps its freshness/verdict semantics unchanged.
- specialization down: `debug_artifact_declarations.py:95-136` preserves raw risk classes, parse diagnostics, pressure, and fence handling | decision: intentional plain-text declaration boundary | proof: local payload proof; no declaration parser change.
- mental-model sibling: subject-refusal and fresh-write routing in `scaffold_debug_artifact.py:314-401` | decision: same class, diagnostic-only for this slice | proof: static scan only; safeguards remain unchanged.
- cross-file: `skills/public/debug/scripts/plan_debug_run.py` and `scripts/gates_support/risk_interrupt_lib.py` | decision: same class, diagnostic-only for this slice | proof: static scan only; canonical parser is consumed without importing freshness.

## Seam Risk

- Interrupt ID: resolved-debug-risk
- Risk Class: repeated-symptom
- Seam: debug lifecycle to effective planner routing
- Disproving Observation: a valid matching handoff still left the fresh planner on `risk-interrupt`
- What Local Reasoning Cannot Prove: final post-fix planner behavior across lifecycle and handoff intersections
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-08-resolved-debug-risk.md

## Prevention

The artifact-state owner composes effective routing once and preserves raw diagnostics before canonical closure. `tests/test_debug_plan.py` covers valid closure, malformed and outstanding handoffs, raw/canonical disagreement, and blocking reads. The proof record owns final independent review and broad verification.

## Evidence Disposition

- Report Identity: probe:PLAN-1#sha256:a4a46a01b97a76e9740ccaa3d94fdd724516e7e9439623ad8ba1e9ba5e32c75f
- Reported Findings: 1
- Dispositioned Findings: PLAN-1
- Missing Findings: none
- Evidence Digest: sha256:cafedfff204ca36647c340f85b77408404911a543d1d7fa17a4bdb07f470c58f
- Report Source: charness-artifacts/probe/2026-09-08-resolved-debug-risk-reproduction.json
- Report Source SHA256: a4a46a01b97a76e9740ccaa3d94fdd724516e7e9439623ad8ba1e9ba5e32c75f

## Adversarial Verification

- Finding: PLAN-1 | source: charness-artifacts/probe/2026-09-08-resolved-debug-risk-reproduction.json | expected: resolved incident with a matching implementation-allowed handoff routes a new subject to fresh investigation | stimulus: invoke the actual debug planner for a new subject with the retained resolved current incident | disposition: reproduced | observed: planner reports resolved but still selects risk-interrupt and interrupt-to-spec; canonical handoff validation with declared incident and spec paths permits implementation | proof: executable fixture | handoff: charness-artifacts/spec/2026-09-08-resolved-debug-risk.md | next move: compose effective routing once and run focused lifecycle intersections | receipt: charness-artifacts/probe/2026-09-08-resolved-debug-risk-reproduction.json | receipt sha256: a4a46a01b97a76e9740ccaa3d94fdd724516e7e9439623ad8ba1e9ba5e32c75f
