## Parent

#744

## Situation

`charness` carried a prebuilt-artifact distribution layer built for exactly one
binary, `repograph`: download, checksum, staging, extraction, atomic activation,
a `current` pointer, version pruning, rollback, and twelve phase statuses
projected into `charness doctor`. Roughly 1,900 lines of production and test
code, plus a `native_core` block in `packaging/charness.json` and three schema
definitions in `packaging/plugin.schema.json`.

That binary's source ships in the same git repository the layer lives in
(`git ls-files native/` → 207 files), and the managed consumer checkout at
`~/.agents/src/charness` is a full clone. Any consumer that has run
`charness update` already holds the source.

Meanwhile `charness` already owned an external-tool control plane:
`integrations/tools/*.json` with `lifecycle.install.commands`, `checks.detect` /
`checks.healthcheck`, `doctor_policy`, and `degradation.when_missing`, surfaced
by `charness tool doctor <id>` and `charness tool install <id>`. Three of its
tools — `awiki`, `lychee`, `tokei` — already install through `cargo install`.

## Experience

The layer's central value was detecting skew between the binary and the source
it was built from: `stale`, `incompatible`, `source_drift`. Building from the
checkout that runs the gates makes those states **structurally impossible**
rather than detectable after the fact — it is definitionally the same commit.
Digest-matching a downloaded artifact only imitates that invariant.

Nothing was ever published through the layer: no `v8.0.0` tag, no GitHub
release, and `asset_names` was always empty.

## Impact

Retiring it removes the archive-reproducibility follow-up (gzip mtime in
`_write_archive`), the `artifact.json` asset-name collision across tuples,
`host_tuple()`'s non-Rust triples (`arm64-unknown-darwin` vs the real
`aarch64-apple-darwin`), the `OSError`/`RuntimeEnvironmentError` mismatch in
`build_native_artifact.py:91-94`, and `corrupt` as an imprecise token for
`state-write-skipped` / `activation-failed`. None of those needed a fix; they
needed the layer to stop existing.

## Desired capability

`repograph` is declared and installed like every other external binary this repo
depends on, and gate resolution prefers the source you are actually editing.

## What was done

- Deleted `scripts/native_core_lib.py`, `scripts/native_core_resolution_lib.py`,
  `scripts/build_native_artifact.py`, `scripts/check_native_release_asset.py`,
  `skills/public/release/scripts/publish_release_native_artifact.py`, the
  `release_upload` / `release_assets` ops, the release attach step in
  `publish_release_resume_publish.py`, `runtime_bootstrap.native_core_path`, the
  `native_core` key across every `charness` doctor/init/update payload, the
  `native_core` declaration in `packaging/charness.json`, and the `nativeCore`
  definitions in `packaging/plugin.schema.json`.
- Added `integrations/tools/repograph.json`: `doctor_policy: required`, install
  by `cargo install --path .` from the crate in the charness checkout,
  `degradation.when_missing` naming the two BLOCKING gates that have no fallback
  engine.
- Rewrote `scripts/native_gate_lib.py` as the single resolver:
  `CHARNESS_NATIVE_CORE` override → this checkout's
  `native/repograph/target/release/repograph` → the installed binary. Dev-tree
  precedes installed so an edited crate answers the gate instead of a binary
  built from other source. When the crate is present but unbuilt or older than
  its source, the resolver builds it and announces what it is doing, from where,
  and why, on stderr before starting. A failed build is an error, never a
  fallthrough to a binary compiled from different source.

## Three traps worth recording

1. `cargo install --path <crate>` run from elsewhere ignores the crate's
   `rust-toolchain.toml`, because rustup selects the toolchain from the working
   directory. On this host `cargo --version` is `1.93.0` in `/tmp` and `1.96.0`
   inside `native/repograph`, and the crate requires `1.96`. The install command
   must `cd` into the crate first.
2. `install_provenance_lib.detect_binary_name` derives `provenance.binary_name`
   from `shlex.split(checks.detect.commands[0])[0]`. A `PATH=... repograph`
   prefix in `detect` made `charness tool doctor` report
   `binary_name: PATH=${CARGO_HOME:-$HOME/.cargo}/bin:$PATH`. Found by running
   the doctor, not by reading the manifest.
3. Declaring `package_managers.cargo.package_name: "repograph"` looked right and
   was dangerous: `install_provenance_lib.package_manager_update_action` turns it
   into `cargo install repograph --force`, which resolves against **crates.io**.
   This crate is not published there, so the derived update could reach an
   unrelated package of the same name. The block carried a note saying it must
   not be installed by name; nothing reads the note, and the derivation reads the
   block. The block is gone and `lifecycle.update.mode` is `manual` --
   `charness tool install repograph` is the rebuild path.

## Links

- Spec: `charness-artifacts/spec/repograph-tool-control-plane.md`
- Plan: `charness-artifacts/design-studies/2026-08-30-next-session-plan.md`
- Debug artifact that started it:
  `charness-artifacts/debug/2026-08-29-native-artifact-sidecar.md`
- Supersedes the shipped-capability claim in #747 and reverses #744 step 3
  ("Ship a version-bound native artifact without requiring a Rust toolchain").
