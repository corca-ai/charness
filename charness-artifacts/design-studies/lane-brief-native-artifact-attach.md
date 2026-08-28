# Lane brief: release-native-attach

Governing contract: THIS BRIEF. Where it and
`charness-artifacts/design-studies/2026-08-29-native-artifact-attach-step.md`
(the design study, rev 1) disagree, THIS BRIEF WINS — it carries
corrections that two opus reviews confirmed against the sources, and the
study's D2 line ranges, D6 mechanism, and D7 pin claim are all known
stale. Read the study for context and rationale only. No sibling lanes
run concurrently on these files. Do not spawn descendant agents.

This lane unblocks the first switch-on release. Everything it builds is
on the single code path every future charness release runs, so a
regression here is a release-machinery outage, not a test failure.

## Outcome

### 1. The builder stops refusing a clean checkout

`_require_clean_tree` (build_native_artifact.py:64-84) runs
`git ls-files --others --exclude-standard --directory -z`, which reports
any directory that is not itself gitignored even when every file under it
is ignored or the directory is empty. On the maintainer checkout this
refuses with "untracked files present" while `git status --porcelain
-uall` reports zero entries. Add `--no-empty-directory` to that
invocation.

PARENT-VERIFIED both directions on the real checkout, and independently
reproduced in review: with the flag the command returns empty on the
clean tree, and it still reports a genuinely untracked file both at the
repo root and inside a directory whose other contents are ignored.
Extend the comment at build_native_artifact.py:73-75 — it already
explains the `--exclude-standard` half of this same false-positive class
— rather than adding a second comment.

### 2. A new cohesion-scoped module owns the whole native-artifact concern

Create `skills/public/release/scripts/publish_release_native_artifact.py`.
It owns declaration resolution, the preflight, the asset-presence read,
and the upload.

This is REQUIRED, not a style preference.
`skills/public/release/scripts/publish_release_helpers.py` measures 358
tokei code lines against a hard 360 limit
(`python3 scripts/check_python_lengths.py --repo-root . --headroom
--paths skills/public/release/scripts/publish_release_helpers.py`), and
`check-python-lengths` is queued BLOCKING at run-quality.sh:1070. Two
code lines of headroom cannot hold a function. The gate's own refusal
text (check_python_lengths.py:191-195) prescribes exactly this response:
"Split the file into a cohesive new module or delete code; do not
mechanically spill into an `_extra_lib`/`_lib` companion to dodge the
cap." A module named for the concern it owns satisfies that; a
`publish_release_helpers_extra.py` does not.

Only ONE thing goes into `publish_release_helpers.py`: the
`release_upload` and `release_assets` entries in `OP_PLACEHOLDERS`
(publish_release_helpers.py:18-26). Spell each placeholder set inline
(`"release_upload": frozenset({"tag", "asset"}),`) so the cost is one
code line per op. After your change, re-run the headroom command above
and report the observed number; if `publish_release_helpers.py` is at or
over 360 you have not finished.

### 3. Two typed backend ops, not one, and not a reused one

Add BOTH to `OP_PLACEHOLDERS`:

- `release_upload`, allowlist `{"tag", "asset"}`, default template
  exactly `["gh", "release", "upload", "{tag}", "{asset}"]`. No
  `--clobber`: overwriting a published asset is irreversible.
- `release_assets`, allowlist `{"tag"}`, default template
  `["gh", "release", "view", "{tag}", "--json", "assets", "--jq",
  ".assets[].name"]`, one asset name per output line.

Do NOT read asset names through the existing `release_view` op. That op's
contract is presence, not content: `release_exists`
(publish_release_helpers.py:180-183) reads only its return code, as does
`verify_release_visible` (publish_release_post_create.py:59-76). An
adapter may declare its own `release_view` template — a shape the suite
actively tests (test_release_backend.py:344,
test_release_distinct_channel.py:283) — and appending `--json` to a
template you do not own produces argv that adapter never contemplated,
and perturbs the token set `publish_release_same_proxy_guard`'s
`release_view_shape` (:71-84) compares observer probes against.

This is the module's own established idiom, not a new invention:
`release_view_body` already exists as a distinct op for precisely this
reason, with the rationale written at publish_release_helpers.py:20-23.
The frozen contract below covers only the FOUR EXISTING entries, so
adding a fifth and sixth is in scope.

A non-`gh` backend that declares no template for either new op must
refuse loudly through the existing `backend_command` path
(publish_release_helpers.py:147-151 — the guard is at :148), not
silently skip the attach.

### 4. The no-op is structural, not conditional

Both the preflight and the upload have this as their FIRST executable
statement:

```python
if read_native_declaration(repo_root) is None:
    return {"status": "not-applicable", "reason": ...}
```

before `host_tuple()`, before any path resolution, before any digest
work. On a release with no `native_core` declaration, no new code beyond
one dict lookup runs. `read_native_declaration`
(native_core_resolution_lib.py:55-57) is a pure read over
`packaging/charness.json` whose `_manifest` helper (:47-52) already
swallows `OSError`/`JSONDecodeError`, so it cannot itself raise.

This matters because the call sites in outcome 6 are UNCONDITIONAL. The
no-op must not depend on you getting a conditional right.

Do NOT resolve the archive directory before the declaration check.
`runtime_root` raises `RuntimeEnvironmentError`
(runtime_bootstrap.py:71,85-89), which is a `RuntimeError` and NOT an
`OSError` — so `build_native_artifact.py:91-94`'s `except OSError` does
not contain it. That is a real pre-existing defect in the builder;
REPORT it, do not fix it here, and above all do not copy that shape.

### 5. The preflight distinguishes "nothing declared" from "declared wrong"

`artifact_declaration` (native_core_resolution_lib.py:78-92) returns
`None` for FOUR different conditions, including a present-but-malformed
entry: a truncated `sha256` or a missing `name` hits the validity guard
at :89-92 and returns `None`, indistinguishable from "this version
declares nothing".

Under a naive outcome-4 reading that means a typo'd digest in
`packaging/charness.json` yields `not-applicable`, the upload is
skipped, and v8.0.0 ships without its asset — the exact failure this
lane exists to prevent. The post-publish net does not catch it either:
check_native_release_asset.py:79-85 returns `not-applicable` for the
same input and `main()` exits 0 (:145).

So: after the declaration is confirmed present, the preflight must
determine whether the artifact TABLE has an entry for this
version+tuple. If an entry exists but is malformed, REFUSE LOUDLY naming
the offending field. Only a genuinely absent entry is `not-applicable`.
Do not change `artifact_declaration`'s own return contract — read the
table yourself for the discriminator.

### 6. Preflight placement — twice, and above the dry-run return

PARENT-VERIFIED trace, confirmed in review: no irreversible action
occurs at or above publish_release_resume_publish.py:183. The pushes are
at :191,193,195 and `create_release` at :198, all inside `publish()`.
(Irreversible work DOES occur later — `commit_final_release_artifact` at
:211 pushes, and `run_release_closeout_tail` at :217 closes GitHub
issues — which is why the upload belongs inside `publish()` and not
after :202.)

Call the preflight TWICE, exactly as `_notes_preflight` is already
called twice, at :123 and at :179-182:

- The early call at :123 moves a digest mismatch ahead of the pre-push
  quality gates (:147) and the fresh-checkout probes (:150) — the same
  reason `_notes_preflight`'s docstring gives at :53-54.
- The late call goes immediately above `commit_artifact_before_push`
  (:183).

Both sites are reachable on both the claims and non-claims lanes; a
preflight reads only `repo_root`, never `state`, so there is no lane
where it crashes on unpopulated state.

STATE THIS CONSEQUENCE in your final message rather than letting it be
discovered: :123 sits ABOVE the dry-run return at :127-130, so a
`--resume` dry-run will now refuse when a declared archive is missing
locally instead of always emitting a packet. That is the intended
behavior, but it is a change to the dry-run contract.

Do NOT copy `_notes_preflight`'s "skipped once the release exists"
behavior (:56, :60-61). A repair resume against an existing release is
PRECISELY the case where the asset may still be missing — the process
died between `create_release` and the upload — so the native-artifact
preflight must run there or the repair cannot complete.

### 7. The upload is unconditional, and its failure does not strand the release

`create_release` is NOT a statement. It is the `else` arm of a
conditional expression at publish_release_resume_publish.py:196-199, so
on the repair lane (`state["release_exists"]` true) it never evaluates.
An upload placed "after `create_release`" lands in the `else` arm and
never runs on exactly the path outcome 6 justifies the design around.

Place the upload UNCONDITIONALLY after the `output = (...)` assignment
completes and before `return` at :200.

It is idempotent: read current asset names through the new
`release_assets` op and skip when the canonical name is already present,
reporting `already-present`. Re-entry must be a typed no-op, not a
failure and not an overwrite.

Upload failure must NOT propagate as a bare `SystemExit` out of
`common.timed` at :202. `cli.run` refuses that way
(publish_release_helpers.py:39-45,56-58), and `gh release upload`
without `--clobber` exits nonzero when the asset already exists — the
TOCTOU the presence check cannot close. If that escapes, `git push` and
`gh release create` have already happened and the raise skips
`finalize_release_payload` (:207), `commit_final_release_artifact`
(:211), and `run_release_closeout_tail` (:217), leaving a PUBLISHED
release with no committed record and no closeout, unrecoverable by
re-running.

Follow the idiom this module already owns for this exact class at
:210-214: record the failure into the payload, commit the final release
artifact, and only then fail. Read those lines and mirror their shape.

### 8. The canonical artifact name has exactly one owner — including the producer

The name is currently spelled THREE times, all character-identical:

- check_native_release_asset.py:86 (the checker)
- build_native_artifact.py:148 (the PRODUCER — the only one that names a
  file on disk)
- and it would be a fourth in your new module

Lift it to a module-level function in
`scripts/native_core_resolution_lib.py` — the module every caller already
imports, and which contains nothing equivalent today
(`artifact_declaration` only READS `name`/`sha256`, it never composes
them). Then wire ALL THREE call sites to it, the producer included.
Leaving `build_native_artifact.py:148` un-wired leaves the drift open on
the only side that creates the file.

This is the only refactor of existing behavior this lane is authorized
to make. It must not change what `check_native_release_asset.py` returns
for any input.

### 9. The archive location has no override flag

Resolve `runtime_root(repo_root) / "native-artifacts"` through
`scripts.runtime_bootstrap.runtime_root` (runtime_bootstrap.py:109) —
the same owner `build_native_artifact.py:87-99` resolves. A
declared-but-absent archive is a refusal naming the RESOLVED expected
path (print it; the directory is keyed on
`sha256(str(repo_root.resolve()))[:16]` at runtime_bootstrap.py:76,106
and is sensitive to `CHARNESS_RUNTIME_ROOT`, `XDG_CACHE_HOME`, and
`TMPDIR`, so a bare "not found" is undebuggable) and naming the
`build_native_artifact.py` command that produces it.

Do NOT add a `--native-artifact-dir` flag. `publish_release_args.py:68-71`
documents that a resume rebuilds its payload from arguments, so a flag
omitted on resume silently relocates where the preflight looks — a
footgun on the release path, and nothing in the v8.0.0 flow needs the
override.

### 10. Payload key

The resume payload gains exactly one additive key,
`native_artifact_upload: {status, asset, reason}`, `status` in
`uploaded | already-present | not-applicable`. Existing payload keys and
the exit table are untouched.

PARENT-VERIFIED: no test asserts the release payload's top-level key set
exhaustively, so expect the conversion work the study's D7 imagines to be
ZERO. Nested sub-dict equality pins do exist
(test_release_resume_surface_revalidation.py:22 on `version_drift_check`,
and also test_release_backend.py:309, test_release_real_host.py:242,
test_release_run_planner.py:138, test_release_observer.py:304) — none is
touched by an additive top-level key. Do not go looking for pins to
"improve", and do not loosen an assertion your change does not break.

### 11. Existing resume fixtures must not read the real manifest

`test_release_resume_edge_coverage.py:183,189,714,882` and
`test_release_resume_surface_revalidation.py:57` construct `args` via
`SimpleNamespace` and pass `Path(".")` as `repo_root`. Today a preflight
there resolves the REAL `packaging/charness.json`, which harmlessly has
no `native_core` key. The moment v8.0.0 adds the declaration — the
release this lane exists to enable — those tests would start looking for
an archive that is not in the test environment and refuse. The lane's
green run would go red on the release it unblocks.

Give those fixtures an isolated `repo_root`. Read any new attribute off
`args` with `getattr(args, ..., None)` so a fixture that predates your
change cannot raise `AttributeError`.

### 12. Proof

Every claim in outcomes 1-11 is proven by a test that fails before your
change and passes after.

## Boundaries

Exactly these paths, and this list matches the `--scope` flags:

- `scripts/build_native_artifact.py`
- `scripts/native_core_resolution_lib.py`
- `scripts/check_native_release_asset.py`
- `skills/public/release/scripts/publish_release_native_artifact.py` (new)
- `skills/public/release/scripts/publish_release_helpers.py`
- `skills/public/release/scripts/publish_release_resume_publish.py`
- `skills/public/release/scripts/publish_release_cli.py`
- `tests/quality_gates/fixtures/release_publish_fake_gh.py`
- `tests/quality_gates/release_publish_fixtures.py`
- `tests/quality_gates/` (the release resume/publish modules named in
  outcome 11, plus your new test modules)
- `tests/test_build_native_artifact.py`
- `tests/test_check_native_release_asset.py`
- `docs/host-packaging.md`

`publish_release_cli.py` is in scope for a specific reason: `cli` is a
`SimpleNamespace` built from an explicit allowlist —
`{name: globals()[name] for name in names}` at :142 over the `names`
tuple at :94-141, with helpers re-exported individually at :54-55. Your
new functions are unreachable as `cli.<name>` until they are registered
in BOTH places. Do not work around this by inlining a private duplicate
into `publish_release_resume_publish.py`.

Out of scope; each is a stop-and-report condition, not something you fix:

- `plugins/charness/**` is a GENERATED export mirror. Do not hand-edit
  it. The parent runs the exporter after integration.
- `packaging/charness.json` and every version-carrying manifest. This
  lane does not bump, declare, or publish. The `native_core` declaration
  and its digest are the PARENT's, added at release time after building
  the archive; that is a deliberate scope cut, not an omission.
- `.agents/release-adapter.yaml`. The checklist already carries the
  post-publish obligation; no new adapter keys.
- The Rust crate under `native/repograph/`.
- `publish_release_execute.py`'s `_publish_and_finalize`. Its docstring
  (:225-237) records that `execute_publish_plan` always stops at the
  prepared record, so it is unreachable in production and its only
  callers are tests. Do not wire the attach into it; do not "fix" its
  reachability.
- `build_native_artifact.py:91-94`'s `except OSError` not catching
  `RuntimeEnvironmentError`. Real, pre-existing, out of scope.

Frozen contracts:

- `check_native_release_asset.py`'s status vocabulary
  (`not-applicable` / `fail` / `pass`) and every reason string.
- The FOUR EXISTING `OP_PLACEHOLDERS` entries and their allowlists.
  Adding new ops is in scope; changing these four is not.
- `NativeStatus` (native_core_resolution_lib.py:14-17).
- `artifact_declaration`'s return contract.

## The fake-gh seam

`tests/quality_gates/fixtures/release_publish_fake_gh.py` matches verbs
by PREFIX today — `args[:2] == ["release", "create"]` at :28, same shape
at :24, :37, :48 — so it accepts arbitrary trailing argv. A payload-only
fake of exactly this kind let a real usage-error regression ship past a
full lane test suite in the 2026-08-28 session.

ADD two new arms; do not modify the existing four. (An earlier draft of
this brief said "do not loosen the existing arms; do not tighten them
either" while also requiring asset names from the `release view` arm,
which prints nothing at :24-27 — those could not both hold. Splitting
asset names onto their own `release_assets` op removes the conflict:
the existing `release view` arm stays exactly as it is.)

- A `release upload` arm parsing STRICTLY: accept exactly
  `release upload <tag> <path>` and exit 2 on any other argv shape,
  including extra positionals and unknown flags. Record the uploaded
  asset name into the release state so the idempotence test can observe
  the second call being skipped.
- A `release view <tag> --json assets --jq ...` arm (or a sibling state
  file) emitting the recorded asset names, one per line, matched
  strictly enough that a malformed invocation exits 2.

## Verification

Run these yourself and quote the observed result of each:

- `python3 scripts/run_standing_pytest.py --repo-root . --include-release-only
  --pytest-target <path>` — one `--pytest-target` per path; the runner
  takes targets by flag, not as bare positionals. `--include-release-only`
  is REQUIRED, not optional: the release publish tests are marked
  `@pytest.mark.release_only` (test_release_publish.py:27,53,80,123,195)
  and are silently deselected without it, so a run that omits it proves
  nothing about the path you changed. Cover every file you touched plus
  `tests/quality_gates/test_release_publish.py`,
  `tests/quality_gates/test_release_resume_publish_integration.py`,
  `tests/quality_gates/test_release_resume_edge_coverage.py`,
  `tests/quality_gates/test_release_publish_resilience.py`,
  `tests/quality_gates/test_release_backend.py`,
  `tests/test_build_native_artifact.py`,
  `tests/test_check_native_release_asset.py`.
- `python3 scripts/check_python_lengths.py --repo-root . --headroom
  --paths <every .py file you touched>`. BLOCKING gate
  (run-quality.sh:1070). `publish_release_helpers.py` starts at 358/360
  and `tests/quality_gates/test_release_publish_resilience.py` at
  779/800 — do NOT put new tests in that file. Report every observed
  headroom number.
- `python3 scripts/check_test_production_ratio.py --repo-root .
  --require-git-file-listing`. BLOCKING; currently 0.9931 with 1,003
  test lines of headroom against a 1.00 max. Report the ratio you
  observe. Review estimated this lane at ~450-600 test lines, which
  fits; if yours would cross, say so and stop rather than trimming
  unrelated tests to fit.

The parent runs `./scripts/run-quality.sh --full` after integration.
Your green run is not integration proof and must not be reported as one.

## Stop condition and result shape

One coherent commit prefixed `release:`. Stop at outcome 12; do not
widen into a release-machinery audit, and do not fix defects you notice
outside the scope list — name them in your final message instead.

Final message states: what you built; every command you ran with its
observed result; the observed per-file length headroom and the
test-production ratio; the dry-run contract change from outcome 6; and
every deviation from this brief with its reason.
