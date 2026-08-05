# Issue #512 metric window ordering code critique
Date: 2026-08-06

## Decision Under Review

Change `record_metric_window` so an existing authored `## Final Verification`
body remains a contiguous prefix and the generated metric line is appended after
it. The public reference, generated plugin mirror, and regression test are part
of the same contract.

## Diff Scope

The slice is limited to the metric-window helper's authoring-order failure in
#512. It does not change serial refusal aggregation, soft-wrapped routing,
provider/CEAL behavior, installed-machine behavior, or broad parser refactors.

## Target

Code critique: Jackson (problem framing), Weinberg (diagnosis and ownership),
Gawande (operator/regression coverage), followed by a separate counterweight.

## Capability at Stake

An author can run the helper and still exact-match-replace the authored
`Final Verification` block without the helper's generated line invalidating the
replacement. Existing-line replacement remains idempotent and probe-readable.

## Failure Angles

- Jackson found the implementation and regression aligned with the reported
  failure. His initial documentation-order concern was repaired: the reference
  now states that exact-match filling is safe either before or after the helper.
- Weinberg placed the repair at the producer (`record_metric_window`) rather
  than teaching a consumer to compensate. Source/plugin parity was checked.
  His initial packet-binding concern was addressed by regenerating the final
  packet and validating its recorded `sha256-v2` identity.
- Gawande found no required operational gap: the focused test covers the former
  exact-prefix failure, while existing tests cover replacement, idempotence,
  empty sections, CLI behavior, and probe parsing.

## Counterweight Pass

- Act Before Ship: none remain after the reference-order clarification and
  final packet regeneration.
- Bundle Anyway: the reference clarification is already bundled with the code
  fix and generated mirror.
- Over-Worry: broad refactors, provider/CEAL behavior, install behavior, and
  already-covered serial-refusal or soft-wrap work are outside this causal
  slice.
- Valid but Defer: the pre-existing global `Host metric window:` matching
  strategy deserves a concrete misplaced-line reproduction before a separate
  design change.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/references/goal-artifact.md:371-377 | action: document | note: document both safe authoring orders; completed in this slice and mirrored to the plugin
- F2 | bin: over-worry | evidence: moderate | ref: issue-512 scope and current helper/parser boundary | action: defer | note: do not expand this ordering repair into provider, install, or broad parser behavior
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/goal_metric_window_lib.py:111-126 | action: defer | note: global metric-line matching remains a follow-up only if a concrete misplaced-line case appears

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra; reasoning_effort=medium; service_tier=priority; fork_context=false; unnamed one-shot spawn.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden (the host returned agent ids and findings but no separate application confirmation).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; three named angle reviewers and one separate counterweight
returned findings. Each reviewer boundary fingerprint verified clean.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-06-issue-512-final-review-packet.json
- Packet path: charness-artifacts/critique/2026-08-06-issue-512-final-review-packet.json
- Packet SHA256: fc2254422732b8482e22f696fd0b991050a1c718ac4a693f82484a0f1db96bc2
- Identity SHA256: e725896886a1c28fbc7fe584c73ab20bd3da45972b530277a0285f2388ea2d30

## Boundary Ownership

- Producer: `skills/public/achieve/scripts/goal_metric_window_lib.py:record_metric_window`.
- Consumer: `scripts/host_log_probe_lib.py:parse_goal_metric_window` and the goal closeout metric-window evidence loader.
- Owning surface: achieve metric-window authoring helper; the plugin copy is a generated mirror.
- Verdict: single-surface

## Deliberately Not Doing

No claim is made about a Ceal host roundtrip, provider adapter, installed plugin,
remote CI, or migration of artifacts already written with the former prepend
ordering. Those require separate evidence or a concrete follow-up case.

## Next Move

Run the normal focused and repository quality gates, then carry this critique
and the debug artifact into the #512 closeout carrier. No further implementation
change is required by this review.
