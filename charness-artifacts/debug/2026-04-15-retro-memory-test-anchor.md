# Debug Review
Date: 2026-04-15

## Problem

`./scripts/run-quality.sh --review` failed in
`tests/quality_gates/test_retro_memory.py::test_retro_memory_surfaces_reference_recent_lessons_digest`
because `charness-artifacts/retro/recent-lessons.md` no longer contained the
literal text `plugin export`.

## Correct Behavior

Given `recent-lessons.md` is the compact digest refreshed from the latest durable
retro artifact, when a newer session retro updates the digest, then the quality
gate should verify the durable memory seam and digest structure without pinning a
single historical lesson as permanent content.

## Observed Facts

- `recent-lessons.md` currently points at
  `charness-artifacts/retro/2026-04-15-hitl-quality-handoff.md`.
- That source retro focuses on routing `quality` `NON_AUTOMATABLE`
  recommendations into `hitl`, not checked-in plugin export drift.
- `docs/retro-self-improvement-spec.md` says `refresh_recent_lessons.py`
  refreshes the digest from the latest durable retro artifact and lists bounded
  rolling preservation as a probe question, not a fixed decision.
- The failing test still asserted that `plugin export` must appear in the
  current digest.

## Reproduction

```bash
python3 -m pytest -q tests/quality_gates/test_retro_memory.py
```

The command failed before the test anchor was updated.

## Candidate Causes

- The digest refresh contract changed from a static lesson file to latest-retro
  generated content, but the test kept a historical content assertion.
- `recent-lessons.md` was accidentally overwritten with the wrong retro source.
- The current product contract really requires preserving selected recurring
  traps across refreshes, but that requirement is still only a probe question.

## Hypothesis

If the digest is meant to reflect the latest durable retro, then replacing the
historical `plugin export` assertion with structural checks for the digest
sections and source link should preserve the intended memory-seam coverage while
allowing legitimate retro refreshes.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_retro_memory.py` passes after
  the assertion change.
- The revised test still checks that `AGENTS.md`, `docs/handoff.md`,
  `skills/public/retro/SKILL.md`, and the retro adapter contract all reference
  the recent-lessons seam.

## Root Cause

The test conflated one historical lesson with the stable digest contract. The
stable invariant is that repo memory points at a compact recent-lessons digest
with recognizable sections and source provenance. The literal `plugin export`
lesson is important history, but the current implementation does not preserve
every historical lesson in `recent-lessons.md`.

## Prevention

- Keep content-specific assertions in fixtures that construct the expected
  source retro locally.
- Keep repo-state tests focused on stable structure and source provenance unless
  the product explicitly chooses a bounded rolling digest that preserves named
  recurring traps.

## Related Prior Incidents

- `2026-04-11-plugin-export-drift.md` — the historical incident behind the stale
  assertion remains valid, but it is no longer the permanent current digest
  invariant.
