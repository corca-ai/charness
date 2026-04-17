# Release Surface Check
Date: 2026-04-17

## Scope

Patch release surface bump after the public-spec executable-proof cleanup.
No tag or published GitHub release has been created in this slice.

## Current Version

- previous version: `0.0.7`
- target version: `0.0.8`
- packaging manifest: `0.0.8`
- checked-in Claude plugin manifest: `0.0.8`
- checked-in Codex plugin manifest: `0.0.8`
- Claude marketplace metadata: `0.0.8`
- Codex marketplace source path: `./plugins/charness`

## Surface Status

- `bump_version.py --part patch` updated `packaging/charness.json` and synced
  checked-in plugin manifests.
- `current_release.py` reports no version drift across packaging, checked-in
  plugin manifests, and marketplace metadata.
- `check_real_host_proof.py` reports no configured real-host proof trigger for
  the current version-only slice.

## Release Scope

- Includes the public-spec executable-proof tightening and the inventory fix
  that now reads real `run:shell` fences.
- Includes the follow-up quality artifact refresh from the live rerun.

## Verification

- `./scripts/run-quality.sh --review` passed with `38 passed, 0 failed`.
- `current_release.py` reports no release-surface drift at `0.0.8`.

## User Update Steps

- After merge/push, operators should run `charness update`.
- Claude plugin users can refresh with `/plugin marketplace update corca-charness`.
- Codex plugin users should refresh from the checked-in `plugins/charness`
  source path according to their local plugin install flow.

## Open Risks

- No real-host proof was required by the configured release trigger for this
  slice. A future release touching integrations or install/update scripts should
  re-run the real-host checklist from `.agents/release-adapter.yaml`.
