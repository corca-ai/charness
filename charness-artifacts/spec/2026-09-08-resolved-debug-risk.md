# Spec: resolved debug risk lifecycle
Date: 2026-09-08

## Problem

The debug planner overlays raw forced-risk declarations after recognizing `Resolution: resolved`, so a new subject can be blocked by a closed incident even when its canonical handoff permits implementation.

## Capability Contract

The planner must distinguish active risk from valid historical closure. A resolved forced-risk incident becomes prior memory only when the existing canonical debug parser and spec handoff parser establish matching interrupt identity and seam, `Chosen Next Step: impl`, and `Impl Status: allowed`. All other risk or lifecycle ambiguity remains active.

## Current Slice

Repair the existing artifact-state/planner composition and add representative in-process planner tests. Preserve raw declaration classes, diagnostics, generalization pressure, write-target/refusal metadata, and deliberate continuation commands.

## Fixed Decisions

- Compose effective routing once in `skills/public/debug/scripts/debug_artifact_state.py`; mode, next action, and required reads consume it.
- Reuse `parse_debug_interrupt` and `parse_spec_interrupt_resolution`, including validation and exact seam equality. Do not import current-slice freshness/applicability into historical closure.
- A valid allowed handoff need not prove eventual implementation completion. Missing, invalid, mismatched, blocked, or outstanding handoffs keep forced risk active.
- Open, missing, or unknown/unreadable Resolution keeps existing behavior. A resolved flag alone cannot clear unknown-only, forced-plus-unknown, or fence-hidden declarations.
- Active interrupt/repair routes read the blocking current artifact first, while ordinary fresh routes retain scaffold and prior-memory reads. No new CLI flag, public schema version, generic guard, taxonomy, or risk-verdict change.

## Probe Questions

- Do resolved forced+valid-handoff, open/missing/unknown lifecycle, invalid/mismatched/blocked handoff, factor-now, unknown-only/mixed-invalid/fence-hidden, and legacy/no-risk controls agree across mode, action, required reads, and raw diagnostics? Update implementation tests if a narrower boundary is discovered.
- Does the actual planner CLI reproduce the valid handoff as fresh prior-memory routing after the local change? This is local consumer proof, not final broad approval.

## Deferred Decisions

- Global history validation, parser/taxonomy redesign, new CLI controls, generated export synchronization, and broad-suite/release proof remain parent-owned or out of scope.
- Whether later repairs need a separate lifecycle abstraction remains deferred; this slice must not create one without a concrete duplicated decision.

## Non-Goals

No changes to `debug_artifact_declarations.py`, `risk_interrupt_lib.py`, public schema, planner flags, latest pointer, artifact index, generated mirror, installed host, or eventual implementation-complete verdict.

## Deliberately Not Doing

Do not fabricate changed paths to satisfy `plan_risk_interrupt`; its current-slice freshness contract is intentionally separate from historical closure. Do not weaken active-risk behavior to make only the reproduced success case pass.

## Constraints

Changes are bounded to the declared source/test paths plus these dated records. Use existing loaders and in-process `build_plan` fixtures. Keep the existing fresh write-target safeguards and refused-write metadata intact.

## Success Criteria

- A resolved forced-risk record with matching interrupt/seam and `impl/allowed` handoff routes a new subject to `fresh-investigation-with-prior-memory` and scaffolds a fresh write target.
- Open/missing/unknown lifecycle and every invalid/outstanding handoff remain active; factor-now, unknown-only, mixed-invalid, and fence-hidden declarations do not get silently demoted.
- Mode, next action, and required-read order agree; active blockers name the current artifact first, while raw classes, parse diagnostics, pressure facts, refusal metadata, and continuation command remain present.
- Legacy no-risk and ordinary resolved/no-forced-risk behavior remain unchanged.

## Acceptance Checks

- `unit`: extend `tests/test_debug_plan.py` with representative positive and negative lifecycle/risk intersections through `build_plan`.
- `integration`: run the standing pytest runner for `tests/test_debug_plan.py` and directly relevant subject/scaffold/risk tests selected by the implementation; run the actual planner CLI for the reproduced new-subject case.
- `specdown`: validate the debug handoff with the emitted scoped debug validator and validate this spec through the emitted canonical risk-interrupt owner command/readback.

## Boundary Ownership

`debug_artifact_state.py` owns effective artifact routing; `plan_debug_run.py` owns plan assembly; `debug_artifact_declarations.py` owns raw declaration parsing; `risk_interrupt_lib.py` owns canonical interrupt/handoff taxonomy and current-slice verdicts. Parent owns source/export synchronization, pointer/index updates, full authoring lane, final independent review, and final approval.

## Critique

- Interrupt Source: consumer-path-and-pytest
- Seam Summary: fixture instruction to executed consumer reads
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: parent permits the bounded implementation after two pre-implementation reviews; final implementation approval remains pending focused proof and parent integration review
- What Disproving Observation Is Resolved: the executed PLAN-1 reproduction shows a resolved forced-risk record with a matching canonical `impl/allowed` handoff still routes to `risk-interrupt`; the implementation probe must resolve that intersection without weakening active-risk controls

## Canonical Artifact

`charness-artifacts/probe/2026-09-08-resolved-debug-risk-reproduction.json` is the evidence-led source and receipt. This spec is the named handoff for the bounded lifecycle repair.

## First Implementation Slice

Add one state-owned effective routing decision, wire all three planner consumers to it, then add focused intersection controls before running the emitted artifact validators and standing tests.
