# Supply-Chain Overview

Use the `security` lens in `quality` to separate repo-local guarantees from
networked audit work.

## What The Repo Can Own Deterministically

- dependency manifests and lockfiles stay aligned
- one package-manager surface stays unambiguous
- committed tooling metadata does not silently drift away from the package
  manager the repo actually uses

These are good repo-owned gates because they run offline and fail for concrete
reasons.

## What Usually Needs A Separate Follow-Up

- vulnerability database lookups
- registry compromise or typosquat investigation
- trust decisions about new publishers or scopes
- CI policies for dependency-review bots or hosted scanners

Those are still real security concerns, but they depend on outside services,
fresh advisories, or human judgment. `quality` should call them out honestly
instead of pretending one local script proves them.

## Current `charness` Slice

`charness` now ships `scripts/check-supply-chain.py` as the first offline gate
for this lens.

It currently checks:

- JavaScript manifest and lockfile alignment for npm, pnpm, yarn, and bun
- Python `pyproject.toml` dependency declarations against `uv.lock`
- ambiguous multi-lockfile situations that make the active package manager
  unclear

It does not yet do online vulnerability lookups. Treat that as a separate
follow-up seam, not as a hidden promise.
