# Issue 597 Quality Fixture Gate Repair Critique
Date: 2026-08-12

## Decision Under Review

Refuse empty fixture corpora, require minimal observation provenance, and wire
the fixture verifier into the standing quality runner.

## Failure Angles

- A green empty corpus is a verdict escape.
- A syntactically valid empty JSON is the same escape at the next layer.
- A file-change surface cannot detect deletion; the runner must be final reader.

## Counterweight Pass

- Acted before ship on empty JSON and provenance completeness.
- Kept nullable `final_consumer`, because recorded evidence can honestly have no
  executable reader; its `non_claim` remains required.
- Did not re-run awiki, which is outside this integrity verifier's boundary.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_quality_tool_fixtures.py | action: fix | note: refuse empty/missing fixture corpus and incomplete provenance.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: queue verifier as final quality consumer.
- F3 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/debug/2026-08-12-issue-597-quality-fixture-gate-debug.md | action: defer | note: external awiki recapture is outside integrity proof.

## Reviewer Tier Evidence

- Requested tier: standard.
- Requested spawn fields: n/a — host-default reviewer controls were used.
- Host exposure state: host-defaulted
- Application state: n/a.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-143920-packet.json
- Packet path: charness-artifacts/critique/2026-08-12-143920-packet.json
- Packet SHA256: 93c30ea562a00445257b5a949a01daf692fbbffe2902430f5474dabc1f693ed9
- Identity SHA256: b06bf97e9286f76dbed91af2dcd7a3721e47ef173f5b44359bac92291174baa2

## Boundary Ownership

- Producer: checked-in fixture corpus and its observation metadata.
- Consumer: `check_quality_tool_fixtures.py` through the run-quality lane.
- Owning surface: fixture integrity verifier plus standing quality runner.
- Verdict: owned-correctly
