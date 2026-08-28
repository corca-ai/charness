# Lane brief: 746-analyzer (lane D)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`
(rev 2), especially D5 (provider contract — normative) and D8 (partial
external analysis fixtures). The graph core, carriers, classify/changed
have landed; every graph-backed command already accepts repeatable
`--analyzer-result <file>` as identity-only plumbing that marks the
affected scope unestablished (`analyzer-not-parsed`). This lane replaces
that stub with real provider parsing. Suggest `graph_analyzer.rs`; keep
shared-file edits minimal (a sibling lane `746-explain` runs concurrently
on the same crate). Do not spawn descendant agents.

## Outcome

1. `repograph.analyzer_result.v1` input schema, deserialized with
   serde `deny_unknown_fields` and NO fallback enum variants: analyzer
   identity + version, source identity (commit or digest — field names
   must avoid `key`/`token`/`secret`), declared scope (path set or
   globs), typed `imports` edges, exclusions, parse conditions,
   completeness (`complete | partial | failed`).
2. Ingestion rules (all typed, all tested):
   - edges whose endpoints fall outside the declared scope → typed
     `scope-violation` records, edges dropped;
   - analyzer edges may only connect `external-module` nodes or an
     external-module to a snapshot file INSIDE the declared scope; they
     can never overwrite or delete Charness-owned skill/adapter/mirror/
     command edges (test: an analyzer result claiming a mirrors-edge
     target is rejected as a violation);
   - `partial`/`failed` completeness, version-incompatible schema,
     zero-module results → every claim over the declared scope becomes
     `unestablished` with a typed condition; never a clean graph;
   - multiple `--analyzer-result` files merge in argument order;
     overlapping declared scopes → typed `scope-conflict` record.
3. rev-dep: a documented mapping (in `native/repograph/ANALYZERS.md`,
   markdownlint-clean) from rev-dep's JSON output shape to
   `analyzer_result.v1`, plus ONE fixture pair (a small hand-written
   rev-dep-shaped document + its expected ingestion). Recorded non-claim:
   no live rev-dep producer is exercised; the provider mechanism is the
   deliverable.
4. Fixtures: complete result over a fixture scope; partial result
   (scope claims unestablished); scope violation; overwrite attempt;
   version mismatch; scope conflict between two results.
5. `cargo test/fmt/clippy -D warnings/build --release` green.

## Boundaries

Only `native/**`. Frozen v1 ABIs unchanged. Do not add analyzer flags to
the four frozen commands. No network; no npm/rev-dep execution.

## Stop condition and result shape

One coherent commit, prefix `topo(746):`. Final message: built, commands +
observed results, deviations with reasons.
