# Issue #603 Quality Packet Debug
Date: 2026-08-12

## Problem

The quality planner advertises `./scripts/run-quality.sh --read-only` to a
consumer repository that has an explicit quality adapter but no such runner,
producing exit 127 before any real repository quality command runs.

## Correct Behavior

Given an explicit quality adapter and no generic runner, when the planner builds
a quality packet, then it emits adapter-declared commands with their declared
semantics or a typed unavailable/not-configured result; it never advertises a
nonexistent generic executable.

## Observed Facts

- GitHub #603 records the consumer reproduction and the exact exit-127 symptom;
  its comments list is empty.
- The selected web search added no diagnosis-specific evidence; it only confirms
  that a shell missing-path error is insufficient to distinguish a missing file
  from a planner-origin mistake.
- `build_plan` passed every catalog gate through unchanged and appended adapter
  packets afterward; no condition interpreted `read-only-quality`'s
  repo-native `run_when`.
- The focused adapter-present/runner-absent fixture reproduced the advertised
  generic packet before repair; its adapter commands were merely additional packets.

## Reproduction

- A temporary consumer fixture with `npm run check` and `npm audit --omit=dev`
  but no `scripts/run-quality.sh` advertised the generic runner before repair.
- After repair, the same fixture omits `read-only-quality`, exposes both
  adapter packets, and records `catalog_gate_unavailable` with the missing path.

## Candidate Causes

- The quality catalog unconditionally emits the generic runner packet.
- Adapter loading occurs after packet construction and cannot replace defaults.
- The planner detects an adapter but lacks a mapping from adapter gate commands
  to the packet's read-only intent.

## Hypothesis

- Confirmed: the catalog default was selected without an existence/adapter
  applicability check; disconfirmer: source construction and the minimal
  adapter-present/runner-absent fixture both showed the pre-repair packet.

## Verification

- `python3 -m pytest tests/quality_gates/test_quality_run_planner.py
  tests/quality_gates/test_quality_declaration_path_resolution.py -q` — 54 passed.
- The regression fixture asserts the adapter packets, absence of the generic
  runner, and the typed unavailable lifecycle gap.

## Root Cause

`build_plan` unconditionally retained catalog gates, while declaration lifecycle
only added adapter packets.  A valid adapter therefore could not prevent the
planner from advertising a missing repo-native executable.

## Invariant Proof

- Invariant: the command presented to an operator has evidence from the target
  repository's adapter or filesystem that it is executable for that target.
- Producer Proof: lifecycle now filters only repo-native catalog commands in a valid adapter-owned route and reports each omission structurally.
- Final-Consumer Proof: the isolated fixture receives declared adapter commands and no missing generic path.
- Interface-Shape Sibling Scan: `runtime-summary` and other non-native catalog packets remain unchanged; the plugin projection was regenerated from source.
- Non-Claims: no adapter command execution, consumer runtime roundtrip, or hosted proof has run.

## Detection Gap

- Planner fixture coverage | no adapter-present/runner-absent packet assertion
  existed | added a fixture that observes adapter command routing and typed generic-gate absence.

## Sibling Search

- Mental model: a generic Charness catalog command is assumed executable in a
  consuming repository even after the repository declares its own quality owner.
- same layer: catalog gates with non-native `run_when` prose | decision: unchanged because #603 proves only explicit local executable paths | proof: focused tests retain unconfigured catalog behavior.
- cross-file: `plugins/charness/skills/quality/scripts` projection | decision: regenerated | proof: packaging sync reported both changed quality scripts.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: adapter-to-planner command projection
- Disproving Observation: an adapter-aware packet already replaces the generic
  runner for the target fixture.
- What Local Reasoning Cannot Prove: behavior in uninspected consumer adapters.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: the fix changes a shipped planner/public quality path.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Keep the behavior-level adapter-present/runner-absent fixture: it proves the
operator-visible packet selection, not just an internal condition.
