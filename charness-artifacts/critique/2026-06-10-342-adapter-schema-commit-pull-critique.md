# 342 adapter-schema commit-time pull slice critique
Date: 2026-06-10

## Decision Under Review

Close #342 by extending `scripts/validate_adapters.py` with a generic
integration-schema validation step (`.agents/<name>-adapter.yaml` ↔
`integrations/<name>/manifest.schema.json`), so the stronger validation owner
runs at every validate-adapters timing (commit-time dispatcher + broad gate,
same command) instead of only at the runtime emitter.

## Failure Angles

- The seam could fork validation logic per integration (the anti-pattern the
  disposition review named) or add a second owner for the same file.
- The new validation could break consumer repos sharing the gate plan
  (missing schema, missing jsonschema/yaml deps).
- A parser split (`adapter_lib.load_yaml` minimal parser vs the runtime's
  `yaml.safe_load`) could make the commit verdict drift from the runtime owner.
- Tests could pin the helper function but not the `main()` wiring, letting the
  call site silently disappear.
- The mirror-image direction (schema edit invalidating a live adapter) and the
  consumer-repo bundled-schema fallback could be silently assumed covered.

## Counterweight Pass

- Real and folded: the `main()` wiring gap (subprocess-level CLI test added),
  the missing-`yaml` degrade case (parametrized), and the consumer-repo
  fallback asymmetry (named in the docs row as a known asymmetry).
- Over-worry: double manifest validation at broad timing
  (`validate_usage_episodes.py` + validate-adapters) — same schema file, no
  logic fork, ~10ms; t-events gate now stricter than its tolerant runtime
  loader — enforcing the published schema is the point, vendoring the schema
  is the opt-in.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/validate_adapters.py:281 | action: fix | note: no automated test covered the main() wiring — all tests called the helper directly; a deleted call site would pass every gate. Fixed: subprocess CLI test asserting exit 1 + offending key in stderr.
- F2 | bin: act-before-ship | evidence: moderate | ref: docs/conventions/validator-timing-layers.md table row | action: document | note: usage-episodes emitter falls back to the charness-bundled schema when a consumer repo lacks integrations/usage-episodes/, so the runtime owner validates while the commit gate inherits nothing there. Documented as a known asymmetry in the classification row.
- F3 | bin: bundle-anyway | evidence: weak | ref: scripts/validate_adapters.py:214 | action: fix | note: degrade test covered missing jsonschema only; missing yaml shares the path. Fixed: parametrized over both deps.
- F4 | bin: over-worry | evidence: weak | ref: scripts/validate_usage_episodes.py:178 | action: defer | note: the broad gate now validates the usage-episodes manifest twice (validate-usage-episodes + validate-adapters); same schema file, no fork, negligible cost.
- F5 | bin: over-worry | evidence: weak | ref: scripts/t_events_emit_lib.py:40 | action: document | note: t-events runtime loader is tolerant (no jsonschema), so the gate is stricter than its runtime owner; enforcing the published additionalProperties:false contract is deliberate.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only, shared parent worktree).
- Requested spawn fields: subagent_type=general-purpose, name=slice1-critique, bounded slice packet (intent, changed files, invariants, tests/proof, non-claims, out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned reviewer verdict with agentId a098aa449792d349f (17 tool uses, independent re-verification of tests, mirror byte-sync, dispatcher wiring, and sibling set).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (reviewer agentId a098aa449792d349f).
The reviewer independently re-verified: 18 tests passing, live gate 0.93s,
mirror byte-identical, dispatcher fires on `.agents/` paths only, sibling set
exactly {usage-episodes, t-events, worktree}, and the yaml.safe_load parse
matching the runtime owner byte-for-byte. Nits folded before commit: the
main()-wiring subprocess test (F1), the missing-yaml degrade case (F3), and
the consumer-fallback asymmetry doc line (F2).
