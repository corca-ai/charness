# Lane brief: 748-real-host-classify (lane P5)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decision D8 (normative — read every bullet; the exclusion is
`role == test` ONLY), D9 (fake-binary test seam), D1 (the shim
`scripts/native_gate_lib.py`, ALREADY LANDED — consume
`resolve_native_core`/`NativeGateError`), and `native/repograph/ABI.md`
`classify` section including the ALREADY-LANDED `--surfaces-optional`
flag. The subject file is
`skills/public/release/scripts/check_real_host_proof.py` — read it in
full; its four-state `evaluation_scope` vocabulary,
absent-`required`-key structure, exit table (0/1/3), and
version-refusal guard are PINNED contracts that must not change.
Sibling lanes touch only `native/**` and
`scripts/check_standalone_imports.py` + its test; stay off those. Do
not spawn descendant agents.

## Outcome

1. Fold change in `check_real_host_proof.py`, raw-glob arm only
   (`build_payload`, currently
   `path_hits = [p for p in changed_paths if matches_any(p, trigger_globs)]`):
   - Candidate hits from `matches_any` are classified via the native
     binary: `classify --surfaces-optional --repo-root <repo_root>
     --path <hit>...` (one invocation), binary resolved through
     `native_gate_lib.resolve_native_core` loaded with
     `SKILL_RUNTIME.load_repo_module_from_skill_script(__file__,
     "scripts.native_gate_lib")` (works in both authoring and exported
     trees). Read the report on exit 0 AND exit 3 (classify emits its
     report at exit 3); only a missing/unparseable report or a
     resolution failure is degradation.
   - A hit is EXCLUDED only when its role is exactly `test`.
     `production`, `doc`, `generated`, `unestablished`, and
     `unestablished-absent` all KEEP the hit.
   - `evaluated` payloads: `path_hits` = post-exclusion hits (still
     drives `required == bool(surface_hits or path_hits)`);
     `excluded_path_hits: [{path, role}]`;
     `test_exclusion: {status: "applied", native_core: <provenance>}`
     or on degradation
     `{status: "unavailable", native_core: <typed status/reason>}`
     with positive-only hits. `test_exclusion` present in EVERY
     `evaluated` payload.
   - `empty`, `not-configured`, broken-config, surface-error payloads:
     byte-for-byte unchanged (no new keys).
   - Declared-surface arm (`match_surfaces`) untouched. Version-refusal
     guard untouched. No new adapter keys. No zero-glob native calls
     (skip classification when there are no candidate raw-glob hits —
     degradation must not be reported when nothing needed excluding;
     use `status: "applied"` with empty exclusions in that case only
     if a classification actually ran, otherwise omit nothing —
     decide, document in the reference doc, and pin it).
2. Tests (`tests/quality_gates/test_release_real_host.py` + existing
   fixture helpers):
   - Consumer-shaped fixture scenario per D8 proof (a): Go-shaped tree
     (production `.go` hit kept; `_test.go` excluded; `testdata/`
     excluded; `README.md` doc-role trigger still a hit; a DELETED
     production path keeps the hit; a generated-mirror-shaped path
     keeps the hit; NO `.agents/surfaces.json` in the fixture repo).
     Drive the REAL fold with `CHARNESS_NATIVE_CORE` pointing at a
     fake binary emitting canned `repograph.classify.v1` documents
     (in-process `main()`/`build_payload` calls, not subprocess — the
     boundary-bypass ratchet counts new test→script process
     boundaries; run it before finishing).
   - Degradation pinned: resolver unavailable → positive-only fold +
     `test_exclusion.status == "unavailable"` + `required` still
     correct.
   - Pin that `empty`/`not-configured`/broken payloads carry NO
     `test_exclusion` key.
   - Existing tests must keep passing unmodified wherever they pin the
     unchanged states; adjust only tests whose pinned `path_hits`
     semantics legitimately meet the new post-exclusion definition.
3. Docs: `skills/public/release/references/real-host-proof.md` and
   `skills/public/release/references/adapter-contract.md` gain the
   derived-exclusion contract: role ownership (topology convention
   table + consumer `topology` declaration), `test`-only exclusion
   with the generated-role rationale (manifest-configured roles must
   not drop publish-gate hits), the degradation state, and the
   payload key table per `evaluation_scope`.

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`skills/public/release/scripts/check_real_host_proof.py`,
`skills/public/release/references/real-host-proof.md`,
`skills/public/release/references/adapter-contract.md`,
`tests/quality_gates/test_release_real_host.py`.
Out of scope: `native/**` (build-only), `plugins/**` (parent syncs),
`scripts/**` (consume `native_gate_lib`, don't modify),
`.agents/release-adapter.yaml`, `adapter.example.yaml` (no new keys —
if you believe a key is needed, STOP and report instead), other
release scripts (`plan_release_run.py` etc. import `build_payload`;
verify they still work unmodified and report if not).

## Verification

- `python3 -m pytest tests/quality_gates/test_release_real_host.py
  tests/quality_gates/test_real_host_proof_version_refusal.py -q`;
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`;
- `./scripts/check-python-lint.sh`;
- one REAL-binary smoke: `cargo build --release` in `native/repograph`
  then run the fold against this repo with a test-only changed path
  (e.g. `--paths tests/quality_gates/test_release_real_host.py`) and a
  production path, `--detail`, and report both payloads verbatim
  (this is D8 proof (b) evidence for the parent).
The parent runs the FULL battery after integration and owns #743
closeout.

## Stop condition and result shape

One coherent commit, prefix `migrate(748):`. Final message: what was
built, commands run with observed results including both verbatim
`--detail` payloads, deviations with reasons.
