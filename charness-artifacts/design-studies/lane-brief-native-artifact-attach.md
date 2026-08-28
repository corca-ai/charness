# Lane brief: release-native-attach

Governing contract:
`charness-artifacts/design-studies/2026-08-29-native-artifact-attach-step.md`.
Decisions D1–D7 in that study are normative for this lane; where this
brief and the study disagree, the study wins and you must say so in your
final message. No sibling lanes run concurrently on these files. Do not
spawn descendant agents.

This lane unblocks the first switch-on release. Everything it builds is
on the single code path every future charness release runs, so a
regression here is a release-machinery outage, not a test failure.

## Outcome

1. `scripts/build_native_artifact.py` no longer refuses a clean
   checkout. `_require_clean_tree` (build_native_artifact.py:64-84)
   runs `git ls-files --others --exclude-standard --directory -z`,
   which reports any directory that is not itself gitignored even when
   every file under it is ignored or the directory is empty. On the
   maintainer checkout this makes the build refuse with "untracked
   files present" while `git status --porcelain -uall` reports zero
   entries. Add `--no-empty-directory` to that invocation.
   PARENT-VERIFIED, both directions, on the real checkout: with the
   flag the command returns empty on the clean tree, and it still
   reports a genuinely untracked file both at the repo root and inside
   a directory whose other contents are ignored. Extend the comment at
   build_native_artifact.py:73-75 — it already explains the
   `--exclude-standard` half of this same false-positive class — rather
   than adding a second comment.

2. A `release_upload` backend op exists, per D1. Add it to
   `OP_PLACEHOLDERS` (publish_release_helpers.py:18-26) with the
   placeholder allowlist `{"tag", "asset"}`, and add
   `upload_release_asset()` beside `create_release`
   (publish_release_helpers.py:186-195) whose default template is
   exactly `["gh", "release", "upload", "{tag}", "{asset}"]`. No
   `--clobber`: overwriting a published asset is irreversible and D1
   forbids it. A non-`gh` backend that declares no `release_upload`
   template must refuse loudly through the existing
   `backend_command` path (publish_release_helpers.py:150-154), not
   silently skip the attach.

3. A preflight refuses BEFORE any irreversible action, per D2. It
   resolves the declaration, locates the local archive, and verifies
   the archive's sha256 equals the declared `sha256`.

   PARENT-VERIFIED trace: the only irreversible actions in this module
   are `git push` (publish_release_resume_publish.py:191,193,195) and
   `create_release` (:198), all inside `publish()`. Everything at or
   above `commit_artifact_before_push` (:183) is local and reversible.

   Call it TWICE, exactly as `_notes_preflight` is already called twice
   — early at :123 and late at :179-182. The early call moves a digest
   mismatch ahead of the pre-push quality gates (:147) and the
   fresh-checkout probes (:150), which is the same reason
   `_notes_preflight`'s docstring gives at :53-55. The late call is the
   one that must be immediately above :183. Both are read-only and
   silent on pass, so repeating is free.

   Do NOT copy `_notes_preflight`'s "skipped once the release exists"
   behavior (:56). A repair resume against an existing release is
   PRECISELY the case where the asset may still be missing — the
   process died between `create_release` and the upload — so the
   native-artifact preflight must run there or the repair cannot
   complete.

   The ordering rule and the reason for it are already written at
   publish_release_resume_publish.py:174-179 ("A gate must not create
   the state it then refuses") — obey that comment; do not restate it.

4. The upload runs inside `publish()`
   (publish_release_resume_publish.py:185-200) immediately after
   `create_release`, and is idempotent per D3: read the release's
   current asset names through the existing `release_view` op and skip
   when the canonical name is already present. Re-entry must be a typed
   no-op, not a failure and not an overwrite.

5. An absent declaration is a typed no-op, never a failure, per D4.
   Reuse the SAME owners `check_native_release_asset.py:66-83` reads —
   `read_native_declaration`, `checkout_version`, `host_tuple`,
   `artifact_declaration` from `scripts/native_core_resolution_lib.py`.
   Do not write a second declaration reader.

6. The canonical artifact name has ONE owner. It is currently an inline
   f-string in a function body at check_native_release_asset.py:86
   (`f"repograph-v{version}-{tuple_name}.tar.gz"`), so it is not
   importable and D6 is not satisfiable as the study words it. Lift it
   to a module-level function in
   `scripts/native_core_resolution_lib.py` (the module both callers
   already import) and make `check_native_release_asset.py:86` call it.
   Both the preflight and the upload read that one owner. This is the
   only refactor of an existing behavior this lane is authorized to
   make; it must not change what `check_native_release_asset.py`
   returns for any input.

7. The archive location follows D5: default
   `runtime_root(repo_root) / "native-artifacts"`, resolved through
   `scripts.runtime_bootstrap.runtime_root`
   (runtime_bootstrap.py:109) — the same owner
   build_native_artifact.py:87-99 resolves, not a re-spelled path. An
   explicit `--native-artifact-dir` flag on the publisher overrides it.
   A declared-but-absent archive is a preflight refusal naming the
   exact expected path and the `build_native_artifact.py` command that
   produces it.

8. The resume payload gains exactly one additive key,
   `native_artifact_upload: {status, asset, reason}`, `status` in
   `uploaded | already-present | not-applicable` (D7). Existing payload
   keys and the exit table are untouched.

   PARENT-VERIFIED: no test asserts the release payload's top-level key
   set exhaustively. The only equality assertion over a payload dict in
   the release suite is on the nested `version_drift_check` sub-dict
   (test_release_resume_surface_revalidation.py:22), which this key
   does not touch. Expect the conversion work in the study's D7 to be
   ZERO. If you nevertheless find a pin that an additive top-level key
   breaks, convert it to a targeted key check and report it by
   file:line — but do not go looking for pins to "improve", and do not
   loosen an assertion that your change does not break.

9. Every claim in outcomes 1-8 is proven by a test that fails before
   your change and passes after.

## Boundaries

Exactly these paths, and this list matches the `--scope` flags:

- `scripts/build_native_artifact.py`
- `scripts/native_core_resolution_lib.py`
- `scripts/check_native_release_asset.py`
- `skills/public/release/scripts/publish_release_helpers.py`
- `skills/public/release/scripts/publish_release_resume_publish.py`
- `skills/public/release/scripts/publish_release_args.py`
- `tests/quality_gates/fixtures/release_publish_fake_gh.py`
- `tests/quality_gates/release_publish_fixtures.py`
- `tests/quality_gates/` (release publish/resume test modules you must
  edit for outcome 8, plus your new tests)
- `tests/test_build_native_artifact.py`
- `tests/test_check_native_release_asset.py`
- `docs/host-packaging.md`

Out of scope, and each of these is a stop-and-report condition rather
than something you fix:

- `plugins/charness/**` is a GENERATED export mirror. Do not hand-edit
  it. The parent runs the exporter after integration.
- `packaging/charness.json`, `packaging/plugin.schema.json`, and every
  version-carrying manifest. This lane does not bump, declare, or
  publish anything.
- `.agents/release-adapter.yaml`. The checklist already carries the
  post-publish obligation; no new adapter keys (D7 of the migration
  plan and the study's D-list both forbid it).
- The Rust crate under `native/repograph/`.
- `publish_release_execute.py`'s `_publish_and_finalize`. Its own
  docstring (publish_release_execute.py:225-237) records that
  `execute_publish_plan` always stops at the prepared record, so it is
  unreachable in production and its only callers are tests. Do not
  wire the attach into it and do not "fix" its reachability.

Frozen contracts:

- `check_native_release_asset.py`'s returned status vocabulary
  (`not-applicable` / `fail` / `pass`) and every reason string.
- The four existing `OP_PLACEHOLDERS` entries and their allowlists.
- `NativeStatus` in native_core_resolution_lib.py:14-17.

## Verification

Run these yourself, and quote the observed result of each in your final
message:

- `python3 scripts/run_standing_pytest.py --repo-root .
  --include-release-only --pytest-target <path>` over every test file
  you touched plus `tests/quality_gates/test_release_publish.py`,
  `tests/quality_gates/test_release_resume_publish_integration.py`,
  `tests/quality_gates/test_release_publish_resilience.py`,
  `tests/test_build_native_artifact.py`,
  `tests/test_check_native_release_asset.py`. Pass one
  `--pytest-target` per path; the runner takes targets by flag, not as
  bare positionals. `--include-release-only` is REQUIRED here, not
  optional: the release publish tests are marked
  `@pytest.mark.release_only` (test_release_publish.py:27,53,80,123,195)
  and are silently deselected without it, so a run that omits it proves
  nothing about the path you changed.
- `python3 scripts/check_test_production_ratio.py --repo-root .
  --require-git-file-listing`. This gate is BLOCKING and the checkout
  has roughly 1,000 test lines of headroom against a 1.00 max. Report
  the ratio you observe. If your tests would cross it, say so and stop
  rather than trimming unrelated tests to fit.

The parent runs `./scripts/run-quality.sh --full` after integration.
Your green run is not integration proof and must not be reported as
one.

## The fake-gh seam

`tests/quality_gates/fixtures/release_publish_fake_gh.py` matches verbs
by PREFIX today — `args[:2] == ["release", "create"]` at line 28, and
the same shape at lines 24, 37, 48 — so it accepts arbitrary trailing
argv. A payload-only fake of exactly this kind let a real usage-error
regression ship past a full lane test suite in the 2026-08-28 session.

Your new `release upload` arm must parse STRICTLY: accept exactly
`release upload <tag> <path>` and exit 2 on any other argv shape,
including extra positionals and unknown flags. Record the uploaded
asset into `FAKE_GH_RELEASE_STATE` (or a sibling state file) so the
idempotence test in outcome 4 can observe the second call being
skipped. Do not loosen the existing arms; do not tighten them either —
that is a different change.

## Stop condition and result shape

One coherent commit prefixed `release:`. Stop at outcome 9; do not
widen into a release-machinery audit, and do not fix defects you notice
outside the scope list — name them in your final message instead.

Final message states: what you built; every command you ran with its
observed result; the observed test-production ratio; every equality-pinned
assertion you converted, by file:line; and every deviation from this
brief with its reason.
