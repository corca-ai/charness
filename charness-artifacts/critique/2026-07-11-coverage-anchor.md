# Critique Review
Date: 2026-07-11

## Decision Under Review

Use an explicitly resolved closeout campaign SHA as the single anchor for
changed-path collection and both mutation-coverage producers, while preserving
the historical `origin/main` default for omitted or automatic bases.

## Failure Angles

- Resolving a moving ref twice could split the payload range from the marker
  range. The orchestration now resolves once and passes the SHA to every
  consumer.
- Helper-only tests could miss orchestration wiring. Main-path tests now prove
  explicit, omitted, and automatic base behavior for broad and focused paths.
- Comparing hashes alone did not prove the consumer contract. The revised test
  writes a real producer marker, proves consumer acceptance, then proves
  rejection after changed-pool drift.

## Counterweight Pass

- No new CLI option or campaign-anchor object was introduced.
- A small resolved-SHA helper moved to `surfaces_lib`; a broader closeout module
  split is real headroom debt but is not required for this behavioral repair.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py | action: fix | note: resolve the explicit ref once and reuse the SHA for range, broad, and focused consumers; cleared
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_run_slice_closeout_surface_obligations.py | action: fix | note: add causal explicit/default/auto orchestration proof and producer-consumer marker proof; cleared
- F3 | bin: over-worry | evidence: weak | ref: scripts/mutation_coverage_producer.py | action: document | note: do not introduce a campaign-anchor abstraction or new CLI
- F4 | bin: valid-but-defer | evidence: strong | ref: scripts/run_slice_closeout.py | action: defer | note: broader closeout-module decomposition remains deferred; this slice keeps the file below its enforced limit

## Reviewer Tier Evidence

- Requested tier: high-leverage, for shared closeout and coverage compatibility.
- Requested spawn fields: model and reasoning override were sent through the host spawn surface.
- Host exposure state: metadata-hidden
- Application state: unverified; host acceptance did not expose provider application.

## Fresh-Eye Satisfaction

parent-delegated; the bounded reviewer consumed the working-tree and post-review
packets, cleared F1/F2/F2R after two focused revisions, and each rail-1 verify
returned zero drift.

## Boundary Ownership

- Producer: `run_slice_closeout` campaign/ref resolution.
- Consumer: committed-range collection, broad/focused coverage producers, and the freshness consumer.
- Owning surface: closeout orchestration resolves once; generic helpers consume the supplied SHA.
- Verdict: owned-correctly
