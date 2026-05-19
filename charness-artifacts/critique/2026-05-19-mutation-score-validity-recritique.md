# Mutation Score Validity Recritique

Date: 2026-05-19

## Target

Post-fix critique for the mutation testing validity repair: active sampling,
scheduled sample rotation, zero-reachable fail-closed behavior, and no-tests
scope-gap fail-closed behavior.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-05-19-093558-packet.md`

## Findings

### Act Before Ship

- Final blocker fixed during the critique loop: `worker_outcome == "no-test"`
  no longer falls through into `survived` counting, so no-tests mutants stay out
  of the reachable score denominator.

### Bundle Anyway

- The final prepare packet is kept as closeout evidence for the delegated
  review.
- The checked-in workflow and template now both assert the sample step only runs
  for full runs when `cmd_sample` is non-empty.
- The active repo adapter sample command is directly covered by regression
  tests.

### Over-Worry

- A bounded full hosted mutation run is not required before shipping this slice.
  Local proof covers the score semantics, adapter wiring, workflow seed, and
  sample config/manifest rewrite; the next GitHub scheduled run is the hosted
  proof point after push.

### Valid But Defer

- A minimum reachable-mutant threshold and a broader sample pool than
  `scripts/*.py` would improve representativeness, but they are policy/design
  ratchets beyond this false-green fix.

## Applied Decision

Ship the fail-closed score semantics and active sampler wiring with the debug
RCA, generated plugin export, and full closeout proof.
