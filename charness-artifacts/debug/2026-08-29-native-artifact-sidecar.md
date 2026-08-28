# Native Artifact Sidecar Debug Review
Date: 2026-08-29

## Problem

The v8.0.0 switch-on release would publish an artifact no consumer can install.
`_prepare_activation` refuses with `artifact metadata sidecar is missing` for the
exact archive `build_native_artifact.py` produces. The deeper problem is that the
refusal is vestigial, and three separate readers — an opus release critique, this
session's parent, and the original author — read that refusal message as a real
requirement without checking whether the demanded value is ever consumed.

## Correct Behavior

Given a published archive whose sha256 matches the `native_core` declaration,
when `charness update` runs, then the core activates and `doctor` reports
`native_core: healthy`. And: a verification failure is investigated by suspecting
the verifier before the subject.

## Observed Facts

- The archive has one member: `tar tzvf` → `4022112 repograph`
  (`build_native_artifact.py:148-153`); the sidecar is written *beside* it at
  `:200`.
- The attach step uploads only `preflight["path"]`
  (`publish_release_native_artifact.py:162-169`), so the sidecar download at
  `native_core_lib.py:258`, gated on `"artifact.json" in assets`, never runs.
- Real artifact through the real release path: `{"status":
  "verification-failure", "reason": "artifact metadata sidecar is missing"}`.
- The only sidecar fields read (`version`, `tuple`) are overwritten with the
  declaration's values three lines later; the follow-up check at `:294` compares
  just-assigned values against their own sources — unreachable.
- `native_core_resolution_lib.py:150` honors only `awaiting-artifact`/`offline`
  from `last-status.json`, so `verification-failure` is laundered into doctor
  `missing`, whose remediation is the command that just failed.

## Reproduction

- Stub `_download_artifact` to serve the built archive from disk; call
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
  not feeding it — yields a healthy install with complete metadata |
  disconfirmer: if any retained field originates in the sidecar, deleting the
  refusal must leave installed metadata incomplete. Cost: one
  `grep 'metadata.get'` plus one roundtrip.

## Verification

- Result: confirmed. Removing only `native_core_lib.py:285-286` gives
  `{"status": "activated"}`; installed metadata carries `version`, `tuple`,
  `artifact_sha256` (from the declaration) and `binary_sha256`, `binary_size`,
  `binary_mtime_ns` (recomputed from the binary) — every field
  `_verify_version_dir:126-136` reads. Doctor → `{"status": "healthy",
  "provenance": "managed", "source_drift": "in-sync"}`. Nothing retained came
  from the sidecar.

## Root Cause

Two layers.

Mechanical: the refusal at `native_core_lib.py:285-295` demands a file whose
contents it discards; the bytes were already bound to the declaration by the
sha256 check at `:274`.

Structural: **the verifier is exempt from verification.** Two faces of one
model. (a) Doubles are derived from the consumer's expectation, so the pair
validates itself — `test_native_core_install.py:50-52` builds an archive with
`bundle.add(metadata, arcname="artifact.json")`, a shape the producer never
emits. (b) A gate's complaint is read as a specification of the problem, so the
gate leaves the audit set — nobody asked who reads the value it demands.

Five whys: (1) archive lacks the file, `:285` refuses; (2) `_write_archive` adds
only the binary; (3) no test caught it because the installer's fixture is
consumer-derived; (4) consumer and fixture landed in `b3a244947 "add inert
native core install lifecycle"`, the producer in `b6d196f43`, unreconciled;
(5) the lifecycle was deliberately **inert**, so the pair never ran end to end
and "inert" never became a reconciliation obligation before first publish.
Bottom (missing invariant + missing gate + missing habit): no owner of the
artifact-shape contract, no gate running the builder's bytes through the
installer, and no standing question "who consumes what this gate demands?"

## Invariant Proof

- Invariant: the byte stream `build_native_artifact.py` emits must activate
  through `run_native_core_phase` unchanged.
- Producer Proof: the builder's tests pass on output the installer rejects.
- Final-Consumer Proof: only the roundtrip establishes it; failed as-is, passed
  with the refusal removed.
- Interface-Shape Sibling Scan: this session's fake `gh`
  (`fixtures/release_publish_fake_gh.py:24-48`) claimed `release view` by argv
  length and broke `release_view_body`'s real argv — consumer-derived double,
  fixed in `7cc3a24ec`.
- Non-Claims: no claim about non-linux tuples; no claim the roundtrip gate
  exists yet; no claim the rest of #747's acceptance list has been re-proven
  against a real artifact.

## Detection Gap

- `check_native_release_asset.py:86-94,114-124` | checks only the asset *name* |
  run real builder output through `run_native_core_phase` with a release probe.
- `test_native_core_install.py` | supplies its own archive, and the local-store
  path (`native_core_lib.py:234-239`) copies the sidecar from the build dir, so
  every #747 build/install test passes while the download path fails | same gate.
- Reading habit | no gate can fire on "this refusal demands an unused value";
  the cheap check is `grep 'metadata.get'` before satisfying any refusal.

## Sibling Search

- Mental model: **verification machinery is not itself verified** — doubles
  written from the consumer, and gate complaints read as specifications.
- prior instance, documented: `check-test-production-ratio` reported 1.18 and
  was read as "too many tests"; the JTBD audit refuted the premise (96.5% keep)
  and the honest move was fixing the denominator
  (`issue-753/2026-08-28-jtbd-audit-quality-gates.md:136-139`) | decision:
  confirms the pattern, no action here | proof: prior artifact
- this session: the opus release critique filed the sidecar as BLOCKER 1 and
  proposed supplying the file; the parent offered three options all premised on
  feeding the gate | decision: same class, corrected | proof: runtime roundtrip
- abstraction up: `_publish_and_finalize` (`publish_release_execute.py:225`)
  unreachable in production, kept alive by three test-only callers | decision:
  valid follow-up outside the slice | proof: static caller scan |
  `follow-up: release-machinery-jtbd-audit`
- cross-file: `tests/quality_gates/fixtures/release_publish_fake_gh.py` and
  `tests/charness_cli/test_native_core_install.py`
- mental-model siblings: the rest of #747's acceptance list (version transition,
  target mismatch, checksum failure, interrupted activation, rollback, skew) was
  proven with the same consumer-derived fixtures | decision: valid follow-up
  outside the slice | proof: static scan |
  `follow-up: native-lifecycle-real-artifact-replay`

## Seam Risk

- Interrupt ID: native-artifact-sidecar-2026-08-29
- Risk Class: external-seam
- Seam: a locally-built artifact meeting a download path no local test traverses
- Disproving Observation: the real artifact returned `verification-failure`
  while every producer-side and consumer-side test was green
- What Local Reasoning Cannot Prove: that emitted bytes satisfy the installer
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/native-artifact-roundtrip.md

## Prevention

Delete the vestigial refusal and its dead follow-up
(`native_core_lib.py:285-286, 294-295`), keeping the sidecar *download* branch
the local-store path uses. Add the roundtrip gate — the invariant's only honest
owner. Extend `.agents/lane-brief-template.md`: a double's accepted shape must be
derived from the real producer, never the consumer's expectation. And record the
reading habit this incident cost: **a verification failure is investigated by
suspecting the verifier first — before satisfying a refusal, name who consumes
the value it demands.**
