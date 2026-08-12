# R6 Boundary-Bypass Content-Identity Critique

Date: 2026-08-12

## Execution

One bounded R6 review, two contrasting code-critique angles, and an independent
counterweight pass reviewed the v2 content-identity change. The problem-framing
angle found a real membership leak: a non-import-safe spawn in the same test
could rotate an otherwise unchanged candidate key. The parent repaired it, then
the mandatory second bounded review read the repaired surface and found no
further issue. Every reviewer boundary fingerprint verified clean.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`,
  service tier `priority`, and `fork_turns: none`; bounded read-only scope.
- Host exposure state: metadata-hidden
- Application state: the host returned no reviewer-tier application metadata.
- Delivery state: findings-received

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.json
- Packet path: charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.json
- Packet SHA256: 904595d2ae0d7dd9015b0b69e9ca5929cb9aee2808dfc005ec06b4896086f6b4
- Identity SHA256: 78c7b949b282f9eed0e82f05d0597e12a01790788bfdad282489b0b961c2c917

## Boundary Ownership

- Producer: the Python inventory owns normalized AST call-site membership and
  its versioned payload.
- Consumer: the boundary-bypass ratchet owns identity comparison; the
  subprocess-only advisory consumes baseline path pairs as non-verdict lookup
  metadata.
- Owning surface: inventory payload v2 plus its ratchet/public-validator
  contract.
- Verdict: owned-correctly

## Target

Code critique: ruling 6 / `#585` content identity for the boundary-bypass
no-increase verdict.

## Change

Replace path-pair identities with a SHA-256-derived, offset-free AST call-site
content fingerprint. Preserve sorted duplicate member hashes, stamp algorithm
version `1` into payload and baseline, migrate the public validator and both
root/plugin baselines, and retain baseline path pairs only for advisory lookup.

## Capability at Stake

Moving an unchanged test no longer creates a new ratchet identity, while a
candidate call's content, membership, or multiplicity change still does. An
unrelated non-candidate spawn does not rotate that identity.

## Findings and Counterweight Triage

- R1-P1 | act-before-ship | A member hash was added before import-safe target
  filtering, so unrelated non-candidate spawn work changed a candidate key.
  Repaired by retaining targets beside each AST call until filtering and hashing
  only calls that intersect the import-safe candidate set; a mixed-call
  regression proves it.
- R2 | no findings | The repaired membership selection, path move behavior,
  duplicate preservation, migrated 47-key baseline, and root/plugin mirror all
  match the v2 contract.
- Bundle anyway | The counterweight requested an end-to-end real-inventory
  path-move assertion. It was added: a baseline made from one synthetic repo
  accepts identical content under a different test path.
- Over-worry | Do not force `candidate_pairs` to change for a path move. They
  are advisory locator metadata and do not participate in the ratchet verdict.
- Valid but defer | A future non-Python emitter needs its own documented
  canonical implementation for algorithm `1`; the current local Python
  producer is version-stamped so incompatible cross-stack output fails rather
  than silently comparing keys.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/inventory_boundary_bypass_lib.py | action: fix | note: filter member hashes to calls that contribute import-safe candidates
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/test_boundary_bypass_ratchet.py | action: fix | note: add real-inventory moved-path ratchet proof
- F3 | bin: over-worry | evidence: weak | ref: scripts/subprocess_only_coverage_advisory.py | action: document | note: baseline path pairs remain advisory locator metadata
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/boundary-bypass-ratchet.md | action: defer | follow-up: deferred charness-artifacts/spec/2026-08-11-six-operator-rulings.md#6-585--content-fingerprint-re-key | note: cross-language canonicalization is outside the one Python producer slice

## Defect Class Cross-Link

charness-artifacts/retro/recent-lessons.md — a proof surface must bind the
actual semantic producer/consumer relation, not an adjacent representation.

## Deliberately Not Doing

- No `set()` deduplication of member hashes, path-sensitive verdict key, push,
  release, hosted CI readback, issue closure, or Cautilus evaluation.
- No cross-language algorithm implementation in this Python-only slice.

## Pre-Merge Action

Focused inventory/ratchet/validator/advisory tests, live v2 payload validation,
the live ratchet, plugin mirror check, and the repository pre-commit gate must
pass before committing.
