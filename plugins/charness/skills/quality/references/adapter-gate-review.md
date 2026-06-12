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

## Template-First Artifact Gates

A validator that constrains the shape of a hand-authored artifact creates
n-fold rework when authors discover its rules one failed run at a time. When
gate review finds an artifact-shape validator, check three properties instead
of only whether the gate passes:

- a producing scaffold exists and its unedited output passes the validator
  (provable with a scaffold-to-validator round-trip test);
- conditional rules that only fire after the slots are filled — line caps,
  required tokens for specific statuses, per-line bullet grammar — are surfaced
  in the template itself as fill-time guidance, not left for post-hoc failures;
- the validator offers a report-every-violation mode and the standing gate uses
  it, so a multi-rule draft is fixed in one pass rather than one rule per run.

Classify an artifact-shape validator with no producing scaffold as
`AUTO_CANDIDATE`: the structural action is to add the scaffold plus the
round-trip test before tightening any rule. A scaffold whose output fails its
own validator is a `structural_fact` finding. A missing
report-every-violation mode is `AUTO_CANDIDATE` at most, never a blocker by
itself. Authors should fill scaffold slots in place; rewriting sections from
scratch is the failure mode that reintroduces conditional violations even
when a scaffold exists.
