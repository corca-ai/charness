# Adapter Gate Review

Use adapter/gate review when quality pressure is about what should be enforced,
recommended, acknowledged, or migrated.

## Classes

- `structural_fact`: directly verifiable facts such as invalid adapters,
  missing declared surfaces, broken links, malformed schemas, or failing gates.
- `contextual_recommendation`: judgment-heavy guidance that should stay in a
  review queue with evidence, confidence, and a suggested action.
- `acknowledgement_gap`: a recommendation is intentionally suppressed or
  accepted without enough durable rationale.
- `migration_gap`: existing adapters still resolve, but the adapter surface has
  not adopted newer optional fields or defaults.
- `brittle_hard_gate_smell`: phrase matching or prose heuristics are close to
  becoming hard failures without a low-noise invariant.

## Enforcement Tiers

- `AUTO_EXISTING`: a current deterministic gate owns this fact.
- `AUTO_CANDIDATE`: the invariant looks low-noise enough to consider as a
  future deterministic gate after a maintainer confirms the structural action.
- `NON_AUTOMATABLE`: keep this as reviewable advisory state unless a sharper
  invariant appears.

Do not promote contextual recommendations into hard gates just because they are
important. Promote only when the expected response to failure is clear and
false positives are rare.
