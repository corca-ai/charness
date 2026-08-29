# Spec — Retire the native-core distribution layer; repograph joins the tool control plane

Date: 2026-08-30

Supersedes the acquisition half of
`charness-artifacts/spec/native-artifact-roundtrip.md` (D1/D2 remain true
statements about a layer that is being removed; they stop being live contracts).

Inputs: `charness-artifacts/design-studies/2026-08-30-next-session-plan.md`
(Step 1), `charness-artifacts/debug/2026-08-29-native-artifact-sidecar.md`,
`2026-08-28-issue-747-distribution-plan.md`.

Operator decisions taken 2026-08-30 (recorded verbatim in "Decisions" below).

## Problem

`charness` builds a parallel distribution lifecycle — download, checksum, stage,
extract, atomically activate, maintain a `current` pointer, prune versions,
roll back, and project twelve phase statuses into a doctor payload — for exactly
one binary: `repograph`. That binary's source ships in the same git repository
that carries the lifecycle (`git ls-files native/` → 207 files), and the managed
consumer checkout at `~/.agents/src/charness` is a full clone, so any consumer
that has run `charness update` already holds the source.

Meanwhile `charness` already owns an external-tool control plane:
`integrations/tools/*.json` declares 15 tools with `lifecycle.install.commands`,
`checks.detect`/`checks.healthcheck`, `doctor_policy`, and
`degradation.when_missing`, surfaced through `charness tool doctor <id>` and
`charness tool install <id>`. Three of those tools — `awiki`, `lychee`, `tokei`
— already install through `cargo install`. A missing toolchain is something this
repo installs; it is not something to design a distribution lifecycle around.

The redundancy is not merely stylistic. Building from the checkout you are
running makes `stale`, `incompatible`, and `source_drift` structurally
impossible: it is definitionally the same commit. Digest-matching a downloaded
artifact only imitates that invariant after the fact, and the 2026-08-29 session
paid three separate times for verifier logic that demanded values nothing
consumed.

## What the binary is actually for

`repograph` is NOT optional decoration. It has four live production consumers:

| Consumer | Site | Severity |
| --- | --- | --- |
| `check-export-safe-imports` | `scripts/run-quality.sh:1092` | blocking |
| `check-plugin-dir-references` | `scripts/run-quality.sh:1121` | blocking |
| `check_standalone_imports.py` | `scripts/check_standalone_imports.py:177` | blocking |
| release real-host test exclusion | `skills/public/release/scripts/check_real_host_proof.py:171` | typed degradation |

All four reach the binary through one resolver, `scripts/native_gate_lib.py`.
That resolver is the only surviving consumer of the retired layer and is where
the replacement lands.

## Decisions

### D1. Tool identity: `repograph`, with cargo as a prerequisite

One manifest, `integrations/tools/repograph.json`, `kind: external_binary`.
The declared tool is the thing the gates actually need. Declaring `cargo` or
`rustup` instead would make `charness tool doctor` report "a toolchain is
present" while saying nothing about whether the gate can run.

Rejected: a second `cargo` manifest. The install command's own cargo-absent
branch already emits the rustup guidance, and a second doctor line for a
prerequisite that only this one tool needs adds a surface without adding an
answer.

### D2. The binary lands on PATH via `cargo install --path`

`cargo install --path <crate> --locked --force` → `~/.cargo/bin/repograph`.
This is the exact shape `awiki`, `lychee`, and `tokei` already use, and it
deletes staging, atomic activation, the `current` pointer, version pruning, and
rollback outright rather than relocating them.

`--force` is required, not defensive: the crate is pinned at `version = "0.1.0"`
and does not bump per commit, so cargo would otherwise refuse every reinstall as
already-present. `--locked` is required because `Cargo.lock` ships and the gate
verdict must not depend on dependency resolution drift.

The install command must `cd` into the crate directory before
`cargo install --path .`, not install from elsewhere with `--path <crate>`.
Rustup selects the toolchain from the WORKING DIRECTORY, so installing from
outside the crate ignores `native/repograph/rust-toolchain.toml`. Proven live on
this host: `cargo --version` is `1.93.0` in `/tmp` and `1.96.0` inside
`native/repograph`, while the crate declares `rust-version = "1.96"` — the
`--path`-from-elsewhere form would fail the build outright.

The install command must find the crate from a cwd that is the SUBJECT repo, not
the provider. It searches, in order, the current repo (authoring case) then the
managed checkout (consumer case), and prints which one it chose:

```
$PWD/native/repograph
${CHARNESS_SRC:-$HOME/.agents/src/charness}/native/repograph
```

If neither exists, it fails with `charness update` as the next step — a consumer
without the managed checkout has no source to build from, and saying so is more
useful than a cargo error about a missing path.

### D3. Resolution order: override → dev-tree → PATH

`native_gate_lib.resolve_native_core` becomes the single resolver, with no
dependency on `runtime_bootstrap` or the retired locator:

1. `CHARNESS_NATIVE_CORE` — provenance `override`. A missing file is an error,
   not a fallthrough: an explicit override that silently degrades is worse than
   no override.
2. `<repo_root>/native/repograph/target/release/repograph` when
   `<repo_root>/native/repograph/Cargo.toml` exists — provenance `dev-tree`.
3. `shutil.which("repograph")` — provenance `installed`.
4. Otherwise `NativeGateError` naming `charness tool install repograph`.

Dev-tree precedes PATH so that editing the crate in the authoring checkout is
immediately reflected in the gate verdict. The inverse order would let a stale
`~/.cargo/bin/repograph` render a verdict on source it was not built from, which
is the same class of dishonesty this whole retirement is removing. In a consumer
repo there is no `native/`, so step 2 does not apply and step 3 is reached
naturally.

### D4. Crate present but unbuilt: build it, and say so

When step 2 finds `Cargo.toml` but no `target/release/repograph`, the resolver
runs `cargo build --release --locked` in the crate root rather than failing or
falling through to PATH — and announces on stderr, before starting, what it is
building, from where, and why:

```
native gate: repograph is not built at <crate>/target/release/repograph
native gate: building from source (cargo build --release --locked in <crate>)
native gate: this is a first-build cost; subsequent gate runs reuse the binary
```

On success it announces the elapsed time and proceeds. On failure it raises
`NativeGateError` carrying cargo's stderr — it does NOT fall through to PATH,
because falling through is precisely the silent substitution the announcement
exists to prevent.

The operator decision that produced this: auto-build is correct **provided it is
explicit**, and that transparency requirement generalizes — anywhere this design
acts on the operator's behalf, the action is announced rather than inferred from
its effect. Applied consequences elsewhere in this spec: D5 (provenance is
printed on every gate run, not only under `--probe`) and D8 (the retired state
directory is removed visibly rather than left as silent residue).

`cargo` absent at this point is a hard `NativeGateError` naming the rustup
install path — consistent with D6.

### D5. Provenance is always visible

Today `native_gate_lib` prints the resolved path and provenance only under
`--probe`. Under D4 the resolver can now silently spend minutes, and under D3 it
can now pick between three sources whose verdicts can differ. Therefore every
invocation prints one stderr line before executing:

```
native gate: repograph <path> (provenance: dev-tree)
```

stderr, not stdout: `export-safe` and `plugin-refs` emit JSON on stdout that
downstream gates parse.

### D6. `doctor_policy: required`, gates fail closed

`repograph.json` declares `doctor_policy: required` and
`degradation.when_missing` in the same shape `nose` uses. Two of the four
consumers are already BLOCKING gates with no fallback path, and
`integrations/tools/README.md` permits `advisory` only where the consuming
workflow has a degraded path. A missing `repograph` must therefore report
`doctor_disposition: blocking-install-needed` and exit non-zero.

The typed-degradation contract from #748 D8 survives unchanged; only its cause
changes — from "the artifact is not published for your tuple" to "the binary is
not installed, here is the one command that installs it".

`detect` and the gate resolver must agree about reachability, which forces a
detail: `cargo install` writes to `${CARGO_HOME:-$HOME/.cargo}/bin`, and the
invoking process's PATH may predate that write. Both sides therefore fall back
to that directory. `detect`'s command must nonetheless START with the bare
binary name, because `install_provenance_lib.detect_binary_name`
(`scripts/install_provenance_lib.py:31-42`) derives `provenance.binary_name`
from `shlex.split(checks.detect.commands[0])[0]`; a `PATH=... repograph` prefix
made the doctor payload report `binary_name: PATH=${CARGO_HOME:-$HOME/.cargo}/bin:$PATH`.
Found by running the doctor, not by reading it.

### D7. Installation is explicit; `init`/`update` no longer acquire

`run_native_core_phase` is removed from `charness init` and `charness update`.
Consumers learn they need `repograph` the same way they learn they need `nose`:
`charness tool doctor repograph` reports `blocking-install-needed` with an
actionable `next_step`, and `charness tool install repograph` satisfies it.

This is deliberate, not an omission. Making `charness update` build a Rust
release binary would make every update — including updates by consumers who
never run the two gates that need it — depend on a cargo toolchain and take
minutes. `nose` is `required` and is not auto-installed either; this is the
established shape.

### D8. `native_core` leaves the doctor payload

The `native_core` key is removed from `charness doctor` / `init` / `update`
payloads, from `host_next_steps`, from `build_doctor_next_action`, and from
`project_runtime_response`. `repograph` health is reported where the other 15
tools report theirs: `charness tool doctor repograph`. Nothing was ever
published carrying this key (no `v8.0.0` tag, no GitHub release), so there is no
compatibility obligation.

`charness uninstall`'s removal of `<state_root>/native` is KEPT, with a comment
naming it as residue of the retired layer. Deleting the cleanup alongside the
writer would leave maintainer machines holding a directory nothing will ever
mention again — silent residue, which D4's transparency requirement rejects.
The cleanup is self-terminating: once the directory is gone it is a no-op.

## What comes out

Deleted outright:

- `scripts/native_core_lib.py` (485 lines) — download, checksum, staging,
  extraction, atomic activation, `current` pointer, pruning, rollback,
  `PHASE_STATUSES`.
- `scripts/native_core_resolution_lib.py` (311) — the declaration read,
  `supported_tuples`, `artifact_declaration`, `host_tuple`, and every
  `NativeStatus` member. With D3 and D8 it has no surviving consumer.
- `scripts/build_native_artifact.py` (220), `scripts/check_native_release_asset.py` (150).
- `skills/public/release/scripts/publish_release_native_artifact.py` (215) and
  the `release_upload` / `release_assets` ops in `publish_release_helpers.py`
  (built 2026-08-29, never used for a published release).
- Tests: `tests/charness_cli/test_native_core_install.py` (534),
  `tests/test_build_native_artifact.py`, `tests/test_check_native_release_asset.py`,
  `tests/quality_gates/test_release_native_artifact.py`.
- `runtime_bootstrap.native_core_path` and its re-exports in
  `runtime_bootstrap.py` / `skill_runtime_bootstrap.py` (repo root and
  `scripts/`).
- `native_core` in `packaging/charness.json`; `native_core` plus the
  `nativeCore` / `nativeCoreVersion` / `nativeCoreArtifact` definitions in
  `packaging/plugin.schema.json`.
- `real_host_checklist` item 1 in `.agents/release-adapter.yaml`, replaced by a
  `repograph` tool-doctor item in the `nose` shape.
- The `scripts/native_core_lib.py` and `scripts/native_core_resolution_lib.py`
  entries in `skills/public/quality/references/attention-state-visibility.json`.

Consumers found only by grepping for the deleted names, each of which would
otherwise have dangled:

- `scripts/packaging_lib.py:43-44` — `build_native_artifact.py` and
  `check_native_release_asset.py` in `SOURCE_ONLY_PLUGIN_SCRIPTS`.
- `skills/public/release/scripts/publish_release_cli.py:33,57-60,130-133` — the
  module load and four re-exports.
- `skills/public/release/scripts/publish_release_resume_publish.py:128,185,203-211,220,222-226`
  — two preflight calls, the upload inside `publish()`, and the whole
  `upload_failure` arm. `publish()`'s return tuple loses its third member and
  `release_verified` loses its `upload_failure is None` conjunct.
- `tests/quality_gates/test_release_resume_edge_coverage.py` — the
  `_NATIVE_NOT_APPLICABLE` fixture, three stub methods, the `upload_failure`
  constructor/helper parameter, and
  `test_a_failed_native_upload_commits_the_artifact_before_it_refuses`, whose
  subject no longer exists.
- `plugins/charness/` is a checked-in generated mirror; it is regenerated with
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`, NOT edited.

Open follow-ups that evaporate with the layer, and are closed by deletion rather
than by fix: archive reproducibility (gzip mtime in `_write_archive`), the
`artifact.json` asset-name collision across tuples, `host_tuple()`'s non-Rust
triples (`arm64-unknown-darwin` vs `aarch64-apple-darwin`),
`build_native_artifact.py:91-94` catching `OSError` where `runtime_root` raises
`RuntimeEnvironmentError`, and `corrupt` as an imprecise token for
`state-write-skipped` / `activation-failed`.

## Deliberately NOT in scope

- `test_exclusion.native_core` in `check_real_host_proof.py` and the
  release adapter contract keeps its name. It denotes the resolved native
  BINARY, which still exists; renaming it would ripple through
  `adapter-contract.md`, `real-host-proof.md`, and their tests to relabel a
  thing that did not change.
- The halted v8.0.0 release (plan Step 2). Publishing is a separate decision
  taken after this lands, and the `native_core` declaration removal here is
  exactly what unblocks a plain release.
- Plan Steps 3–5.

## Success criteria

1. `grep -rn "native_core_lib\|native_core_resolution_lib\|build_native_artifact\|check_native_release_asset\|publish_release_native_artifact"` returns no production or test hits outside `charness-artifacts/`.
2. `charness doctor --detail` emits no `native_core` key and exits 0.
3. `charness tool doctor repograph --no-write-locks` with the binary absent from
   PATH and no dev-tree build reports `doctor_disposition: blocking-install-needed`
   and exits 1.
4. `charness tool install repograph --dry-run --detail` prints the crate-search
   install command.
5. `charness tool install repograph` produces `~/.cargo/bin/repograph`, after
   which detect and healthcheck pass.
6. With `native/repograph/target/release/repograph` removed, one gate run
   rebuilds it, printing the D4 announcement, and then succeeds.
7. With `CHARNESS_NATIVE_CORE` unset, no dev-tree, and `repograph` on PATH,
   `check-export-safe-imports` and `check-plugin-dir-references` pass and print
   `provenance: installed`.
8. `python3 scripts/validate_integrations.py` and
   `python3 scripts/validate_packaging.py` pass with the new manifest and the
   removed declaration.
9. Full battery green.
