# Critique Review — Release Argparse Help

Date: 2026-07-11

## Decision Under Review

Clear all eight missing-help findings in the single release planner without
changing parser behavior or weakening the distinction between planning and
irreversible publication.

## Failure Angles

- Boundary honesty: a read-only planner must not claim that it publishes,
  bumps, or authorizes a release.
- Contract drift: option names, defaults, choices, required state, mutual
  exclusion, plan schema, and runtime behavior must remain unchanged.
- Test fidelity: each option must be paired with its own wrapping-safe help
  block rather than passing from usage-line presence.

## Counterweight Pass

- The first wording overstated four options as direct publication actions or
  authorization; they now explicitly describe planned commands or plan inputs.
- Whole-output snapshots, a shared parser abstraction, and a new repo-wide
  blocking floor would add brittleness without strengthening this proof.
- The remaining findings stay in separately owned packages.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/plan_release_run.py | action: fix | note: describe critique and version selectors as planned inputs, not publication or authorization performed by this read-only command.
- F2 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/skills/release/scripts/plan_release_run.py | action: document | note: packaged mirror is byte-identical to the corrected public source.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_release_run_planner.py | action: document | note: each of eight options is paired with its own wrapping-tolerant description assertion.
- F4 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/2026-07-11-release-argparse-help.md | action: defer | note: the remaining 43 findings require separate cohesive package selection.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye code review.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=high`,
  `service_tier=priority`; implementation ran on a lower-power worker.
- Host exposure state: requested_fields_sent
- Application state: applied — the reviewer inspected parser semantics,
  planning-versus-publication ownership, mirror parity, test fidelity, and live
  help; the corrected delta then received a second read-only approval.

## Fresh-Eye Satisfaction

parent-delegated — the first pass found the planning-boundary overstatement;
the corrected four descriptions received a second pass with no remaining
blocker or should-fix, and both reviewer-boundary fingerprints had zero drift.

## Boundary Ownership

- Producer: the release run planner owns its read-only command descriptions.
- Consumer: operators and agents inspecting release prerequisites and packets.
- Owning surface: the public planner, packaged mirror, and focused executable
  readback test.
- Verdict: single-surface
