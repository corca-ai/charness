# Quality Review
Date: 2026-08-12
Title: Issue 603 quality packet routing

## Scope

Target boundary: adapter-owned quality planner packet selection for #603.

Ambient repo findings: broad gate health and consumer runtime execution are out of scope.

## Surface Contract Review

- semantic coverage: `observed` — the planner's adapter-to-packet projection is exercised.
- surface: structured quality-run plan sent to a consumer operator
- owner: a valid consumer quality adapter owns its declared commands
- projections: YAML detail plan, lifecycle gaps, and human packet rendering
- state scope: adapter present, generic runner absent, declared commands available as text
- transitions: catalog default selected, native path checked, packet omitted or adapter command routed
- proof boundary: isolated planner fixture and focused Python tests; no consumer command is executed
- unexamined axes: arbitrary adapter command availability and hosted consumer behavior

## Current Gates

- The catalog describes `read-only-quality` as a repo-native command, but the planner previously emitted it unconditionally.

## Runtime Signals

- runtime source: focused pytest receipt; timing capture is missing because this cheap planner path has no configured timing capture. <!-- reproduction-source -->
- runtime hot spots: none observed; this slice does not run a broad quality gate.
- coverage gate: focused planner and declaration-lifecycle regressions pass (54 tests).
- evaluator depth: deterministic-gates-only; Cautilus is not approved and would not establish consumer command reachability.

## Healthy

- Existing unconfigured-repository catalog behavior remains a non-goal of this narrow adapter-owned repair.

## Weak

- A valid adapter did not suppress a missing generic executable, so an operator could receive exit 127 before an adapter command.

## Missing

- No runtime execution claim is made for adapter-declared commands; declaration proves routing, not installation.

## Deferred

- Canonical-gate recognition policy is #604's queued operator decision, not part of #603.

## Advisory

- structural review result: the capability is an executable first packet; command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail` showed unconditional catalog composition.
- prose review result: `references/adapter-gate-review.md` classifies absent repo-native routing as a structural fact; only that path check becomes deterministic.

## Delegated Review

- Delegated Review: executed — fresh-eye review approved behavior, then caught and repaired a clean-interpreter import defect before final re-review; record: `charness-artifacts/critique/2026-08-12-issue-603-quality-packet-critique.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not applicable; the selected planner fixture is cheap and bounded.

## Commands Run

- Planner detail inspection and focused source/test reads identified the adapter-present/runner-absent regression shape. <!-- reproduction-source -->

## Recommended Next Quality Moves

- active adapter packet selection — capability_needed=an executable consumer starting point; next_center=planner lifecycle; transformation=omit missing repo-native defaults when a valid adapter owns routing and emit a typed gap; proof_boundary=isolated adapter fixture; enforcement_posture=existing-gate-reuse.
- passive adapter command execution — capability_needed=installed consumer dependencies; next_center=consumer repository; transformation=run a declared command only under consumer authority; proof_boundary=consumer receipt; enforcement_posture=no-gate because the planner cannot prove dependency installation.

## History

- [Quality adapter lifecycle review](./history/2026-08-05-issue-507-quality-adapter-lifecycle.md)
