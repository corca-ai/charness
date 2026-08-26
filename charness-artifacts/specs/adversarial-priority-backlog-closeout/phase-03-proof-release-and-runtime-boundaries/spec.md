# Phase 3: Resolve proof, release, and runtime boundaries

Status: planned
Goal: [adversarial-priority-backlog-closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## Objective

Repair or retire the live verdict, release-binding, mutation-ownership, cadence, and process-lifecycle issues without turning advisory gaps into new global gates.

## Scope In

- #701, #700, #699, #698, #697, #695, #694, #693, #669, and #668
- the exact producer-to-final-consumer paths that can emit a false verdict or orphan work
- second-round review only when an implementation actually changes verdict logic

## Scope Out

- release publication or push without a fresh explicit grant
- same-agent review represented as fresh-eye evidence
- raising budgets or adding prose when the owning runtime path remains wrong

## Dependencies

- Phase 1 premise and owner map
- Issue-specific debug hypothesis before bug-class implementation
- Disjoint writer ownership for shared release and proof surfaces

## Completion Criteria

- Each issue either closes with a targeted behavior verdict or remains a named blocker that prevents goal completion
- Shared verdict logic has bounded review at the real irreversible boundary, not during bulk classification
- Runtime and release evidence state exactly what was observed and do not infer publication or adoption

## Verification

- Focused adversarial tests cover the original failure arm and a control arm
- Changed proof surfaces run their owning gate and required bounded review
- Issue closeout readback is distinct from behavior evidence

## Non-Claims

- A CLOSED tracker state is not behavior proof
- A local release planner result is not a published-release claim
- A timeout increase alone does not resolve an unowned process or reporting defect

## Failure Handling

If verification fails, use `debug` and a 5-whys root-cause pass. Record the structural pattern and repair before retrying; a retry alone is not completion.
