# Release Surface Check

<!-- charness-release-state:abandoned-prepare -->
Date: 2026-08-29

## Scope

- target version: `8.0.0`

This record ABANDONS the `8.0.0` prepare attempt of 2026-08-28
(`533f24dad release: prepare charness v8.0.0 locally`). It is not a
release record. The next release run rewrites this file.

## Why this attempt is abandoned rather than resumed

- Nothing was published. `git ls-remote --tags origin 'refs/tags/v8*'`
  returns empty, there is no `v8.0.0` GitHub release, and `origin/main`
  is 78 commits behind local `main`.
- No claims review was ever committed against it. The superseded record
  read `pending independent claims review` for the branch/tag push, the
  GitHub release record, and the public surface verification, so the
  prepared boundary binds no review and discards no evidence.
- The prepared record commit is unreachable as a boundary. 78 commits of
  the #748 slice-1 migration and the #753 test-corpus work landed on top
  of it. `critique-boundary.md:145-150` names the abandon exit as "a
  reset to the commit before the prepared record"; that reset would
  discard all of that work, so the exit is taken by RECORDING the
  abandonment here instead.

`critique-boundary.md:124-131` states plainly that deleting the marker
and amending is cheaper than authoring an accepted record, and that the
floor "does not defeat a deliberate bypass" — its standard is that a
reviewer should read the claims record itself rather than infer one from
a green publish. This file is that record: the bypass is deliberate,
its reason is stated, and no review verdict is claimed.

## Non-claims

- No quality, real-host, or claims-review proof is carried forward from
  the 2026-08-28 attempt. The new run establishes its own.
- The superseded record's real-host checklist is not discharged by this
  file.
