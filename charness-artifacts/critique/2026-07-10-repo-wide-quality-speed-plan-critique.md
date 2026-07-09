# Repo-wide Quality and Speed Plan Critique
Date: 2026-07-10

## Execution

- Fresh-eye spec critique completed before implementation with two independent
  angle reviewers and one separate parent-owned counterweight reviewer.
- Packet Consumed: `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.md`
- Target: `references/spec-critique.md`
- Spec Path: `charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md`

## Decision Under Review

Lock an evidence-ranked S1/S2 bundle: two usage-feedback correctness repairs,
a healthy-bootstrap fast path, and overlapped Markdown checks before v0.64.0.

## Capability at Stake

Usage review must not corrupt product decisions or crash on historical data;
common CLI and standing proof paths should get faster without weakening repair,
advisory, blocking, mirror, or release semantics.

## Failure Angles

- Minto/Jackson: the selected slices fit the user's broad request only when the
  final quality record shows broad inventory, ranking, selected fixes, and
  explicit non-claims instead of calling four edits the whole codebase.
- Weinberg/Gawande: delivery/feedback semantics belong in the shared review and
  reconciliation layer; repair ownership stays in `bootstrap_runtime.py`; shell
  overlap must retain deterministic output and blocking exit behavior.
- Acceptance: exact JSON fields, byte-identical rejection, healthy/fallback
  branch proof, and advisory/blocking combinations were missing before review.

## Fixed/Probe/Defer Coherence Result

- Fixed: delivery rows own usage denominator/dimensions; linked feedback enriches
  signal/friction only; invalid history rejects without append; bootstrap fast
  path is reuse-only; Markdown checks may overlap with unchanged semantics.
- Probe: repeated before/after CLI and Markdown timings establish claimed deltas.
- Deferred: lazy `urllib`, changed-file Markdown caching, broad subprocess
  consolidation, pytest worker tuning, and concurrent JSONL locking.
- Result: pass after the pre-implementation contract edits below.

## Acceptance Check Coverage Result

- S1 denominator: focused product-review regression asserts `usage_count == 1`,
  no feedback-created `<missing>` dimensions, delivery-based first/last seen,
  and linked feedback contributes to signal/friction interpretation.
- S1 write safety: malformed existing feedback returns structured
  `invalid_feedback`, exits without traceback, and leaves JSONL byte-identical.
- S2 bootstrap: healthy launcher uses one module probe without repair; absent or
  unhealthy launcher calls the existing bootstrap helper unchanged.
- S2 Markdown: both-pass, advisory-fail/blocking-pass, and blocking-fail cases
  preserve deterministic report order and MarkdownLint's blocking status.
- Bundle: repeated timing samples plus focused tests, mirror sync, and final
  verification lock cover the user-visible and release boundaries.

## Counterweight Pass

### Act Before Ship

- Exact denominator/linking assertions, invalid-history no-append proof,
  reuse-only bootstrap fallback, and Markdown exit/order proof are required.

### Bundle Anyway

- Final quality artifact shows inventory to selection logic and residual gaps.
- Feedback policy remains owned by the review/reconciliation data-contract layer,
  with formatter helpers only as mechanical implementation.

### Over-Worry

- No general telemetry redesign, second bootstrap system, broad test-process
  rewrite, or new caching abstraction is justified by this evidence.

### Valid but Defer

- Lazy `urllib` is a weak incremental win after the bootstrap slice and adds
  release-adjacent review surface; reconsider only with a fresh material profile.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/usage_episode_product_review.py | action: fix | note: deliveries must remain the usage denominator while linked feedback enriches signal interpretation
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/record_usage_feedback.py | action: fix | note: invalid historical JSONL must reject structurally and remain byte-identical
- F3 | bin: act-before-ship | evidence: strong | ref: charness:1100 | action: fix | note: healthy runtime reuse must fall back to the existing bootstrap repair owner
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check-markdown.sh | action: fix | note: concurrency must preserve advisory and blocking output and exit semantics
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md | action: document | note: closeout must show broad inventory ranking and honest residuals
- F6 | bin: bundle-anyway | evidence: moderate | ref: scripts/usage_episode_feedback.py | action: document | note: shared review/reconciliation owns feedback meaning rather than a formatter
- F7 | bin: valid-but-defer | evidence: weak | ref: charness:14 | action: defer | note: lazy urllib does not earn release-adjacent scope without a material post-bootstrap profile

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn surface accepted the requested fields; model execution metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: usage episode and feedback event stream; bootstrap runtime contract;
  inline-code and MarkdownLint checks.
- Consumer: product-review packets; repo script invocations; standing quality gate.
- Owning surface: shared review/reconciliation data contract, existing bootstrap
  repair helper, and the Markdown gate orchestrator respectively.
- Verdict: moved-to-owner

## Deliberately Not Doing

- No changed-file Markdown cache without invalidation proof.
- No general feedback/telemetry abstraction or concurrent writer lock without
  observed concurrency evidence.
- No parser rewrite, worker-count change, nested-process consolidation, or lazy
  urllib in this release slice.

## Pre-Impl Action

Tighten the active goal with F1-F4's exact tests, then delegate the bounded code
bundle. F5-F6 remain required closeout documentation; F7 stays deferred.

## Next Move

Implement the smallest S1/S2 bundle, sync mirrors before focused verification,
then run a fresh-eye code critique before release lock.
