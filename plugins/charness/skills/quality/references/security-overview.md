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

`charness` now ships `<repo-root>/scripts/check_supply_chain.py` as the first offline gate
for this lens.

It currently checks:

- JavaScript manifest and lockfile alignment for npm, pnpm, yarn, and bun
- Python `<repo-root>/pyproject.toml` dependency declarations against `uv.lock`
- ambiguous multi-lockfile situations that make the active package manager
  unclear

It does not yet do online vulnerability lookups. Treat that as a separate
follow-up seam, not as a hidden promise.

## Secret Scanner Choice

For repo-local secret scanning, `quality` should not pretend there is one
universal winner.

- prefer `gitleaks` when the repo is not already Node-based and wants a
  binary-first gate with git, directory, and stdin scan modes plus baseline
  and allowlist support
- prefer `secretlint` when the repo already carries Node tooling and needs
  pluggable rules, rule-level suppression, or custom rule packages

`charness` now treats `gitleaks` as the lower-friction first choice for
npm-light repos, but keeps `secretlint` as an honest fallback where the repo
already vendors it.
