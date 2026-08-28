# Native Artifact Sidecar Debug Review
Date: 2026-08-29

## Problem

The v8.0.0 switch-on release would publish an artifact no consumer can install.
`_prepare_activation` refuses with `artifact metadata sidecar is missing` for the
exact archive `build_native_artifact.py` produces. Every x86_64-linux consumer
running `charness update` would get a permanent state where the core never
activates and `doctor` reports the wrong status with remediation that is the
command that just failed.

## Correct Behavior

Given a published archive whose sha256 matches the `native_core` declaration,
when `charness update` runs, then the core activates and `doctor` reports
`native_core: healthy`.

## Observed Facts

- The archive has one member: `tar tzvf` → `4022112 repograph`.
  `build_native_artifact.py:148-153` adds only the binary; the sidecar is written
  *beside* the archive at `:200`.
- The attach step uploads only `preflight["path"]`
  (`publish_release_native_artifact.py:162-169`), so `artifact.json` is never a
  release asset, so the download at `native_core_lib.py:258` — gated on
  `"artifact.json" in assets` — never runs.
- Real artifact through the real release path: `{"status":
  "verification-failure", "reason": "artifact metadata sidecar is missing"}`.
- `native_core_resolution_lib.py:150` honors only `awaiting-artifact`/`offline`
  from `last-status.json`, so `verification-failure` is laundered into doctor
  `missing`, whose message is "run `charness update`".

## Reproduction

- Stub `_download_artifact` to serve the built archive from disk, call
  `run_native_core_phase` with a probe returning
  `{"status":"ok","latest_tag":"v8.0.0","asset_names":[<archive>]}`. Fails first
  run.

## Candidate Causes

- Producer omits a file the consumer requires (control flow).
- The consumer's requirement is vestigial and should not exist (contract).
- The attach step uploads too few assets (release machinery).
- Fixtures encode a shape the producer never emits (test double).

## Hypothesis

- Falsifiable claim: the sidecar contributes nothing, so deleting the refusal —
  not feeding it — yields a healthy install with complete installed metadata |
  disconfirmer: if any field the installer keeps originates in the sidecar,
  deleting the refusal must leave installed metadata incomplete.

## Verification

- Result: confirmed. Removing only `native_core_lib.py:285-286` gives
  `{"status": "activated"}`; installed `artifact.json` carries `version`,
  `tuple`, `artifact_sha256` (from the declaration) and `binary_sha256`,
  `binary_size`, `binary_mtime_ns` (recomputed from the binary) — every field
  `_verify_version_dir:126-136` reads. `native_core_doctor_payload` →
  `{"status": "healthy", "provenance": "managed", "source_drift": "in-sync"}`.
  Nothing kept came from the sidecar.

## Root Cause

The requirement is vestigial and self-cancelling. At
`native_core_lib.py:285-295` the only fields read from the sidecar (`version`,
`tuple`) are overwritten with the declaration's own values three lines later,
and the follow-up check at `:294` compares those just-assigned values against
their own sources — provably dead. The bytes were already bound to the
declaration by `sha256(archive) != expected["sha256"]` at `:274`.

Five whys: (1) archive lacks `artifact.json` and `:285` refuses; (2)
`_write_archive` adds only the binary; (3) no test caught it because
`test_native_core_install.py:50-52` builds its own archive with
`bundle.add(metadata, arcname="artifact.json")` — a shape the producer never
emits; (4) consumer and fixture landed together in `b3a244947 "add inert native
core install lifecycle"` while the producer landed in `b6d196f43`, unreconciled;
(5) the lifecycle was deliberately **inert**, so producer→consumer never ran
end-to-end and "inert" was never converted into a reconciliation obligation
before the first real publish. Bottom (missing invariant + missing gate): no
owner of the artifact-shape contract, and no gate asserting the builder's bytes
are the bytes the installer accepts.

## Invariant Proof

- Invariant: the byte stream `build_native_artifact.py` emits must activate
  through `run_native_core_phase` unchanged.
- Producer Proof: the builder's own tests pass on output the installer rejects.
- Final-Consumer Proof: only the roundtrip above establishes it; it failed
  as-is and passed with the refusal removed.
- Interface-Shape Sibling Scan: this session's fake `gh`
  (`fixtures/release_publish_fake_gh.py:24-48`) claimed `release view` by argv
  length and broke `release_view_body`'s real argv — same producer/consumer
  shape, found only by running real argv. Fixed in `7cc3a24ec`.
- Non-Claims: no claim about non-linux tuples; no claim that the roundtrip gate
  exists yet.

## Detection Gap

- `check_native_release_asset.py:86-94,114-124` | checks only the asset *name*,
  never its contents | run the real builder output through
  `run_native_core_phase` with a release-shaped probe.
- `test_native_core_install.py` | supplies its own archive, and the local-store
  path (`native_core_lib.py:234-239`) copies the sidecar from the build dir, so
  all #747 build/install evidence passes while the download path fails | same
  roundtrip gate.

## Sibling Search

- Mental model: **a test double written from the consumer's expectation, so the
  pair validates itself and the real producer never enters the loop.** Third
  instance: the P5 classify fake accepted `--path a b c` the real binary rejects
  (`charness-artifacts/retro/2026-08-29-session-retro.md:52-55`). None of the
  three was caught by its own suite.
- abstraction up: `_publish_and_finalize` (`publish_release_execute.py:225`) is
  unreachable in production with three test-only callers — the suite keeping
  dead production code alive | decision: valid follow-up outside the slice |
  proof: static caller scan | `follow-up: release-machinery-jtbd-audit`
- specialization down: lane fixtures assuming `CHARNESS_RUNTIME_ROOT` is honored
  where `runtime_bootstrap.py:83` ignores it | decision: same class, fixed in
  `7cc3a24ec` | proof: executable fixture
- cross-file: `tests/quality_gates/fixtures/release_publish_fake_gh.py` and
  `tests/charness_cli/test_native_core_install.py` — both outside
  `native_core_lib.py`
- mental-model siblings: every repo fake standing in for an external binary
  (`gh`, `repograph`, `nose`) | decision: same class, diagnostic-only |
  proof: static scan | `follow-up: seam-fake-real-argv-audit`

## Seam Risk

- Interrupt ID: native-artifact-sidecar-2026-08-29
- Risk Class: external-seam
- Seam: locally-built artifact meeting a GitHub-hosted download path no local
  test traverses
- Disproving Observation: the real artifact through the real installer returned
  `verification-failure` while every producer-side and consumer-side test was
  green
- What Local Reasoning Cannot Prove: that the emitted bytes satisfy the
  installer; only the roundtrip can
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/native-artifact-roundtrip.md

## Prevention

Delete the vestigial refusal and its dead follow-up
(`native_core_lib.py:285-286, 294-295`), keeping the sidecar *download* branch at
`:258` that the local-store path legitimately uses. Add the roundtrip gate named
in Detection Gap — the invariant's only honest owner. Generalize the
seam-fake rule already added to `.agents/lane-brief-template.md` this session
to: a double's accepted shape must be derived from the real producer, never from
the consumer's expectation.
