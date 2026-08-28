# Lane brief: 748-seam-export-safe (lane S1)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decisions D1 (the native-binary seam — normative, including
the PROBE-VERIFIED fact that `native_core_path()` returns
`not-distributed` on main before its dev-tree branch can run), D2
(export-safe migration), D9 (test seam), D10 (catalog/reference
consequences), and `native/repograph/ABI.md` (`export-safe` contract;
the wrapper rule: exit 3 blocks, exit 70 is never remapped). A sibling
Rust lane runs concurrently but touches only `native/**`; do not touch
`native/**` source (building it read-only for verification is fine).
Do not spawn descendant agents.

## Outcome

1. New `scripts/native_gate_lib.py` — the ONE shared gate-side
   resolver and runner for the repograph binary:
   - Resolution order: (1) `CHARNESS_NATIVE_CORE` env override (file
     must exist); (2) a HEALTHY managed result from
     `runtime_bootstrap.native_core_path()`; (3) the dev-tree build
     `<repo>/native/repograph/target/release/repograph` whenever the
     crate SOURCE tree (`native/repograph/Cargo.toml`) exists —
     first-class `dev-tree` provenance for gate execution, with NO
     env-var gate; (4) typed failure.
   - Failure is loud (exit 1) with context-typed remediation: crate
     source present but binary missing → name the exact
     `cargo build --release` command and directory; no `native/` crate
     source (exported/consumer checkout) → say the native core is not
     yet distributed and name `charness update` — never a cargo
     instruction in a tree that cannot run it.
   - The docstring states this is a GATE-EXECUTION policy layered on
     top of the product resolver; `native_core_path()` and
     `CHARNESS_ALLOW_DEV_NATIVE_CORE` semantics are NOT modified.
   - CLI entry: `python3 scripts/native_gate_lib.py [--repo-root PATH]
     [--probe] <repograph-command> [args...]`. `--probe` resolves and
     reports without running. Otherwise exec/subprocess the resolved
     binary with the given args, streaming stdout/stderr through, and
     EXIT WITH THE BINARY'S EXIT CODE UNCHANGED (70 stays 70; 3 stays
     3; never remap).
2. `scripts/run-quality.sh`:
   - a single preflight before queueing: when any selected label is in
     a new `NATIVE_GATE_LABELS` list, run the `--probe` once and fail
     fast with its message. Keep the label lines plain double-quoted
     literals (the label-universe parser requirement).
   - rewire `check-export-safe-imports` (line ~1076) to
     `python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT"
     export-safe --repo-root "$REPO_ROOT"` (exact arg shape yours; the
     label name must not change and must stay OFF
     `UNESTABLISHED_CAPABLE_LABELS`).
3. Delete `scripts/check_export_safe_imports.py`. Contract deltas
   (report-all, zero-scope exit 3, non-parsed exit 3) are ratified —
   do not preserve first-violation/exit-1 behavior anywhere.
4. CI (`.github/workflows/quality-core.yml`): add ONE provisioning
   step before the gate steps — `cargo build --release --locked` in
   `native/repograph`, with `actions/cache` on `~/.cargo` and
   `native/repograph/target` keyed on `Cargo.lock` +
   `rust-toolchain.toml`. Provisioning only: do NOT add `cargo test`
   here (it would falsify the `local-gate-subset-mirror` marker).
   Add `cargo test --release` (same cache) to
   `.github/workflows/mutation-tests.yml` (the `scheduled-deeper-check`
   home). Run `python3 scripts/check_github_actions.py --repo-root .`
   after editing workflows.
5. Tests (`tests/quality_gates/**` unless named):
   - DELETE `test_export_safe_asset_paths.py` (AST helpers die with
     the algorithm; detection is crate-fixture-owned).
   - Update `test_shared_script_gate_scope.py`,
     `test_empty_scope_refusals.py` (remove the deleted module from
     `_MODULES`/scope pins; the zero-scope refusal for this family is
     now the native exit-3 contract), and `support.py` stub tuples so
     `test_quality_runner.py`'s queued-gate enumeration passes with
     the new command shape.
   - NEW behavioral tests for `native_gate_lib`: resolution order
     (override beats managed beats dev-tree; dev-tree used when source
     exists), context-typed remediation for both failure shapes, exit
     passthrough for 0/1/3/70 using a FAKE binary injected via
     `CHARNESS_NATIVE_CORE` that emits canned
     `repograph.export_safe.v1` documents (the schema is the seam —
     per D9, no compiled binary in these tests).
6. Reference sweep: remove the `scripts/check_export_safe_imports.py`
   entry from
   `skills/public/quality/references/consumer-validator-catalog.yaml`;
   update the companion-gate comments in
   `scripts/check_plugin_import_smoke.py` and
   `scripts/export_self_sufficiency_lib.py` that name the deleted
   file.

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`scripts/native_gate_lib.py`, `scripts/run-quality.sh`,
`scripts/check_export_safe_imports.py`,
`scripts/check_plugin_import_smoke.py`,
`scripts/export_self_sufficiency_lib.py`,
`.github/workflows/quality-core.yml`,
`.github/workflows/mutation-tests.yml`, `tests/quality_gates/`,
`skills/public/quality/references/consumer-validator-catalog.yaml`.
Out of scope: `plugins/**` (the parent runs the canonical export
sync), `native/**` source (build-only), `.agents/**`, other gates'
labels, `check-plugin-dir-references` (a later lane owns it). Frozen
ABI v1 unchanged. Generated surfaces are not hand-edited.

## Verification

Canonical runners only:
- `python3 scripts/run_standing_pytest.py tests/quality_gates` (the
  standing pytest runner — not ad hoc pytest);
- build the real binary once (`cargo build --release` in
  `native/repograph`) and run
  `CHARNESS_QUALITY_LABELS=check-export-safe-imports
  ./scripts/run-quality.sh` to smoke the rewired label end-to-end,
  plus one `--probe` run with the binary removed from resolution
  (unset override, point repo-root at a copy without the crate) to see
  the not-yet-distributed message;
- `python3 scripts/check_github_actions.py --repo-root .`.
The parent runs the FULL battery after integration; lane self-report
is not integration proof.

## Stop condition and result shape

One coherent commit, prefix `migrate(748):`. Final message: what was
built, commands run with observed results (including the smoked label
run and both failure-shape messages), and every deviation from this
brief with its reason. Stop at the stated outcome; do not widen into
other family scripts.
