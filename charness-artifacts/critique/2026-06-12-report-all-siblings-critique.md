# Critique Review
Date: 2026-06-12

## Decision Under Review

Extend `--report-all` to the two high-rule-count sibling artifact validators
(critique: 14 rules, debug: 14) via a shared `run_validation_checks` helper
in `artifact_validator.py`, wire both standing gates to it, and narrow D28
to the remaining retro/handoff/ideation + fill-guard + `--write` scope.
Operator-approved narrowed option from the prior template-first critique
(`2026-06-12-critique-review.md`).

## Failure Angles

- Lambda refactor changing debug validator semantics (late-binding capture,
  fail-fast order drift vs HEAD).
- Cascade noise: a missing-section failure repeating through downstream
  section-based checks under `--report-all`.
- Critique validator's own `ValidationError` class escaping the `__main__`
  handler when raised by the shared helper.
- Test pairs not actually pinning fail-fast vs report-all contract; quality
  refactor regression after replacing its inline collect block.

## Counterweight Pass

- Real and folded: duplicate identical violation message (exact-section +
  nonempty-section overlap) — order-preserving dedupe added to the shared
  helper in the same slice.
- Over-worry (probed clean by the reviewer): no closure bugs, fail-fast
  order byte-identical vs `git show HEAD:`, `error_cls` round-trips
  critique's own exception class, mirrors byte-identical, quality covered
  by 17 existing tests including its report-all pair.
- Valid-but-defer: multi-artifact stop-at-first-artifact loop in the
  critique validator is pre-existing behavior, out of slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py | action: fix | note: dedupe identical violation messages while preserving order — fixed this slice before commit
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py | action: document | note: per-artifact loop still stops at the first failing artifact; pre-existing behavior, revisit only if multi-artifact batches become common
- F3 | bin: over-worry | evidence: strong | ref: scripts/validate_debug_artifact.py | action: defer | note: lambda-capture and ordering risks probed against HEAD and found byte-identical

## Reviewer Tier Evidence

- Requested tier: high-leverage (validator-surface change).
- Requested spawn fields: `.agents/critique-adapter.yaml` reviewer_tiers
  mapping targets a Codex host; not sendable on this Claude Code host.
- Host exposure state: host-defaulted
- Application state: host resolved the tier to its default strongest
  reviewer; one bounded reviewer covering angle + counterweight lenses for
  this already-design-critiqued follow-up slice.

## Fresh-Eye Satisfaction

parent-delegated. Reviewer verdict SHIP-as-is with one optional cosmetic
dedupe, which was folded before commit. Concrete signals: reviewer reran
the debug/critique/quality test files (53 passed), verified mirror
byte-identity, and compared fail-fast order against
`git show HEAD:scripts/validate_debug_artifact.py`.
