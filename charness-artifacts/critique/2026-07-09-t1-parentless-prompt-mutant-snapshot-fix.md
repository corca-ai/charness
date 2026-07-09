# T1 parentless prompt-mutant snapshot fix
Date: 2026-07-09

## Decision Under Review

Resolve #426 by changing prompt-mutant generation from parented
`refs/prompt-mutants/*` commits to raw parentless snapshot SHAs: one
capture-facing `baseline_snapshot_sha` and one parentless `mutant_sha` per
selected unit. Keep `baseline_sha` only as original-baseline provenance and
keep cleanup for legacy prompt-mutant refs.

## Failure Angles

- Michael Jackson / problem framing: the core diff solves the named
  parent-diff unblinding channel. The reviewer raised one possible footgun:
  keeping `baseline_sha` in the manifest could let old code treat the parented
  commit as the capture baseline. This was resolved by labeling CLI output
  `baseline_provenance_sha` and documenting `baseline_snapshot_sha` as the
  capture-facing baseline.
- Gerald Weinberg / diagnostic and boundary ownership: the producer boundary
  is correct. `scripts/prompt_mutant_lib.py` now owns parentless snapshot
  creation, while the scorer remains keyed on unit IDs and raw snapshot SHAs.
  The completed pilot goal still describes the old historical run shape; that
  is not rewritten in this T1 slice.
- Atul Gawande / operational checklist: the first reviewed diff still had
  stale CLI/help wording and a scorer fixture carrying `mutant_ref`. Those
  were fixed before closeout; the manifest fixture is now ref-free and the
  CLI summary emits both provenance and snapshot SHAs.

## Counterweight Pass

No Act Before Ship items remain after the critique-driven fixes. Keeping
`baseline_sha` as provenance is not a live footgun now that the CLI labels it
as provenance and `baseline_snapshot_sha` carries the capture-facing meaning.
The old completed pilot artifact remains historical evidence, not a contract
to rewrite during T1. Broader capture-isolation redesign belongs to T2/T3.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/generate_prompt_mutants.py; tests/test_score_prompt_mutation_survival.py | action: fix | note: stale CLI/help and scorer fixture still implied ref-backed manifests; fixed before closeout.
- F2 | bin: over-worry | evidence: moderate | ref: scripts/prompt_mutant_lib.py | action: document | note: retaining `baseline_sha` is acceptable as original-baseline provenance because `baseline_snapshot_sha` is the capture-facing baseline.
- F3 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md | action: defer | note: completed pilot artifact records the old historical run shape; do not rewrite it in this T1 fix.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium; service_tier inherited.
- Host exposure state: requested_fields_sent
- Application state: host returned subagent ids and completion payloads, but no provider-side application confirmation.

## Fresh-Eye Satisfaction

parent-delegated — three bounded angle reviewers and one separate counterweight
reviewer completed through `multi_agent_v1.spawn_agent`.

## Boundary Ownership

- Producer: `scripts/generate_prompt_mutants.py` / `scripts/prompt_mutant_lib.py` produce prompt-mutant arm refs and the mutation manifest.
- Consumer: `scripts/run_skill_efficiency_ab.py` and capture operators use manifest SHAs as arm refs; `scripts/score_prompt_mutation_survival.py` consumes unit IDs and per-unit snapshot SHAs.
- Owning surface: prompt-mutation generator and manifest contract.
- Verdict: owned-correctly
