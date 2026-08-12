# Preset Lineage Reconciliation Contract

## Problem

The declaration-lifecycle report treats every `preset_lineage` item as
`declared-only` and emits `preset_not_reconciled` unconditionally. Its existing
detector observes only repository technology signals, not whether a preset's
suggested command families are adopted, so changing the state on detection alone
would create a false clean result.

## Capability Contract

A preset lineage entry can reach a clean reconciliation state only when a
machine-readable, versioned prescription declares which observable adapter or
repository signals count as adoption, and the lifecycle report evaluates those
signals. A preset with no executable prescription remains metadata and reports a
typed advisory rather than an impossible action-required gap.

## Current Slice

Specify the prescription vocabulary and lifecycle states before changing preset
front matter, adapter schema, or the declaration-lifecycle verdict.

## Fixed Decisions

- Human prose under `Suggested Gate Vocabulary` is not an executable
  prescription and must never produce a clean state by substring matching.
- Each prescribed requirement names one stable observable: adapter key/value,
  declared command family, or repository file/tool signal; evaluation returns
  satisfied, missing, or unavailable with evidence.
- A preset that deliberately stays sample-vocabulary-only has
  `reconciliation_state: metadata-only`, no `preset_not_reconciled` gap, and a
  clear advisory explaining that it is not a claimed applied policy.
- A prescription-bearing preset has `reconciliation_state: reconciled` only
  when every required observable is satisfied; otherwise it emits one gap per
  missing or unavailable observable with a concrete adapter-facing remedy.
- `repo_signal_detected` remains provenance-only and cannot substitute for a
  prescription observation.

## Probe Questions

- Which current preset defaults are stable enough to become required observable
  prescriptions rather than optional guidance?
- Does a lineage item need a preset version pin before a changed prescription can
  be evaluated safely?
- Can `skill_ergonomics_gate_rules` and dangling coverage-policy paths share the
  same observable vocabulary, or do they require separately-owned follow-ups?

## Deferred Decisions

- Consumer migration and any automatic adapter rewrite are deferred.
- The contents of a prescription for each existing language preset are deferred
  until a representative fixture proves the vocabulary is sufficient.

## Non-Goals

- Do not promote sample recommendations into hard quality gates.
- Do not infer command adoption from Markdown prose or technology detection.
- Do not close #589 until a declared preset reaches a tested clean state and a
  missing prescription reaches a distinct tested non-clean state.

## Constraints

- Preserve source and shipped-plugin parity.
- Keep adapter compatibility: absent prescription data must have an explicit
  `metadata-only` result, not a malformed-config crash.
- Separate report state from gate exit policy; the lifecycle report is an
  operator-facing declaration reader, not permission to make every advisory red.

## Success Criteria

- A fixture with a prescription-bearing lineage and all observables satisfied
  produces `reconciled` and no preset gap.
- A fixture missing one required observable produces a named missing gap and
  `action-required`.
- A sample-only or unknown legacy preset produces `metadata-only` with a typed
  advisory, never a permanent `preset_not_reconciled` gap.
- Technology detection alone cannot make a prescribed preset reconciled.

## Acceptance Checks

- unit: lifecycle-state evaluator covers satisfied, missing, unavailable, and
  absent-prescription cases.
- integration: quality run plan renders the new state and matching gap/remedy
  for a fixture adapter.
- e2e: source and shipped quality planner report identical reconciliation output.

## Boundary Ownership

- Producer: preset front matter and adapter/repository observable readers.
- Consumer: `quality_declaration_lifecycle.py` and the quality run-plan report.
- Owning surface: preset schema plus quality declaration lifecycle.
- Verdict: escalated-to-issue-spec.

## Critique

- Interrupt Source: #589.
- Seam Summary: current technology detection is adjacent to but semantically
  different from prescribed-gate adoption.
- Chosen Next Step: spec.
- Impl Status: not-started.
- Impl Status Reason: no machine-readable prescription vocabulary exists.
- What Disproving Observation Is Resolved: a detected TypeScript/Python signal
  alone cannot prove a preset's suggested gates were applied.

## Canonical Artifact

This file.

## First Implementation Slice

Introduce a minimal typed prescription in one fixture-only preset path and an
evaluator that returns `reconciled`, `missing`, or `metadata-only`; prove the
three states before migrating shipped presets.
