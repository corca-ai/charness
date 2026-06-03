# Testability Quality Ratchet Retro

## Mode

session

## Context

Reviewed the active achieve goal that turned the boundary-bypass advisory probe
into a no-increase ratchet, skillified the portable `quality` contract, and
converted the first clean `inventory_*` boundary-bypass test in-process.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md`
- Fresh-eye reviewers:
  `019e8d85-5c11-7382-882e-7084334a7c0a`,
  `019e8d85-72a3-78d2-82d2-bc146c0b1014`, counterweight
  `019e8d88-656c-7cc1-93d5-83fc943d1ed4`
- Final broad proof: `./scripts/run-quality.sh --read-only` passed
  71 checks, 0 failed.

## Waste

- I ran a broad final gate before the fresh-eye critique was consumed, then had
  to rerun it after real critique findings changed the public contract.
- The first public payload contract under-specified two machine invariants
  already used by the repo-local ratchet: candidate keys and clean/internal
  target disjointness.
- The first Slice 4 payload validator test accidentally added a new
  boundary-bypass candidate, proving the new ratchet was useful but costing an
  extra correction pass.

## Critical Decisions

- Keep the public concept in `quality`, not a new public test skill.
- Treat lazy/composable DSLs as test ergonomics, not proof of production-code
  testability.
- Accept the fresh-eye Act Before Ship findings and turn them into validators,
  tests, and routing triggers before closeout.

## Expert Counterfactuals

- Gary Klein would have forced the pre-mortem question earlier: what hidden
  machine invariant must another repo implement to reproduce the ratchet? That
  would have exposed candidate-key count and schema-drift checks before the
  first broad gate.
- Daniel Kahneman would have slowed the "green gate means done" impulse and
  separated proof of the current repo from proof of the portable public
  contract.

## Next Improvements

- applied: Make fresh-eye critique precede the final broad gate when the
  critique can still change prompt/public contract surfaces.
- applied: Encode portable boundary-bypass invariants as validator-enforced
  fields, not only reference prose.
- applied: Keep new quality-gate tests in-process by default; subprocess tests
  need an explicit CLI-contract reason.

## Sibling Search

Searched sibling surfaces conceptually in this goal: the same derived-invariant
risk existed in both the public payload validator and repo-local ratchet. Both
were patched: public candidate-key/disjointness validation and repo-local
inventory schema drift enforcement.

## Persisted

yes
