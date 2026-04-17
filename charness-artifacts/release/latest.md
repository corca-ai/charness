# Release Surface Check
Date: 2026-04-17

## Scope

Minor release surface bump after adding the `markdown-preview` support
capability, tightening the `premortem` subagent contract, and refocusing the
public `quality` skill on structure-first review and explicit gate-promotion
routing.
No tag or published GitHub release has been created in this slice.

## Current Version

- previous version: `0.0.8`
- target version: `0.1.0`
- packaging manifest: `0.1.0`
- checked-in Claude plugin manifest: `0.1.0`
- checked-in Codex plugin manifest: `0.1.0`
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

- Includes the new `markdown-preview` support capability for rendered Markdown
  QA artifacts.
- Includes the follow-up hardening for `markdown-preview`, including explicit
  backend rejection and stronger manifest provenance.
- Includes the public `premortem` contract change that now requires the
  canonical subagent path instead of silently degrading into same-agent local
  review.
- Includes the `quality` skill follow-up that treats length/duplicate/pressure
  signals as structure-first advisory by default, clarifies when they may still
  promote to deterministic gates, and aligns fresh-eye premortem wording with
  the canonical subagent path.
- Includes the `inventory_public_spec_quality.py` seam extraction that keeps
  the standing file-length gate satisfied without loosening the gate.

## Verification

- `./scripts/run-quality.sh` passed for the final release slice.
- `python3 scripts/run-slice-closeout.py --repo-root .` passed for the final
  release slice.
- `current_release.py` reports no release-surface drift at `0.1.0`.

## User Update Steps

- After merge/push, operators should run `charness update`.
- Claude plugin users can refresh with `/plugin marketplace update corca-charness`.
- Codex plugin users should refresh from the checked-in `plugins/charness`
  source path according to their local plugin install flow.

## Open Risks

- No real-host proof was required by the configured release trigger for this
  slice. A future release touching integrations or install/update scripts should
  re-run the real-host checklist from `.agents/release-adapter.yaml`.
