# Release Critique: Retro Phase-Aware Efficiency

Date: 2026-05-25

## Execution

Fresh-eye satisfaction: parent-delegated.

## Change

Release the #217 `retro` public-skill contract change as a patch release:
phase-aware waste attribution before labeling broad exploration as waste.

#218 remains open as deferred Codex-specific evidence-producer work.

## Angles

- public-skill contract risk
- host-specific evidence boundary
- validation and release readiness
- counterweight against over-scoping #218 into this patch

## Act Before Ship

- Run the release proof sequence before publish: surface sync, deterministic
  validators, release quality gate, release no-drift proof, public release
  verification, and issue-state verification.
- Close #217 only after the release helper verifies GitHub issue state.
- Do not close #218 in this slice.

## Bundle Anyway

- Keep the dogfood update and design/gather artifacts with the implementation
  so future sessions can see why #218 was not bundled.

## Over-Worry

- Exact Codex token totals are not required for #217.
- A full SQLite/TUI analyzer is not required for this release because the
  portable interpretation rule now prevents count-driven waste claims.

## Valid But Defer

- Upstream `audit_codex_session.py` or an equivalent support capability in a
  separate #218 slice.
- Consider a dedicated token/tool-call waste dogfood case after the analyzer
  exists.

## Next Move

Proceed with `v0.7.14` patch release after the already-passed deterministic
quality gates and slice closeout.
