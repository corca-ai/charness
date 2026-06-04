# Release Review: 0.18.0

Reviewer: subagent `019e92a1-366d-7be2-9ce2-0f5568e81d75`.

## Scope

Fresh-eye release review for publishing Charness 0.18.0 from current `main`,
with emphasis on the new `nose` quality advisory integration, install/update
surface, generated plugin mirrors, and operator release instructions.

## Findings

- Minor bump `0.17.0 -> 0.18.0` is appropriate because this ships a new
  maintained advisory validation surface for `quality`.
- Version surfaces were consistent at 0.17.0 before the bump: packaging,
  Claude plugin, Codex plugin, and marketplace metadata had no drift.
- Generated plugin mirrors for `nose` are present and synced.
- Release quality passed before release prep with `72 passed, 0 failed`.
- Caveat: local `inventory-nose-clones` proof used the degraded missing-binary
  advisory path on this machine unless `NOSE_BIN` is explicitly pointed at the
  maintainer checkout.

## Blockers

- Fixed before publish: `.agents/release-adapter.yaml` still described 0.17.0
  and older release notes.
- Fixed before publish: the release-time real-host checklist still centered on
  `tokei`; 0.18.0 needs `nose` doctor/install/update/advisory proof.

## Required Checks

- After bump/sync, `current_release.py` must report every release surface at
  0.18.0 with no drift.
- Re-run `./scripts/run-quality.sh --release` after the bump.
- Re-run fresh-checkout probes.
- Keep `nose` real-host proof honest: missing `nose` must be advisory, install
  guidance must point at the upstream release installer, and a present `nose`
  binary must drive only advisory clone-family inventory.

## Disposition

Proceed after applying the release-adapter update and passing the release helper
preflight. Do not claim that `nose` is installed on every operator machine;
claim only that update/install/doctor guidance exists and `quality` degrades
cleanly when the binary is absent.
