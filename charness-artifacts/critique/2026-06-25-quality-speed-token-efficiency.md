# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the quality slice that scopes prompt-bulk scans through the quality adapter,
adds compact summary output, excludes stale runtime hot spots, refreshes duplicate
id-set baselines, and updates focused tests.

## Failure Angles

- Jackson/problem framing: stale runtime samples could disappear from markdown
  when every hot spot is stale, making a ranking-fidelity fix look like no data.
- Weinberg/diagnostic: rotating duplicate family ids could update only the hard
  gate baseline while leaving the advisory clone baseline stale.
- Gawande/operations: the low-token prompt-bulk path must preserve adapter
  metadata and a count, not just hide findings.

## Counterweight Pass

- The stale-only markdown blocker was fixed with a no-fresh-samples branch and
  `test_render_runtime_summary_names_excluded_stale_hotspots_without_fresh_hotspots`.
- The paired-baseline blocker was fixed by refreshing both `dup-ratchet-baseline.json`
  and `nose-baseline.json` with the current nose scan.
- Streaming `--summary`, command-timing timestamps, nested-CLI conversion, and
  tokenizer-specific counts are valid follow-ups, not ship blockers for this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/render_runtime_summary.py | action: fix | note: stale-only runtime samples must be named in markdown; fixed with focused test
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/dup-ratchet.md | action: fix | note: rotated code family ids require gate and advisory id-set baselines to move together; fixed by refreshing both
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_find_inline_prompt_bulk.py | action: fix | note: adapter-backed summary path now asserts adapter validity, finding_count, sample, and no full findings payload
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/find_inline_prompt_bulk.py | action: defer | note: summary still computes all findings before sampling; output/token bound is fixed, streaming scan can wait
- F5 | bin: over-worry | evidence: moderate | ref: charness-artifacts/quality/2026-06-25-skill-ergonomics-yaml-summary-quality-review.md | action: document | note: tokenizer-specific counts are not required until a stable repo-owned tokenizer seam exists

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: three bounded angle reviewers and one separate counterweight
reviewer completed through `multi_agent_v1.spawn_agent`. The counterweight found
no remaining act-before-ship issues after the stale-only markdown fix, paired
baseline refresh, adapter-summary assertion, and focused tests.
