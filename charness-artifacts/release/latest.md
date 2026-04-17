# Release Surface Check
Date: 2026-04-17

## Scope

Patch release after fixing prerelease-tag handling in the release probe and
installed CLI update notice surfaces.
No tag or published GitHub release has been created in this slice.

## Current Version

- previous version: `0.1.1`
- target version: `0.1.2`
- packaging manifest: `0.1.2`
- checked-in Claude plugin manifest: `0.1.2`
- checked-in Codex plugin manifest: `0.1.2`
- Claude marketplace metadata: `0.1.0`
- Codex marketplace source path: `./plugins/charness`

## Surface Status

- `bump_version.py --part minor` updated `packaging/charness.json` and synced
  checked-in plugin manifests.
- `current_release.py` reports no version drift across packaging, checked-in
  plugin manifests, and marketplace metadata.
- `check_real_host_proof.py` reports no configured real-host proof trigger for
  the current version-only slice.

## Release Scope

- Preserves prerelease suffixes such as `v1.2.3-rc.1` in the shared release
  probe helper instead of truncating them to the numeric core.
- Preserves the same prerelease tag in installed CLI update notices so the
  operator sees the actual upstream release tag that triggered the notice.
- Adds direct helper and managed-install coverage for prerelease release tags.

## Verification

- `./scripts/run-quality.sh` passed for the final release slice.
- `python3 scripts/run-slice-closeout.py --repo-root .` passed for the final
  release slice.
- `python3 scripts/validate-packaging.py --repo-root .` passed after syncing
  the checked-in install surface at `0.1.2`.

## User Update Steps

- After merge/push, operators should run `charness update`.
- Claude plugin users can refresh with `/plugin marketplace update corca-charness`.
- Codex plugin users should refresh from the checked-in `plugins/charness`
  source path according to their local plugin install flow.

## Open Risks

- No real-host proof was required by the configured release trigger for this
  slice. A future release touching integrations or install/update scripts should
  re-run the real-host checklist from `.agents/release-adapter.yaml`.
- Complex release tags outside the current semver-like prerelease shape remain
  deferred.
