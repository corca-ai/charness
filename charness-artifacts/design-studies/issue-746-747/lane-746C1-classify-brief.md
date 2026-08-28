# Lane brief: 746-classify (lane C1)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`
(rev 2), especially D1a (role rules — normative), D6 (`classify` and
`changed` contracts: presence semantics, exit tables, `--exclude-prefix`
defaults, fnmatch reuse mandate) and D8 (#743 scenario + Go fixture).
Lane A landed the graph core; build on it additively. NOTE: a sibling lane
(`746-carriers`) runs concurrently in its own worktree on the same crate —
keep changes additive: new module(s) (suggest `graph_queries.rs`), one
dispatch arm in `lib.rs`, fixtures under
`native/repograph/fixtures/classify/`, minimal `graph.rs` edits. Do not
spawn descendant agents.

## Outcome

1. `repograph classify --path <p>...` per plan D6: per path — `role`
   (from lane A's D1a resolver), `presence`
   (`present | absent-from-snapshot`), owning package, per-surface
   production membership computed with the EXISTING `surfaces` fnmatch
   matcher (`src/surfaces.rs`) — no second matcher. Absent paths still
   resolve pattern-level surface membership and path-shape role rules;
   when rules cannot apply the role is `unestablished-absent`; an absent
   or unestablished path is NEVER reported as not-production — the field
   stays typed. Exit 3 if any requested path is unestablished, else 0
   (2 usage, 70 internal).
2. `repograph changed --path <p>...`: affected surfaces/packages/roots
   with per-path explanations; same presence semantics; pure report
   (0/2/3).
3. Equality test: `classify`'s surface membership equals `match-surfaces`
   v1 output for the same paths (run both commands in the test).
4. Fixtures with exact expected sets:
   - the #743 scenario: a fixture surface with production sources and
     adjacent test files — changed production file → hit; changed
     `*_test.go` → excluded by `role != test`; a doc-role path matched by
     a raw trigger glob → still a hit (exclusion contract, not
     production-selection); an unclassifiable path → `unestablished`
     (exit 3), never silently non-production;
   - a Go-shaped tree (`x.go`, `x_test.go`, `testdata/`) — path shapes
     only, no Go toolchain;
   - deletion/rename: two `--file-list` inventories over one fixture
     tree; the expected files assert `absent-from-snapshot` presence and
     stable output across the two runs.
5. Whole-repo run to report (not assert): `classify` over every tracked
   path (feed via `--file-list` of the inventory itself) — report the
   role census and the count of unestablished paths by top-level
   directory (this becomes the parent's pre-declared-list census).
6. `cargo test/fmt/clippy -D warnings/build --release` green.

## Boundaries

Only `native/**`. No carrier/invokes work, no components/explain, no
analyzer parsing. Frozen v1 ABIs unchanged (classify reuses the matcher,
does not modify it); usage string + ABI.md updated together if the
dispatch list line changes. Digest-ish fixture values non-hex-looking; no
`key`/`token`/`secret` member names.

## Stop condition and result shape

One coherent commit, prefix `topo(746):`. Final message: what was built,
commands + observed results including the whole-repo classify census,
deviations with reasons.
