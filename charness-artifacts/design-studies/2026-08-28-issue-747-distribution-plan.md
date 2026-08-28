# Issue #747 plan: version-bound native core distribution

> Status: rev 2 (post-critique; two opus reviews applied — lifecycle
> correctness, operability/blast-radius; three blockers resolved by design
> change, not wording)
> Date: 2026-08-28
> Parent: #744; depends on the ratified #745 spike (executable `repograph`,
> ABI v1, pinned toolchain + `Cargo.lock`)
> Investigation records: `issue-746-747/` (install lifecycle, release
> evidence)
> Critique records: `../critique/2026-08-28-issue-747-plan-{contract,scope}.md`

## Objective

Ship one version-bound `repograph` binary through the managed
`charness init/update` lifecycle — staged, checksum-verified, atomically
activated, offline-typed, doctor-legible — without Rust on consumer
machines and without a second version owner.

## Decisions

### D1. Supported matrix: evidence only

`x86_64-unknown-linux-gnu` only (sole tuple with recorded evidence). Other
tuples are typed `unsupported-tuple` for the native core; the Python
surface is unaffected. The matrix lives in the D3 declaration and expands
only on real install evidence.

### D2. The declaration switch (governs everything)

`packaging/charness.json` gains a `native_core` object: supported tuples
and, per released version, the expected artifact name + sha256. This
declaration is THE switch:

- Undeclared for the checkout's version → the entire native phase is
  inert: no network, no state writes, doctor reports typed
  `not-distributed`. Existing managed-install tests (which run a real
  seeded `charness init`) therefore stay network-free with no fixture
  plumbing; lane F can land fully before any artifact exists.
- Declared → init/update runs the staged lifecycle (D5) and the release
  readback asserts the artifact exists (D8).

This also bounds the maintainer-machine dependency: a release from a
machine without cargo publishes honestly with `native_core` undeclared for
that version (typed `not-distributed`), never a silently incomplete
release.

### D3. Artifact production and one version truth

`scripts/build_native_artifact.py` (source-only: added to
`SOURCE_ONLY_PLUGIN_SCRIPTS` so it never ships to consumers;
gitignore-aware per the scan-hygiene surface since it touches the ignored
`target/`): runs `cargo build --release --locked` under the pinned
toolchain, packages `repograph-v<version>-<tuple>.tar.gz` +
`SHA256SUMS` + a sidecar `artifact.json` (product version read from
`packaging/charness.json`, git tag + commit, tuple, rustc version,
`Cargo.lock` digest). The crate's own `Cargo.toml` version is NOT synced
and is not a version owner — this removes the `--locked`-vs-bump conflict
and any portable-skill (`bump_version.py`) edit entirely. Upload via the
existing `gh release upload` path. Reproducibility claim: pinned-toolchain
`--locked` rebuild discipline with recorded digests (bit-for-bit is a
non-claim). No `repograph --version` flag: the frozen ABI types unknown
options as usage errors, and the digest chain already binds
binary → version; the smoke check uses `parse-corpus --help`. #747
therefore touches nothing under `native/**`.

### D4. Install layout: versioned dir + atomic pointer, same filesystem

Under the state root (resolved ONLY via `default_state_root(home_root)` —
honoring `CHARNESS_STATE_HOME`; a resolved native root escaping an
explicitly-passed home root is refused, following the runtime-root
precedent):

```text
<state_root>/native/
  staging/<version>-<tuple>/    # inside the state root: os.replace is
  versions/<version>-<tuple>/   # same-filesystem by construction
  current                       # atomic JSON pointer
```

Downloads stage into `staging/` (NOT the tmpfs-backed runtime TMPDIR — a
cross-device rename would be non-atomic). The `current` pointer is written
with the existing `current_pointer_writer_lib.py` idiom (temp file +
`os.replace`); no third pointer-writer implementation. The whole
stage→verify→activate→prune sequence holds an exclusive `fcntl` lock on
`native/.lock` (existing repo idiom). Retention: exactly the previous
version; pruning runs only after a verified activation and never removes
the version named as the pointer's recorded predecessor. Read-only state
root degrades the same way `write_version_state` does (typed skip, no
crash).

### D5. Staged activation in init/update

Insertion point, named precisely: in both `cmd_init` and `cmd_update`,
after `install_surface` and after the re-exec boundary (the
`maybe_reexec_refreshed_cli` / `os.execv` calls), before
`build_doctor_payload` — so the phase runs once in the final process and
is idempotent if reached twice. Steps:

1. Read the D2 declaration for the checkout's version + host tuple.
   Undeclared → typed `not-distributed`, done. Unsupported tuple → typed
   `unsupported-tuple`, done.
2. Pointer already at this version with digest previously verified →
   typed no-op.
3. The wanted version already present under `versions/` and
   digest-verified → re-activate from disk, no network (this is also the
   rollback path: roll the checkout back, run `charness update`, the
   older core re-activates offline).
4. Otherwise resolve the artifact from the release of the checkout's
   version — artifact repo derived from the checkout's
   `git remote get-url origin`; a mismatch against the declaration's
   source is a typed `foreign-origin` refusal, never a silent upstream
   fetch. Release or asset absent → typed `awaiting-artifact`: the
   current release flow pushes the version-bearing branch before
   `gh release create`/upload, so every release has a window where
   consumers see version N with no artifact; remediation is "previous
   core stays active; artifact publishes shortly", NOT "run update".
   Offline → typed `offline`. Test/fixture override:
   `CHARNESS_NATIVE_ARTIFACT_STORE` points at a local directory store
   (mirroring the `CHARNESS_RELEASE_PROBE_FIXTURES` idiom); release
   probing reuses `probe_self_release()`/its asset_names rather than a
   third probe implementation.
5. Stage → verify (sha256 vs declaration, tuple, version, smoke:
   `repograph parse-corpus --help` exit 0) → move into `versions/` →
   atomically replace `current` (all under the D4 lock). Any failure
   leaves the prior `current` untouched with a typed status.

There is no `charness native rollback` command (a pointer-only rollback
would land in the `stale` state by definition — incoherent; step 3 is the
rollback contract). No new CLI subcommand exists, so no command-docs /
cli-reference / registry / side-effect-probe surfaces change.
`charness uninstall`/`reset` additionally remove `<state_root>/native/`
and report `removed_native_core`.

### D6. One locator, typed provenance, no silent dev builds

`native_core_path()` lives in `scripts/runtime_bootstrap.py` (lazy
imports — this module is on a measured 17ms startup budget) and is
re-exported through `skill_runtime_bootstrap.py` so BOTH bootstrap seams
reach it. It returns a sum type: `healthy(path, provenance, version)` or
`missing | corrupt | stale | incompatible | not-distributed` — non-healthy
variants carry NO path attribute, so a consumer cannot unwrap absence
into something executable (the "no silent native-claimed-complete"
acceptance is enforced by shape, not instruction; the consumer-side
reporting obligation moves to #748's acceptance). Resolution order:
`CHARNESS_NATIVE_CORE` override (provenance `override`, never reported
healthy by doctor), the `current` pointer (hot path checks recorded
size + mtime_ns; full digest only on mismatch → `corrupt`; full digest
verification happens at activation and in doctor), and — only when
`CHARNESS_ALLOW_DEV_NATIVE_CORE=1` — the dev-tree build (provenance
`dev-tree-build`, never healthy). Default on a source checkout without a
managed core is `missing`, same as any consumer. No binary is copied
under skill directories or the plugin tree; the export ships the locator
(runtime_bootstrap is already exported), not the artifact.

### D7. Doctor and response surfacing

Doctor resolves through the locator (never a parallel read) and reports:
`not-distributed | awaiting-artifact | offline | missing | stale |
corrupt | incompatible | unsupported-tuple | healthy`, each with exact
remediation, plus `provenance` and a `source_drift` field
(`in-sync | ahead-of-artifact`, comparing `artifact.json`'s commit with
the checkout HEAD). Counterweight to the review's "report stale when
ahead": between releases every checkout is ahead of the release artifact;
making that non-healthy is standing noise. `healthy` + explicit
`source_drift: ahead-of-artifact` keeps the claim honest without a false
alarm; #748 consumers read the field. The typed `native_core` block is
added to `project_runtime_response`'s allowlist with a compact projector
(so it appears WITHOUT `--detail`), and `build_doctor_next_action` gains a
`native_core` candidate source prioritized below host-delivery failures.

### D8. Release readback and checks

When the declaration names an artifact for the released version: the
existing post-publish readback asserts
`repograph-v<version>-<tuple>.tar.gz` ∈ `probe_self_release().asset_names`
and the `real_host_checklist` gains one line — `native_core: healthy`
after the post-publish `charness update`. No new gate, no CI Rust
toolchain: CI has no cargo, so build-script tests fake the cargo
invocation (fake-binary fixture idiom); real build proof is the recorded
maintainer-host artifact + digest. `Cargo.lock` remains outside the
supply-chain surface detector — recorded typed non-coverage decision
(follow-up issue candidate, not silently unclaimed).

### D9. Fixtures and tests

Lifecycle logic lives in a length-capped `scripts/native_core_lib.py`;
the uncapped `charness` script gets wiring and payload assembly only.
Pytest battery (local directory artifact store; `CHARNESS_STATE_HOME`
pinned in fixture env dicts so a developer's real `XDG_STATE_HOME` is
never touched): clean first install; already-current no-op; version
transition; unsupported tuple; checksum failure; interrupted activation
(staged, `current` never replaced → prior core active); re-activation
from disk after checkout rollback (offline); `awaiting-artifact`;
`offline`; `foreign-origin`; `not-distributed` (undeclared); skew
(pointer ≠ checkout version → `stale` with remediation); uninstall
removes `native/`. Existing managed-install tests must pass unchanged
with the phase present (inert by D2). These lifecycle tests are named
explicitly in the parent's per-lane verification — the standing closeout
gate excludes release-only install/update tests, so a green closeout
alone proves nothing here.

## Execution shape

Production surfaces → full discipline: lanes author; the parent alone
syncs the `plugins/` export, runs gates, and commits. Sequenced F → E
(reviewer-adopted): F lands fully inert (declaration absent — provably no
behavior change on main), E lands the build/upload machinery, and the
declaration switch turns on at the next release.

- Lane F `747-install`: `scripts/native_core_lib.py`, init/update phase,
  locator + both bootstrap seams, doctor states + projections +
  next-action source, uninstall cleanup, full fixture battery.
  Scope: `charness`, `scripts/**`, `tests/**`, `docs/host-packaging.md`,
  `packaging/**` (schema of the — still absent — declaration).
- Lane E `747-artifact`: `scripts/build_native_artifact.py` (+
  SOURCE_ONLY registration), `SHA256SUMS`/`artifact.json` format, release
  readback assertion + checklist line, declaration documentation.
  Scope: `scripts/**`, `packaging/**`, `tests/**`,
  `skills/public/release/**` (readback assertion only if it lives there —
  the lane must NOT edit `bump_version.py`).

No `native/**` changes anywhere in #747, so #746 lanes run fully in
parallel. Parent post-integration per lane: plugin export sync, gate
battery, the named lifecycle pytest set.

## Acceptance traceability

Matrix from evidence → D1; reproducible artifacts + checksums + metadata →
D3; one bound install identity readable by doctor → D2 declaration +
pointer + `artifact.json` (doctor reads all three); staged verify + atomic
activation, failure leaves prior core → D4/D5; rollback proven with
interrupted/invalid fixture → D5 step 3 + D9 fixtures; no Cargo for
consumers → D3 prebuilt + D6 dev-gate; one locator, no per-skill binaries
→ D6; typed offline behavior, no silent native-claimed-complete → D2/D6
(sum type); doctor distinguishes states + remediation → D7; export
references contract without second ownership → D3/D6; fixture coverage →
D9.

## Non-claims

- No validator or CLI migration (#748/#749); no consumer reads the
  locator's healthy path in #747.
- No matrix expansion; no native assets for unsupported hosts.
- No network during skill execution; fetch only in init/update.
- The Python surface is not a second analysis owner; absence is typed,
  never silently substituted.
- Bit-for-bit reproducibility not claimed; `Cargo.lock` supply-chain
  coverage not claimed (typed decision).
