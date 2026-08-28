# Issue #747 evidence record

> Date: 2026-08-28
> Plan: `../2026-08-28-issue-747-distribution-plan.md` (rev 2)
> Lanes: 747-install (F), 747-artifact (E) — Codex (`gpt-5.6-luna`,
> xhigh); parent applied the `.agents/release-adapter.yaml` wiring the
> sandbox blocked, synced the plugin export, and ran the gates.

## What shipped

- `scripts/native_core_lib.py` + `native_core_resolution_lib.py`: staged
  download → sha256/tuple/version verify → smoke → same-filesystem atomic
  activation under an `fcntl` lock, previous-version retention,
  re-activation-from-disk (the rollback contract), typed statuses
  (`not-distributed | awaiting-artifact | offline | missing | stale |
  corrupt | incompatible | unsupported-tuple | healthy`, plus
  `foreign-origin` refusal), `CHARNESS_NATIVE_ARTIFACT_STORE` fixture
  override.
- `native_core_path()` sum-type locator in `runtime_bootstrap.py`,
  re-exported through `skill_runtime_bootstrap.py` and both root shims;
  non-healthy variants carry no path; dev-tree resolution only under
  `CHARNESS_ALLOW_DEV_NATIVE_CORE=1`.
- `charness` wiring: init/update phase at the post-re-exec insertion
  point; doctor `native_core` block (with `source_drift`) in the DEFAULT
  response projection; next-action source; uninstall/reset remove the
  native state dir.
- `packaging/plugin.schema.json` `native_core` declaration schema — the
  single switch. No declaration exists on main, and the inertness of that
  state is test-pinned.
- `scripts/build_native_artifact.py` (SOURCE_ONLY, never exported) and
  `scripts/check_native_release_asset.py`; release-adapter
  `real_host_checklist` line requiring the asset readback and
  `native_core: healthy` (or the typed not-applicable states) after
  publish.

## Parent-executed verification (integrated tree)

- Lifecycle battery + existing managed-install suites: 32 + 9 focused
  tests green; the main-state inertness test passes; packaging validation
  and `validate_packaging_committed` green after the parent's export
  sync; docs gate PASS after one doc-links fix.
- `charness doctor` on this host reports the typed
  `native_core: not-distributed` block at the default response level.
- First real artifact build (proof of path, unpublished):
  `repograph-v8.0.0-x86_64-unknown-linux-gnu.tar.gz` built with the
  pinned 1.96.0 toolchain and `--locked`; digests recorded in
  `2026-08-28-first-native-artifact-build.md`.

## Deliberately not yet exercised (typed, not silent)

The live path — a published release carrying a `native_core` declaration,
the network staging in a consumer install, and the post-publish
`native_core: healthy` readback — waits for the next actual release; the
release-adapter checklist now carries that obligation, and until then
every consumer sees the typed `not-distributed` state. Closing #747
before or after that first switch-on release is an operator decision
recorded in the session log.

## Final integrated proof

Shares the #746 record's final battery: 78 passed, 0 failed at the
integrated head; lifecycle suites green; export mirror synced and
committed-tree validated.
