# v0.5.28 Post-Release Critique

## Execution

- Fresh-Eye Satisfaction: `parent-delegated`
- Target: `release-critique`
- Release: `v0.5.28`
- Release commit: `8a6281f Release charness 0.5.28`
- Packet Consumed:
  `charness-artifacts/critique/2026-05-17-v0-5-28-post-release-critique-packet.md`

## Release Scope

`v0.5.28` published the pending `main` changes since `v0.5.27`, including
gather acquisition fallback fixes, quality behavior/runtime-lens work,
critique-packet improvements, mutation diagnostics, packaging refresh, and a
release-time mutation summary helper refactor.

## Surface-Lock Inventory

- generated packaging/plugin surfaces:
  `packaging/charness.json`, `.claude-plugin/marketplace.json`,
  `plugins/charness/.claude-plugin/plugin.json`,
  `plugins/charness/.codex-plugin/plugin.json`
- public GitHub release:
  `https://github.com/corca-ai/charness/releases/tag/v0.5.28`
- release artifact:
  `charness-artifacts/release/latest.md`
- helper surface changed during release:
  `scripts/check_mutation_score.py` and
  `plugins/charness/scripts/check_mutation_score.py`

## Findings

### Act Now For v0.5.28

- The public GitHub release body was initially only a generated Full Changelog
  link. That was too sparse for operators because the release spans gather
  behavior, quality guidance, runtime-lens work, mutation diagnostics, and
  packaging surfaces.

Resolution: edited the existing `v0.5.28` GitHub release body in place with
`Highlights`, `Update`, `Validation`, and `Known Follow-Up` sections. No new
patch release was needed because the published artifact bits, tag, and manifest
versions were correct.

- The release should not imply real-host proof is complete. The release artifact
  still tracks real-host update proof for the Cautilus doctor/sync-support path.

Resolution: the public release body now says repo quality gates passed and that
real-host update proof remains tracked internally. The real-host trigger may be
too broad for this release, but that belongs to a later surface-classification
slice.

### Bundle Anyway

- The post-release critique packet needed durable handling.

Resolution: this result artifact and the packet are checked in together.

### Over-Worry

- No new patch release is necessary. `current_release.py` reports `0.5.28`
  across packaging, Claude plugin, Codex plugin, and marketplace metadata with
  no drift, and the public GitHub release exists.
- No fresh-checkout blocker exists because the release adapter declares no
  fresh-checkout probes.

### Valid But Defer

- Harden the release helper so GitHub releases cannot publish with only a Full
  Changelog link when the release artifact contains operator-relevant notes.
- Tighten the real-host proof trigger so mutation-score plugin helper exports
  do not inherit Cautilus/control-plane proof expectations unless the actual
  install/runtime surface moved.
- Consider a structured real-host proof artifact so `published`, `operator
  verified`, and `support materialized` cannot be conflated.

## Proof

- `gh release view v0.5.28 --repo corca-ai/charness` showed the initial body was
  only a Full Changelog link.
- `gh release edit v0.5.28 --repo corca-ai/charness --notes ...` updated the
  public release body.
- `current_release.py` reported version `0.5.28` across packaging and plugin
  surfaces with no drift.

## Next Move

Commit and push this post-release critique record. Track release-helper note
quality and real-host trigger precision as separate hardening work.
