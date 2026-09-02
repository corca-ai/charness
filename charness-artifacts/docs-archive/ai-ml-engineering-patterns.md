# AI/ML Engineering Patterns For Charness

> Status: retired 2026-09-02
> No successor; dated record.

This page records the engineering patterns that are current in Charness. It
does not claim product-success measurement; consuming products own that data.

## Current state

- Deterministic quality gates, metadata-rich artifacts, debug RCA, release proof,
  and lesson-ledger feedback are the core loop.
- Product outcome telemetry, prompt storage, and model/search experiment grids
  are deliberately outside the harness core.

## Patterns to keep

- Treat evaluation as one proof class, not the whole product metric.
- Keep validation, metadata, rollback pointers, and durable artifacts together.
- Use several health signals instead of optimizing one proxy.
- Monitor failures through debug, retro, issue, quality, and goal/artifact loops.

## Quality posture

The quality bar should prefer deletion, ownership clarification, and a smaller
production surface before adding another heuristic or event stream. A lesson
that changes behavior belongs in the lesson ledger; a durable decision belongs
in a current `docs/` page or a dated artifact, not in an accumulating telemetry
file.

## Open boundary

If a consuming product needs first-value, acceptance, or satisfaction metrics,
it should define the vocabulary, privacy policy, and storage in that product's
own source-of-truth docs. Charness can consume a proven result as an artifact,
but should not silently create a second product analytics system.
