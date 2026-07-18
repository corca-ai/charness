# Critique Review
Date: 2026-07-18

## Decision Under Review

Route SessionStart hidden-capability lookup through a compact YAML catalog view,
while preserving the full catalog contract and bundling only measured test-cost
and proven orphan cleanup.

## Failure Angles

- Problem/interface: the old hook command used an unsupported public `--json`
  flag; the replacement must execute and retain the facts its agent consumer needs.
- Diagnostic/boundary: the catalog remains the producer, the CLI remains the YAML
  renderer, and SessionStart consumes a projection rather than owning inventory.
- Operational: source/export sync, full-view compatibility, conflicting output
  flags, and dynamic references to deleted symbols were reviewed explicitly.

## Counterweight Pass

- Act Before Ship: add a full public-CLI preservation assertion; completed in
  `tests/charness_cli/test_codex_cache_refresh.py`.
- Bundle Anyway: align the hook docstring, reject `--summary --json`, and cover
  every projected hidden layer; completed with focused tests.
- Over-Worry: rewriting historical or generic bare-catalog references would
  incorrectly turn valid full-detail consumers into summary consumers.
- Valid but Defer: version or budget the compact schema only after it gains an
  external compatibility consumer; today it is an opt-in routing projection.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_codex_cache_refresh.py | action: fix | note: full public CLI output now has a preservation assertion
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/capability_catalog.py | action: fix | note: contradictory summary-plus-json flags now fail explicitly
- F3 | bin: over-worry | evidence: strong | ref: docs/public-skill-dogfood.json | action: document | note: historical and generic full-catalog references remain unchanged
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/capability_catalog.py | action: defer | note: compact schema versioning waits for a real compatibility consumer

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but did not expose provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated — two distinct angle reviewers and one separate counterweight
reviewer consumed `2026-07-18-045813-packet.md`; parent fingerprint verification
returned `ok: true` with no drift after each review phase.

## Boundary Ownership

- Producer: capability catalog source and inventory builders.
- Consumer: SessionStart agent/operator deciding hidden support or integration availability.
- Owning surface: catalog projection in `scripts/capability_catalog.py`, public
  YAML rendering in `charness`, and SessionStart as a projection consumer.
- Verdict: owned-correctly
