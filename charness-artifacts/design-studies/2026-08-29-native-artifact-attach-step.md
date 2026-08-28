# Design: attach the native artifact to the published release

> Status: rev 1 (pre-review)
> Date: 2026-08-29
> Parent: #744; discharges the last unbuilt piece of #747's distribution
> machinery. Blocks the first switch-on release (v8.0.0).

## Problem

`scripts/build_native_artifact.py` builds and hashes
`repograph-v<version>-<tuple>.tar.gz`, and
`scripts/check_native_release_asset.py` verifies post-publish that the
declared asset name appears in the release's `asset_names`
(check_native_release_asset.py:114-124). Nothing attaches the archive
between those two steps.

The release backend declares exactly four ops —
`release_view`, `release_view_body`, `release_create`, `auth_check`
(publish_release_helpers.py:18-26) — and `create_release` runs
`gh release create {tag} --verify-tag --title {title}` plus a notes flag
(publish_release_helpers.py:186-195). There is no `--attach`, no
`gh release upload`, and no asset op. `docs/host-packaging.md:88-91`
describes the upload as if it existed; it does not.
`charness-artifacts/design-studies/issue-746-747/release_evidence.md:68`
already records this as a wholly new step, not an extension.

Consequence today: publishing v8.0.0 with a `native_core` declaration
would ship a release whose every consumer resolves `awaiting-artifact`
or `offline` — the declaration promises an asset that is not there.

## The live publish path (the seam this change edits)

`execute_publish_plan` always stops at the prepared record, so
`_publish_and_finalize` is unreachable in production and its own
docstring says so (publish_release_execute.py:225-237). The live
push/create path is `publish()` inside
`publish_release_resume_publish.py:185-200`.

## Decisions

### D1. A new typed backend op, not a flag on `release_create`

Add `release_upload` to `OP_PLACEHOLDERS`
(publish_release_helpers.py:18-26) with the placeholder allowlist
`{"tag", "asset"}`, and a helper `upload_release_asset()` beside
`create_release` (publish_release_helpers.py:186-195). Default template:

```
["gh", "release", "upload", "{tag}", "{asset}"]
```

Rationale for a distinct op rather than appending `--attach` to the
`release_create` template: a non-`gh` backend that declares its own
`release_create` template would silently lose the attach if it rode on
that template, and `backend_command` already refuses an undeclared op
for non-`gh` backends (publish_release_helpers.py:150-154) — which is
the correct loud behavior for a backend that cannot upload assets.

NO `--clobber`. Overwriting a published asset is an irreversible
outward-facing action. Idempotency comes from D3's presence check,
matching the existing `release_exists` → skip-create idiom
(publish_release_resume_publish.py:196-199).

### D2. Preflight BEFORE the tag push; upload AFTER create

Two separate steps, deliberately:

- **Preflight** (`native_artifact_preflight`), called next to
  `_notes_preflight` at publish_release_resume_publish.py:181-184, i.e.
  before `commit_artifact_before_push` and before `publish()`:
  resolve the declaration, locate the local archive, and verify its
  sha256 equals the declared `sha256`. Refuse loudly here.
- **Upload**, inside `publish()` immediately after `create_release`
  (publish_release_resume_publish.py:196-199).

The ordering is the file's own already-paid lesson, stated at
publish_release_resume_publish.py:174-179: a gate must not create the
state it then refuses. A digest mismatch discovered after
`git push` + `gh release create` leaves a published release that
promises an asset it will never get; discovered before the push, it is
a clean stop.

### D3. Idempotent upload via presence check

Before uploading, read the release's current asset names through the
existing `release_view` op and skip when the canonical name is already
present. Resume re-entry is a first-class path here
(publish_release_resume_publish.py:71), so a second upload attempt must
be a typed no-op, not a failure and not a silent overwrite.

### D4. Absent declaration is a typed no-op, never a failure

Releases without a `native_core` declaration must publish unchanged.
The preflight and upload both return
`{"status": "not-applicable", "reason": ...}` when
`read_native_declaration` returns `None` or `artifact_declaration`
returns `None` for this version+tuple — reusing the SAME owners
`check_native_release_asset.py:66-83` reads
(`scripts.native_core_resolution_lib.read_native_declaration`,
`checkout_version`, `host_tuple`, `artifact_declaration`). No second
declaration reader is written.

### D5. Archive location

Default: `runtime_root(repo_root) / "native-artifacts"` — the same
default `build_native_artifact.py:87-99` writes to, resolved through
`scripts.runtime_bootstrap.runtime_root` (runtime_bootstrap.py:109), not
re-spelled. An explicit `--native-artifact-dir` flag on the publisher
overrides it. A declared-but-absent archive is a preflight refusal
naming the exact expected path and the build command.

### D6. Canonical-name agreement

The preflight reuses the canonical-name rule
`repograph-v{version}-{tuple}.tar.gz` that
check_native_release_asset.py:86-94 already enforces against the
declaration. It must be READ from that owner, not re-spelled, so the
two cannot drift.

### D7. Payload contract

The resume payload gains one key,
`native_artifact_upload: {status, asset, reason}` with `status` in
`uploaded | already-present | not-applicable`. Purely additive; the
existing exit table and every other payload key are untouched. Four
exact-payload pins raised `KeyError` on exactly this shape of additive
field during the #746/#747 integration (recorded in #753's Experience
section) — so the lane must check for equality-pinned release payload
assertions and convert them to targeted key checks rather than let the
pin dictate the schema.

## Proof obligations

- Fake-`gh` fixture (`tests/quality_gates/fixtures/release_publish_fake_gh.py`)
  extended to the `release upload` verb with a STRICT argv parser:
  exactly `release upload <tag> <path>`, exiting 2 on any other shape.
  A payload-only fake let a real usage-error regression ship in the
  last session; the argv shape is the seam.
- Digest-mismatch preflight refusal happens with no tag created and no
  push performed.
- Absent-declaration path publishes byte-identically to today.
- Re-entry with the asset already present reports `already-present` and
  issues no second upload.
- Non-`gh` backend without a declared `release_upload` template refuses
  loudly rather than silently skipping the attach.

## Non-claims

- This does not make the release path build the artifact; the operator
  still runs `build_native_artifact.py` and the digest lands in
  `packaging/charness.json` by hand before the release commit.
- This does not add CI-side artifact publication.
- Multi-tuple releases are out of scope: the host tuple is the only one
  built, and `supported_tuples` stays a single-entry list for v8.0.0.
