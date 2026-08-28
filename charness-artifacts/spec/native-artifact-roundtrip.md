# Spec — Native Artifact Producer/Consumer Roundtrip

Date: 2026-08-29

Source: `charness-artifacts/debug/2026-08-29-native-artifact-sidecar.md`
(external-seam risk interrupt `native-artifact-sidecar-2026-08-29`).

## Problem

`build_native_artifact.py` and `native_core_lib.run_native_core_phase` are a
producer/consumer pair with no shared owner of the artifact shape, and no gate
that runs one into the other. They disagreed for the entire life of #747 without
a single test failing: the builder emits an archive containing only `repograph`
(`build_native_artifact.py:148-153`), and the installer refused it with
`artifact metadata sidecar is missing` (`native_core_lib.py:285`).

The refusal itself is vestigial. The only sidecar fields it reads (`version`,
`tuple`) are overwritten with the declaration's own values three lines later,
and the follow-up check at `:294` compares the just-assigned values against
their own sources — dead code. The archive bytes were already bound to the
declaration by the sha256 check at `:274`.

Proven by roundtrip: as-is → `verification-failure`; with `:285-286` removed →
`activated`, and `native_core_doctor_payload` → `healthy`, with installed
metadata complete (`version`, `tuple`, `artifact_sha256` from the declaration;
`binary_sha256`, `binary_size`, `binary_mtime_ns` recomputed from the binary —
every field `_verify_version_dir:126-136` reads).

Why no gate caught it: `test_native_core_install.py:50-52` builds its own
fixture archive with `bundle.add(metadata, arcname="artifact.json")`, a shape
the producer never emits, and the local-store path
(`native_core_lib.py:234-239`) copies the sidecar from the build directory — so
every build-side and install-side test passes while the release download path
fails.

## Decision

### D1. Delete the vestigial refusal

Remove `native_core_lib.py:285-286` (the `artifact metadata sidecar is missing`
refusal) and the dead follow-up check at `:294-295`. Metadata is constructed
from the declaration and the extracted binary, which is already what the
installed record contains.

KEEP the sidecar download branch at `:258` and the adjacent-file read at
`:283-284`: the local-store path legitimately supplies a sidecar from the build
directory, and a future multi-file artifact may carry one. Absence stops being
a refusal; presence stays usable.

### D2. One roundtrip gate owns the invariant

Invariant: *the byte stream `build_native_artifact.py` emits must activate
through `run_native_core_phase` unchanged.*

Add a single test that builds (or reuses a built) artifact via the real
producer, serves it through a release-shaped probe whose `asset_names` is
exactly what the attach step uploads, and asserts activation reaches
`activated` and doctor reaches `healthy`. Producer-only and consumer-only proof
do not satisfy this; both existed and both were green.

This gate is the only honest owner of D1's correctness. Without it, deleting the
refusal is just a second unverified guess about the pair.

### D3. Doubles are derived from the producer, never from the consumer

`test_native_core_install.py`'s archive builder must construct its fixture the
way `build_native_artifact.py` constructs a real one — ideally by calling the
producer's own `_write_archive`, so the shapes cannot drift.

Generalize into `.agents/lane-brief-template.md`, extending the strict-argv rule
already added this session: **a test double's accepted shape must be derived
from the real producer, never from the consumer's expectation.** Three confirmed
instances of the consumer-derived double this session and last (the sidecar
fixture; the fake `gh` `release view` arm; the P5 classify fake's `--path a b c`),
none caught by its own suite.

### D4. Non-goals

- Does not change the `native_core` declaration schema.
- Does not make the archive reproducible (separate follow-up: the gzip mtime in
  `_write_archive` makes digests differ across identical builds).
- Does not address consumer repos resolving `not-distributed` because they carry
  no `packaging/charness.json` — recorded, deferred by operator decision.

## Success Criteria

- The real built artifact activates and reads back `native_core: healthy`.
- The roundtrip gate fails if the producer stops emitting what the consumer
  accepts, proven by mutating one side.
- No test constructs a native artifact by a shape the producer cannot emit.
