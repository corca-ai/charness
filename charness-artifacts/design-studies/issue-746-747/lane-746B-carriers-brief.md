# Lane brief: 746-carriers (lane B)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`
(rev 2), especially D2 (normative: program-position-only invokes, tier
table, typed opacity) and D8. Lane A landed the graph core (`graph_model`,
`graph_roles`, `graph_imports`, `graph_mirrors`, `graph`); build on it
additively. NOTE: a sibling lane (`746-classify`) is running concurrently
in its own worktree on the same crate — keep your changes additive: new
module(s) (suggest `graph_carriers.rs`), one dispatch arm in `lib.rs`,
fixtures under `native/repograph/fixtures/carriers/`, and minimal edits to
`graph.rs` (a builder hook, not a rewrite). Do not spawn descendant agents.

## Outcome

1. Carrier scanning per D2 tiers over: `.githooks/*`, `.github/workflows/*.yml`
   (inline `run:` single commands only; multi-line/expression steps are
   opaque), `package.json` scripts, `.agents/surfaces.json`
   sync/verify command strings, `integrations/tools/*.json` check commands,
   `scripts/run-quality.sh` (label extraction via the same source-regex
   contract `scripts/quality_label_universe.py` uses — read it first;
   bash-source part only, adapter `startup_probes` labels typed
   `unresolved (yaml)`).
2. `invokes` edges: ONLY the resolved program word (argv[0] after `env`
   prefixes, `KEY=VALUE`, interpreter flags; `python3 x.py`,
   `python3 -m pkg.mod`, `bash x.sh`, `./x`). Path-valued arguments →
   `carrier-path-reference` records, never invokes. Command-shaped strings
   inside `echo`/`printf` args or `-c` payloads → typed
   `unresolved-carrier`. Multi-statement/computed shell → typed
   `unresolved-carrier` with carrier identity + raw text.
3. `command-carrier` and `validation-command` nodes; root extraction per
   plan D1 root classes (validation entrypoints from hooks/CI/surfaces
   commands/gate plan labels; `charness` CLI and `init.sh` as product
   roots — they may already exist from lane A; extend, do not duplicate).
4. Fixtures with exact expected sets, including the two NAMED negative
   fixtures (D2/D8): a hook-style `echo "... run python3 scripts/x.py ..."`
   line and a `queue_selected "label" python3 "$VAR" ...` variable-target
   line — both asserted to produce NO invokes edge. Snake_case `.py`
   names; no `key`/`token`/`secret` JSON members.
5. A label-parity test: Rust-extracted run-quality labels (bash part)
   compared against `python3 scripts/quality_label_universe.py` output
   with the yaml-sourced labels accounted as a typed known gap (run the
   Python script to capture its output into a fixture expected file; do
   not import it at test time).
6. Whole-repo run to report (not assert): invokes edge count,
   unresolved-carrier count by tier, carrier-path-reference count, label
   count vs Python reader count.
7. `cargo test/fmt/clippy -D warnings/build --release` green (offline
   cache in CARGO_HOME; network may work).

## Boundaries

Only `native/**`. No YAML crate (D9). No classify/changed/components/
explain work. Frozen v1 ABIs unchanged; shared usage string + ABI.md
updated together if the dispatch list line changes.

## Stop condition and result shape

One coherent commit, prefix `topo(746):`. Final message: what was built,
commands + observed results including the whole-repo carrier census and
the label-parity outcome, deviations with reasons.
