# Lane brief: native-lifecycle-roundtrip

Governing contract: `charness-artifacts/spec/native-artifact-roundtrip.md`
(D1–D4) and the RCA it came from,
`charness-artifacts/debug/2026-08-29-native-artifact-sidecar.md`. Where this
brief and the spec disagree, THIS BRIEF WINS. No sibling lanes run concurrently.
Do not spawn descendant agents.

Read the RCA first. Its structural finding is the point of this lane: **the
verifier is exempt from verification.** Every existing proof of the native
install lifecycle used a fixture archive built to the consumer's expectation, so
producer and consumer disagreed for the whole life of #747 with every test
green. You are replacing that proof, not adding to it.

## Outcome

### 1. Delete the vestigial refusal

`native_core_lib.py:285-286` refuses with `artifact metadata sidecar is missing`.
Delete it, and delete the dead follow-up at `:294-295` — it compares
`metadata["version"]`/`["tuple"]` against `version`/`tuple_name` three lines
after assigning them from exactly those values, so it cannot fire.

PARENT-VERIFIED: the sidecar contributes nothing. The only fields read
(`version`, `tuple`) are overwritten at `:288-292`; the archive bytes are already
bound to the declaration by `sha256(archive) != expected["sha256"]` at `:274`;
and with `:285-286` removed the real artifact yields `{"status": "activated"}`
with installed metadata carrying every field `_verify_version_dir:126-136` reads.

KEEP the sidecar download branch at `:258` and the adjacent-file read at
`:283-284`. The local-store path (`:234-239`) legitimately supplies a sidecar
from the build directory. Absence stops being a refusal; presence stays usable.

### 2. One roundtrip gate owns the producer/consumer invariant

Invariant: *the byte stream `build_native_artifact.py` emits must activate
through `native_core_lib.run_native_core_phase` unchanged.*

Build a harness that takes the REAL producer's output and drives the REAL
consumer path. It must not construct an archive of its own. Shape:

- obtain the archive from `build_native_artifact.build_native_artifact()` (or a
  cached artifact produced by it — never a hand-rolled `tarfile`);
- serve it through an injected download seam whose release payload is exactly
  what the attach step produces: `asset_names` containing ONLY the archive name
  (`publish_release_native_artifact.py:162-169` uploads one file);
- assert the phase reaches `activated` and
  `native_core_resolution_lib.native_core_doctor_payload` reaches `healthy`.

Prove the gate bites: mutate one side (e.g. have the producer emit a differently
named member) and show the gate fails. A gate that cannot fail is not a gate.

Cargo must not be required. If building in-test is too slow or needs a
toolchain, take the artifact path as a parameter and have the standing test use
a small fixture binary run through the PRODUCER's own `_write_archive`
(`build_native_artifact.py:148-153`) — the point is that the archive's shape is
producer-derived, not that the payload is the real Rust binary.

### 3. Replay the rest of #747's acceptance list against a producer-derived artifact

#747 lists: clean first install, already-current no-op, version transition,
target mismatch, checksum failure, interrupted activation, rollback, and
source/plugin/core skew. Every one was proven with the consumer-derived fixture
that outcome 1 just showed to be wrong-shaped, so none of them is currently
established.

Re-run each through the outcome-2 harness. For each, assert BOTH the phase
status (`PHASE_STATUSES`, `native_core_lib.py:35-50`) and what
`native_core_doctor_payload` reports afterwards. Report a table of scenario →
phase status → doctor status → doctor message.

This is the lane's highest-value work. Treat a scenario you cannot drive through
the real path as a finding to report, not a scenario to skip.

### 4. A failure status must not be laundered into misleading remediation

`_write_status` (`native_core_lib.py:55-60`) records the FULL phase result to
`last-status.json`, including `verification-failure` and `checksum-failure`. But
`_no_pointer_result` (`native_core_resolution_lib.py:148-152`) honors only
`awaiting-artifact` and `offline` from it; every other recorded status falls
through to `missing`, whose message is "No managed native core is active; run
`charness update` when the artifact is available."
(`native_core_resolution_lib.py:281`).

That is how this incident presented: a permanent `verification-failure` reported
to the operator as `missing` with a remediation that is the command that just
failed.

Make a recorded failure status survive into the doctor payload with a message
that does not prescribe the failing command. Do NOT invent new `NativeStatus`
values without saying so — `NativeStatus` (`native_core_resolution_lib.py:14-17`)
already contains `corrupt`, whose message is "The managed native core failed
verification; run `charness update` to restore it." Judge whether an existing
value carries the meaning honestly; if you add one, justify it in your final
message and update every exhaustive consumer of the literal set.

### 5. The install fixture is producer-derived

`tests/charness_cli/test_native_core_install.py:45-52` builds its archive with
`bundle.add(metadata, arcname="artifact.json")` — the shape the producer never
emits, and the direct cause of the missed defect. Rebuild that fixture through
the producer's own archive writer so the shapes cannot drift again.

### 6. Proof

Every claim in outcomes 1-5 is proven by a test that fails before your change
and passes after. For outcome 1 specifically, the "fails before" is the real
`verification-failure`, not a synthetic one.

## Boundaries

Exactly these paths; this list matches the `--scope` flags:

- `scripts/native_core_lib.py`
- `scripts/native_core_resolution_lib.py`
- `scripts/build_native_artifact.py`
- `tests/charness_cli/test_native_core_install.py`
- `tests/charness_cli/` (new harness/test modules)
- `tests/test_build_native_artifact.py`
- `tests/quality_gates/test_native_gate_lib.py`
- `docs/host-packaging.md`

Out of scope; report, do not fix:

- `plugins/charness/**` — generated mirror; the parent runs the exporter.
- `packaging/charness.json` — the declaration and its digest are the parent's.
- `skills/public/release/scripts/**` — the attach step is already integrated and
  correct for what it uploads; if outcome 3 shows the release path itself must
  change, REPORT it rather than editing there.
- Archive reproducibility (the gzip mtime in `_write_archive`) — operator
  deferred it to a later version. Do not fix; do not let it block you. If your
  harness needs a stable digest, compute it from the artifact you actually
  built.
- Consumer repos resolving `not-distributed` for want of a
  `packaging/charness.json` — recorded, deferred.

Frozen contracts:

- `PHASE_STATUSES` (`native_core_lib.py:35-50`) — you may not remove a member.
- The atomic-activation and rollback mechanics (`_phase_locked`,
  `native_core_lib.py:308-397`). Outcome 3 tests them; it does not redesign them.
- `check_native_release_asset.py`'s status vocabulary and reason strings.

## Verification

Run these and quote observed results:

- `python3 scripts/run_standing_pytest.py --repo-root . --include-release-only
  --pytest-target <path>` (one flag per path) over every file you touched plus
  `tests/charness_cli/test_native_core_install.py` and
  `tests/quality_gates/test_native_gate_lib.py`.
- `python3 scripts/check_python_lengths.py --repo-root . --headroom --paths <every
  .py you touched>`. BLOCKING (`run-quality.sh:1070`).
- `python3 scripts/check_test_production_ratio.py --repo-root .
  --require-git-file-listing`. BLOCKING; currently 0.9941 against max 1.00.
  Outcome 3 adds scenario tests, so watch this. If you would cross it, say so
  and stop rather than trimming unrelated tests.

The parent runs `./scripts/run-quality.sh --full` after integration. Your green
run is not integration proof.

## Stop condition and result shape

One coherent commit prefixed `fix(747):`. Stop at outcome 6.

Final message states: what you built; every command run with its observed
result; **the outcome-3 scenario table**; the proof that the outcome-2 gate can
fail; the per-file length headroom and the ratio; every scenario you could not
drive and why; and every deviation from this brief with its reason.
