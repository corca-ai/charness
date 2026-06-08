# Critique Review
Date: 2026-06-08

## Decision Under Review

Slice 4 of the #335 goal (commit `7ff8aa62`): extend the author-time artifact-shape
preflight to the goal-closeout / coordination-floor surfaces (the one authoring
surface the v0.28.0 generalization did not cover — discovered by failing the
complete flip ~4×). Additive surfacing, not a new hard gate; the achieve flip
floors keep enforcement.

## Failure Angles

- Shape re-declaration drift: a stub/registry copy of the early-close sections
  that can silently diverge from the floor validator (`_REPORT_SECTIONS`).
- Verdict change: a new registry entry or the early-close module's new CLI
  changing an existing validator's verdict on existing artifacts.
- Sweep leakage: a new surface accidentally entering the fail-fast commit-boundary
  structural sweep and blocking on pre-existing goal files.
- Coupling smell: turning a floor-validator LIB into a CLI-scaffold.
- Scope gap: the Activation-time format shape was named in the goal but not added.

## Counterweight Pass

- Drift is the central worry; it is BOUND, not just asserted: the round-trip
  (`report_stub()` → `validate_report_shape() == []`) and the cross-validator
  emit-stub dogfood pin the stub to the floor's own validator. The reviewer
  injected a drifted heading and confirmed the test fails — genuine
  single-source-with-binding.
- Verdict/sweep/coupling worries all falsified (see Structured Findings + Fresh-Eye
  Satisfaction). The Activation-time omission is a defensible scope line, recorded
  as a follow-up — it is enforced at activation-readiness (not the closeout-floor
  class this slice closes) and needs preamble extraction (different machinery than
  the `## Heading` template-section source), so it is a separate, honest follow-up,
  not laundered as done.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_early_close_report.py | action: defer | note: _CANONICAL_REPORT_SECTIONS vs _REPORT_SECTIONS can drift in principle, but the round-trip + cross-validator tests bind them (reviewer confirmed a drifted heading fails the test). No action.
- F2 | bin: over-worry | evidence: strong | ref: scripts/check_artifact_surface_preflight.py:254 | action: defer | note: both new surfaces are prefix=None/commit_boundary=False; changed_artifacts returns checked:[] for goal/early-close paths — author-time-only, no sweep leakage, no verdict change. Validation funcs byte-unchanged.
- F3 | bin: over-worry | evidence: moderate | ref: scripts/check_artifact_surface_preflight.py:108 | action: defer | follow-up: deferred goal-activation-preflight-surface | note: goal-activation surface (the Activation: line) is not added — a defensible scope line (enforced at activation-readiness, not the closeout floor; needs preamble extraction, not the `## Heading` template-section source). Recorded as a named follow-up in the premerge/preflight spec, not laundered as done.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer (different agent context), read-only, shared parent worktree, git-show inspection only.
- Requested spawn fields: Agent(subagent_type=general-purpose) with the Slice 4 review packet (intent + design constraints, changed surfaces, expected invariants, proof already run, non-claims/out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: bounded reviewer (agent af365cb08b8f0fe7e) ran via the Agent tool and returned VERDICT: SHIP with zero blockers; it verified every invariant by execution (drift-binding, changed_artifacts checked:[], byte-unchanged validators, stub bodies 81/62/63 chars vs the 20-char floor, mirrors byte-identical).

## Fresh-Eye Satisfaction

The reviewer returned SHIP and verified the invariants by EXECUTION, not reading:
it injected a drifted early-close heading and confirmed `validate_report_shape`
returns failures (so the drift-binding test really binds); it ran `changed_artifacts`
against goal/early-close paths and got `{status: ok, checked: []}` (author-time-only,
no sweep leakage); it confirmed the four floor-validation functions are byte-unchanged
and the lone consumer (`goal_artifact_closeout_evidence.py`) is untouched; and it
measured the stub section bodies (81/62/63 non-whitespace chars) against the 20-char
floor. The single nit (no goal-activation surface) is recorded as F3 follow-up.
