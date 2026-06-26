# Critique Review
Date: 2026-06-26

## Decision Under Review

Add per-scan path-result caches to `inventory_boundary_bypass_lib.py`.

## Failure Angles

- Stale cache: a target file could be changed during one scan and the cached
  result would hide that change.
- Complexity: cache plumbing could make the simple advisory scanner harder to
  reason about for little speed gain.
- Generated surface drift: root script changes must sync the plugin mirror.

## Counterweight Pass

- The scan is a single-process snapshot over one working tree; target files are
  not expected to mutate during one inventory pass.
- The cache is local to `find_boundary_bypass_candidates()` and not global.
- Ratchet JSON output remained unchanged and plugin mirror drift check passed.
- Timing samples showed no material wall-clock gain, so the closeout records
  this honestly as structural cleanup rather than a speed claim.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: moderate | ref: scripts/inventory_boundary_bypass_lib.py | action: fix | note: repeated target probes now share per-scan caches with unchanged ratchet output
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/inventory_boundary_bypass_lib.py | action: defer | note: profile AST scanning before adding any further ratchet optimization complexity

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: local cache refactor with unchanged deterministic ratchet output
and synced generated surface.
