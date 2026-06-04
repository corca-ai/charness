# Retro: Nose duplicate refactoring

## Context

This session completed the active `nose` duplicate-refactoring goal: bootstrap
and adapter duplicate families were reduced, the near-copy hard gate was
narrowed to document surfaces, and `jscpd` was reassessed after cleanup.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md`
- Strategy doc: `docs/duplicate-detection-strategy.md`
- Commits: `8cd0975d`, `2bff46b0`, `f838ebf6`
- Final gate: `./scripts/run-quality.sh --read-only` passed with 70 phases in 53.4s.
- Fresh-eye reviews checked the adapter refactor, document near-copy gate, and
  final `jscpd` disposition.

## Waste

The main waste was interpretive, not implementation-heavy: raw clone counts were
easy to overstate as either noise or proof. The final `jscpd` review needed the
command/options recorded next to the report counts so future readers can
reproduce the exact scan shape.

## Critical Decisions

- Kept `check_doc_near_duplicates.py` as the hard document near-copy gate instead
  of replacing whole-file similarity with token/block clone detection.
- Used `nose 0.4.0` as the refactoring driver and left arbitrary-machine support
  binary work explicit rather than pretending the sibling checkout is a product
  path.
- Deferred `jscpd` hard-gate adoption after evidence showed it remains useful
  but still needs baseline/ignore policy around portable bootstrap debt.

## Expert Counterfactuals

- Gary Klein would have asked for the recognition cue earlier: "Which clone
  families would cause us to block a push today?" That points directly to the
  high-floor `jscpd` comparison instead of only reading the default count.
- Daniel Kahneman would have pushed against a binary "noise or gate" conclusion.
  The better framing is base-rate plus threshold: default `jscpd` is noisy for a
  hard gate, while high floors show small real follow-up candidates.

## Next Improvements

- applied: record command lines and version beside temporary clone-report
  counts before treating a tool comparison as durable evidence.
- applied: keep duplicate-detector responsibilities named by algorithm shape:
  whole-file near-copy gate, exact token/block clone candidate, and advisory
  semantic/structural clone inventory.

## Sibling Search

n/a - the improvement is a closeout evidence habit applied in this goal artifact
and strategy doc, not a code pattern with plausible sibling implementations.

## Persisted

Persisted by `persist_retro_artifact.py`.
