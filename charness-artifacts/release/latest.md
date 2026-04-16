# Release Surface Check
Date: 2026-04-16

## Scope

Patch release surface bump after the #25-#31 dogfood fixes and retro correction.
No tag or published GitHub release has been created in this slice.

## Current Version

- previous version: `0.0.6`
- target version: `0.0.7`
- packaging manifest: `0.0.7`
- checked-in Claude plugin manifest: `0.0.7`
- checked-in Codex plugin manifest: `0.0.7`
- Claude marketplace metadata: `0.0.7`
- Codex marketplace source path: `./plugins/charness`

## Surface Status

- `bump_version.py --part patch` updated `packaging/charness.json` and synced
  checked-in plugin manifests.
- `current_release.py` reports no version drift across packaging, checked-in
  plugin manifests, and marketplace metadata.
- `check_real_host_proof.py` reports no configured real-host proof trigger for
  the current version-only slice.

## Release Scope

- Includes skill behavior fixes for `quality`, `narrative`, `init-repo`,
  `gather`, and `find-skills` from #25-#31.
- Includes the corrected dogfood retro: charness needs consumer-side dogfood
  fixtures, not only producer-side validation gates.
- Includes local runtime budget recalibration for `specdown` recent-median
  variance.

## Verification

- `./scripts/run-quality.sh` passed with `37 passed, 0 failed` after this
  artifact update.
- Pushed to `origin/main` in commit `36a6530`.

## User Update Steps

- After merge/push, operators should run `charness update`.
- Claude plugin users can refresh with `/plugin marketplace update corca-charness`.
- Codex plugin users should refresh from the checked-in `plugins/charness`
  source path according to their local plugin install flow.

## Open Risks

- No real-host proof was required by the configured release trigger for this
  slice. A future release touching integrations or install/update scripts should
  re-run the real-host checklist from `.agents/release-adapter.yaml`.
