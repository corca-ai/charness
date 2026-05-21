# Session Retro: Release Real-Host Config Fail-Closed

Date: 2026-05-22
Mode: session

## Context

This session continued the release proof suppression scan by fixing publish
behavior for broken real-host proof configuration and proof-builder failures.

## Evidence Summary

- Debug artifact:
  `charness-artifacts/debug/2026-05-22-release-real-host-config-suppression.md`.
- Fresh-eye critique caught that the first patch proved broken payloads but not
  proof-builder exceptions or dry-run no-trigger compatibility.
- Closeout: `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
  completed.
- Quality: `./scripts/run-quality.sh --read-only` passed with `65` checks.

## Waste

- The first implementation claimed the proof builder cannot run path before a
  test exercised an actual builder exception.
- Compatibility for no-trigger dry-run repos without `.agents/surfaces.json`
  was implied by execute tests but not directly pinned.

## Critical Decisions

- Keep path-glob/no-trigger release adapters compatible without a surfaces
  manifest.
- Fail closed only when configured surface triggers are broken or the proof
  builder raises.
- Leave `_release_base_ref()` fallback, mutation changed-file diff failure, and
  post-create verification as separate slices.

## Expert Counterfactuals

- Gary Klein lens: enumerate all visible modes for a new fail-closed claim:
  broken payload, thrown exception, dry-run, and execute mutation boundary.
- Daniel Kahneman lens: treat compatibility claims as separate hypotheses, not
  as a free consequence of positive-path execute tests.

## Next Improvements

- workflow: when replacing an advisory fallback with fail-closed behavior, add
  one test for returned error payloads and one for thrown exceptions.
- workflow: when moving a gate before dry-run output, add a dry-run
  compatibility assertion for the non-trigger case.
- memory: keep the next release suppression slice focused on `_release_base_ref()`
  known-tag fetch fallback before post-create recovery semantics.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`
