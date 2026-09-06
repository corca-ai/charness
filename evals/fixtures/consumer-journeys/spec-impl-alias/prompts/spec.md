# Spec phase: alias resolution

Work in the consumer repository seeded beside this prompt. Read its
`AGENTS.md` and `README.md` first. Use the installed `spec` skill from
`CHARNESS_FIXTURE_PLUGIN_ROOT`; report the consumed skill path and package
version in your handoff. Resolve that skill's references from the exported
package root, never from host-installed Charness.

Create exactly `docs/alias-resolution.md` and make no other file changes in
this spec phase. Do not implement the feature. The next context will consume
this exact document.

The concrete request is to extend the public `Catalog` API with aliases while
keeping canonical lookup compatible:

- Existing `Catalog(mapping)` callers and canonical keys must continue to
  work unchanged.
- The new form is `Catalog(mapping, aliases=...)`.
- Represent aliases as a list of `(alias, canonical_key)` pairs, not a dict,
  so duplicate definitions remain observable and can be rejected rather than
  silently overwritten.
- Reject an alias name that collides with a canonical key.
- Reject an alias whose target is not an existing canonical key.
- Reject duplicate alias definitions deterministically, including duplicates
  that repeat the same target. Do not use last-write-wins behavior.
- These invalid alias definitions raise `ValueError`; unknown lookup remains
  `KeyError`. Report the first invalid pair in input order and include its alias
  name in the exception message.
- Define the public failure shape and deterministic offending-entry behavior
  precisely enough that two implementers will make the same choice.

The document must include fixed success criteria and a criterion/check mapping:
each criterion names its observable behavior and its concrete test or check,
including the preserved baseline behavior and every rejection above. State
what “ready for impl” means, identify the first implementation slice, and keep
any probe or deferred decision visible. Keep the contract bounded to this
fixture; do not propose a new evaluator, dependency, or broad repository
rewrite.
