# Release Surface Check
Date: 2026-04-17

## Scope

Minor release after adding a maintained `glow` install/runtime surface for
markdown preview seams used by `narrative` and `quality`, plus release-time
test hardening so local host installs do not contaminate degraded fallback
proof.
No tag or published GitHub release has been created in this slice.

## Current Version

- previous version: `0.1.2`
- target version: `0.2.0`
- packaging manifest: `0.2.0`
- checked-in Claude plugin manifest: `0.2.0`
- checked-in Codex plugin manifest: `0.2.0`
- Claude marketplace metadata: `0.2.0`
- Codex marketplace source path: `./plugins/charness`

## Surface Status

- `bump_version.py --part minor` updated `packaging/charness.json` and synced
  checked-in plugin manifests.
- `current_release.py` reports no version drift across packaging, checked-in
  plugin manifests, and marketplace metadata.
- `check_real_host_proof.py` reports no configured real-host proof trigger for
  the current version-only slice.

## Release Scope

- Adds a repo-owned `glow` tool manifest and install route so `narrative` and
  `quality` users get a maintained runtime recommendation instead of ad hoc
  install prose.
- Adds a `narrative` recommendation wrapper so both `narrative` and `quality`
  expose the same install/verify seam for rendered markdown proof.
- Hardens markdown-preview tests so degraded fallback proof stays isolated even
  when the maintainer host has `glow` installed locally.

## Verification

- `./scripts/run-quality.sh` passed for the final release slice.
- `python3 scripts/run-slice-closeout.py --repo-root .` passed for the final
  release slice.
- `python3 scripts/validate-packaging.py --repo-root .` passed after syncing
  the checked-in install surface at `0.2.0`.

## User Update Steps

- After pull/push, operators should run `charness update`.
- Claude plugin users can refresh with `/plugin marketplace update corca-charness`.
- Codex plugin users should refresh from the checked-in `plugins/charness`
  source path according to their local plugin install flow.

## Open Risks

- No real-host proof was required by the configured release trigger for this
  slice. A future release touching broader install/update scripts or published
  operator docs should re-run the real-host checklist from
  `.agents/release-adapter.yaml`.
- `glow` is now a maintained install surface, but rendered preview is still an
  opt-in helper rather than a default workflow step; choosing the default
  caller remains deferred.
