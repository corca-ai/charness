# Lane brief: 746-explain (lane C2)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`
(rev 2), especially D6 (`components`, `explain` contracts) and D8. The
graph core, carriers/roots, and classify/changed have all landed (modules:
`graph_model`, `graph_roles`, `graph_imports`, `graph_mirrors`,
`graph_carriers`, `graph_queries`, commands `graph|carriers|classify|
changed`). Build additively: suggest `graph_components.rs`; one dispatch
arm each in `lib.rs`; fixtures under `native/repograph/fixtures/components/`.
NOTE: a sibling lane (`746-analyzer`) runs concurrently on the same crate —
keep shared-file edits minimal. Do not spawn descendant agents.

## Outcome

1. `repograph components`: strongly connected components (over imports +
   invokes edges), rootless components, validator/test-only islands
   (components reachable only from validation or test roots), and
   import-boundary violations RE-REPORTED from the same graph with
   `export-safe` v1 remaining the verdict owner — include a test running
   both commands on a violation fixture and asserting the violation sets
   agree. Pure report: exits 0/2/3 (3 only for unestablished scope).
2. `repograph explain --path <p>`: the roots reaching p with the actual
   typed edge paths traversed (bounded: report up to a few shortest root
   paths, stated in the schema, not silently truncated — include a
   `paths_bounded` flag), a `dependents` section (reverse edges), and
   nearest classified ancestors when no root reaches p. Pure report:
   0/2/3.
3. Both commands take the common `--repo-root/--file-list/
   --exclude-prefix` (default `plugins/` + `native/repograph/fixtures/`)
   and `--analyzer-result` identity-only plumbing.
4. Fixtures with exact expected sets: a cross-package cycle (SCC),
   a rootless component, a test-only closed component (test root only),
   an explain case with a multi-edge root path and a dependents set.
5. `cargo test/fmt/clippy -D warnings/build --release` green.
6. Whole-repo run to report (not assert): SCC count and sizes >1,
   rootless component count, test-only island count, and
   `explain --path scripts/surfaces_lib.py` summarized.

## Boundaries

Only `native/**`. Frozen v1 ABIs unchanged; update the shared usage
string + its ABI.md copy and add the two ABI sections following the
existing additive-command style. No analyzer parsing (sibling lane), no
role-rule changes.

## Stop condition and result shape

One coherent commit, prefix `topo(746):`. Final message: built, commands +
observed results incl. the whole-repo component census, deviations with
reasons.
