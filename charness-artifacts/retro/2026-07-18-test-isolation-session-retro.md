# Session Retro
Date: 2026-07-18

## Mode

session

## Context

This slice followed a broad-suite shared-checkout race and the user's question
about deeper coupling. It converted the lesson from a one-off test repair into
a correct-by-construction rule: standing tests treat the source checkout as
read-only input, while writes happen in a minimal temporary repository.

## Evidence Summary

- `charness-artifacts/quality/2026-07-18-test-isolation-quality.md` records the
  gate inventory, runtime budget, structural packet, and chosen enforcement
  posture.
- `charness-artifacts/critique/2026-07-18-test-isolation-critique.md` records
  fresh-eye findings that narrowed the detector contract and closed class,
  alias, `Path.open`, and false-positive gaps before the broad suite.
- The locked closeout completed with 4,735 tests passing, and the process-level
  seed-cache tests proved build-once plus stale/partial recovery behavior.
- Packet Consumed: `charness-artifacts/retro/2026-07-18-061104-packet.md`.

## Waste

The initial detector draft tried to express the whole isolation principle in a
finite AST check. Review showed that this both overclaimed the guarantee and
missed ordinary spellings of the same direct-path write. The avoidable rework
was designing the detector before separating the portable rule, the finite
ratchet, and the dynamic concurrency proof.

## Critical Decisions

- Make the source checkout read-only the portable authoring rule; keep the AST
  checker explicitly limited to direct `pathlib` writes rooted in the checkout.
- Extend the existing early isolation gate instead of adding a new standing
  gate, preserving runtime and ownership clarity.
- Prove lock and recovery semantics with spawned processes, not static source
  inspection or a copy-heavy broad fixture.

## Expert Counterfactuals

- Engelbart's system-improving lens would design the method, language, and tool
  together: state the read-only-checkout rule, provide the minimal temporary
  repository pattern, and ratchet the reproduced escape in the same slice.
- Ousterhout's complexity lens would keep one owner per invariant: the existing
  isolation gate owns early direct-write detection, while behavioral tests own
  seed-cache concurrency. Neither surface pretends to own all filesystem side
  effects.

## Sibling Search

- same layer: tests deriving paths from the real checkout root | decision: same waste, fix now | proof: the extended repo-wide checker found one remaining writer, which now uses a minimal temporary repository
- abstraction up: public quality testability guidance | decision: same waste, fix now | proof: the quality reference now states the read-only-checkout rule and temporary-repository pattern
- specialization down: class methods, imported aliases, `Path(ROOT)`, `joinpath`, `Path.open`, and safe local `ROOT` names | decision: same waste, fix now | proof: focused positive and negative fixtures cover each spelling and the false-positive boundary
- mental-model siblings: xdist seed-cache locking and recovery | decision: same waste, fix now | proof: spawned-process and stale/partial-state tests exercise behavior through the public cache helper

## Next Improvements

- workflow: run the existing isolation checker while authoring or reviewing any
  test that executes a mutating CLI or materializes repo artifacts.
- capability: keep finite static ratchets paired with dynamic tests at process,
  filesystem, or concurrency boundaries; do not market either as a sandbox.
- memory: retain the portable read-only-checkout rule, executable fixtures,
  quality record, critique, and this sibling scan in the same commit.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-test-isolation-session-retro.md
