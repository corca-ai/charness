# Lane brief: 747-artifact (lane E)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-747-distribution-plan.md`
(rev 2), especially D2 (declaration switch — do NOT declare a native core
for any existing version; the switch stays off), D3 (artifact production,
no crate-version sync, no `--version` flag), D8 (release readback, no CI
cargo). Lane F already landed: `scripts/native_core_lib.py` /
`native_core_resolution_lib.py`, the inert init/update phase, the locator,
doctor states, and the `native_core` declaration schema in
`packaging/plugin.schema.json` + docs. Read those first and build on them;
do not restructure them. Do not spawn descendant agents.

## Outcome

1. `scripts/build_native_artifact.py`: reads the product version from
   `packaging/charness.json`; runs `cargo build --release --locked` in
   `native/repograph` under the pinned toolchain; packages
   `repograph-v<version>-<tuple>.tar.gz` containing the binary; writes
   `SHA256SUMS` and a sidecar `artifact.json` (product version, git tag +
   commit, tuple, rustc version, `Cargo.lock` digest) into an output
   directory given by `--out-dir` (default outside the repo via the
   runtime tmp root — never write artifacts into the repo tree). The
   script must be gitignore-aware per the python-scan-hygiene surface
   (it touches the ignored `target/`), and must not modify
   `native/repograph/Cargo.toml` (the crate version is not a version
   owner).
2. Register `build_native_artifact.py` in `SOURCE_ONLY_PLUGIN_SCRIPTS`
   (`scripts/packaging_lib.py`) so it never ships to consumers. Do NOT
   run the plugin export sync — the parent owns generated surfaces.
3. `scripts/check_native_release_asset.py` (repo-local, NOT in
   `skills/public/**`): given the repo root, reads the `native_core`
   declaration; if the checkout's version declares an artifact, asserts
   `repograph-v<version>-<tuple>.tar.gz` is present in the release's
   asset names (reuse the existing self-release probing idiom — see
   `probe_self_release` in the `charness` script and
   `CHARNESS_RELEASE_PROBE_FIXTURES`; support that fixture override so
   tests are offline). Undeclared version → typed pass
   (`not-applicable`). Wire it into `.agents/release-adapter.yaml`: one
   `real_host_checklist` line requiring `native_core: healthy` after the
   post-publish `charness update` (prose line), and add the check command
   where the adapter's existing verify/readback commands live. Do NOT
   touch `skills/public/release/**` (especially not `bump_version.py`).
4. Tests (pytest, offline): build script with a FAKED cargo (fake-binary
   fixture idiom from `tests/charness_cli/fixtures/fake_*.py`) — verifies
   tarball layout, SHA256SUMS correctness, artifact.json contents, and
   refusal when the git tree is dirty or version cannot be read;
   `check_native_release_asset.py` against fixture release payloads
   (declared+present → pass; declared+missing → fail; undeclared →
   not-applicable). CI has no cargo; no test may invoke the real cargo.
5. Real-build proof (best effort, report only): if `cargo` works in your
   sandbox (CARGO_HOME is pre-seeded in your environment), run the real
   script once with `--out-dir` under the task runtime tmp and report the
   produced names + digests. If the sandbox blocks it, say so — the
   recorded maintainer-host build is the production path.

## Boundaries

Scope: `scripts/**`, `packaging/**`, `tests/**`,
`.agents/release-adapter.yaml`, `docs/host-packaging.md` (extend the
existing native-core section with the artifact/build contract). Never
touch `plugins/**`, `native/**`, `skills/**`. Do not add a `native_core`
declaration for any version. Respect the 480-code-line cap for
`scripts/*.py`.

## Stop condition and result shape

Focused verification: the new pytest modules + `ruff check` on touched
files + `python3 scripts/validate_packaging.py --repo-root .`. One
coherent commit, prefix `dist(747):`. Final message: what was built,
commands + observed results, whether the real build ran (names +
digests), deviations with reasons.
