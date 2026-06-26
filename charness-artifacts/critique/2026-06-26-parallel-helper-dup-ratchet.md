# Critique Review
Date: 2026-06-26

## Decision Under Review

Extract the repeated parallel subprocess collection pattern into
`scripts/subprocess_guard.py`, consume it from command-docs and skill-surface
preflight, and refresh the dup-ratchet baseline after inspecting new family
summaries.

## Failure Angles

- Helper semantics: a generic helper could change timeout behavior or result
  ordering for existing callers.
- Baseline masking: refreshing dup-ratchet could hide genuinely new duplication.
- Consumer drift: command-docs and skill-surface preflight could preserve speed
  but lose their deterministic report order.

## Counterweight Pass

- Existing `run_process()` keeps its default timeout; the new batch helper is
  opt-in and has a direct order-preservation test.
- New family summaries were inspected; the block was consistent with line-offset
  family id churn and duplicated helper shape from the preceding slices.
- Focused tests, dup-ratchet, and mirror drift proof passed after the refactor.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/subprocess_guard.py | action: fix | note: extracted run_processes_in_order and covered order preservation directly
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: fix | note: refreshed dup-ratchet baseline after inspecting closeout failure family summaries

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent closeout repair critique

## Fresh-Eye Satisfaction

not spawned: closeout-gate repair with direct failing gate reproduction and
deterministic focused proof.
