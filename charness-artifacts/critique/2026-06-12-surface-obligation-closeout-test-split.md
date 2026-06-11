# Surface obligation closeout test split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-215510-packet.md

## Decision Under Review

Split `run_slice_closeout`-related tests out of
`tests/quality_gates/test_surface_obligations.py` into
`tests/quality_gates/test_run_slice_closeout_surface_obligations.py`, and
regenerate the boundary-bypass baseline for the resulting test-file key
migration.

## Failure Angles

- Problem framing: this could be metric gaming if it only moved lines out of a
  near-limit file. Verdict: the split is behavior-aligned because the original
  surface/manifest tests remain together while closeout-runner behavior now has
  a dedicated module; it does not claim to solve all fixture duplication.
- Diagnostic: baseline regeneration could hide a real boundary-bypass increase.
  Verdict: reviewers confirmed the moved test bodies match `HEAD`, the root and
  plugin baselines are byte-identical, and the current inventory matches the
  regenerated baseline. The regen also removed two stale scaffold/export keys;
  that is recorded as intentional cleanup rather than hand-edited back.

## Counterweight Pass

- Act before ship: include the new closeout test file and critique packet
  artifacts in the commit.
- Over-worry: restoring the two stale scaffold/export baseline keys would make
  the baseline less canonical only to preserve a narrower-looking diff.
- Valid but defer: repeated temporary `.agents/surfaces.json` setup in the new
  closeout test file remains real duplication, but extracting a helper now
  would expand a length/cohesion slice into a broader fixture refactor.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_run_slice_closeout_surface_obligations.py:1 | action: fix | note: include the new closeout test file in the commit.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-06-11-215510-packet.md:1 | action: fix | note: include the critique packet artifacts with this closeout.
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary-bypass-baseline.json:126 | action: document | note: baseline regeneration also removes two stale scaffold/export keys.
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_run_slice_closeout_surface_obligations.py:18 | action: defer | note: repeated temporary surfaces fixture setup remains a future cleanup candidate.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: inherited parent model; no explicit model override sent
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted two bounded angle reviewer requests and one counterweight reviewer request; host did not confirm provider-side application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned two bounded angle
reviewers and one separate counterweight reviewer through `multi_agent_v1`;
all completed read-only review. No same-agent substitute was used.
