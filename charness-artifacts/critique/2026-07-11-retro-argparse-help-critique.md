# Critique Review — Retro Argparse Help

Date: 2026-07-11

## Decision Under Review

Clear the 11 missing-help findings owned by the three retro CLIs without
changing their parser or runtime contracts.

## Failure Angles

- Contract drift: descriptions must not alter option names, defaults, types,
  destinations, required flags, or packet-selection behavior.
- Mirror drift: public skill sources and packaged plugin copies must remain
  byte-identical.
- Test fidelity: each distinctive phrase must appear in its own option block,
  not merely elsewhere in usage output.

## Counterweight Pass

- Full-output snapshots would make harmless wrapping and copy edits expensive;
  whitespace-normalized, option-scoped assertions prove the relevant contract.
- A shared parser abstraction or new repo-wide floor is disproportionate to a
  help-only package.
- The remaining findings belong to later cohesive packages rather than this
  change.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/retro/scripts | action: document | note: exactly 11 help strings were added and parser behavior is unchanged.
- F2 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/skills/retro/scripts | action: document | note: all three packaged mirrors are byte-identical to their public sources.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_retro_help.py | action: document | note: wrapping-tolerant assertions bind each changed option to its own distinctive description.
- F4 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/2026-07-11-retro-argparse-help.md | action: defer | note: the remaining 51 findings require separate package selection and proof.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye code review.
- Requested spawn fields: lower-power implementation worker with an independent
  child reviewer; per-agent model metadata was inherited from the active worker.
- Implementation ran in a lower-power delegated worker; its child reviewer ran
  read-only in a separate agent context.
- Host exposure state: metadata-hidden
- Application state: applied — mirror parity, parser-contract preservation,
  option-scoped proof, and focused runtime output were explicitly inspected.

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded reviewer found no blocker, should-fix, or
nice-to-have finding after inspecting sources, mirrors, tests, and live help.

## Boundary Ownership

- Producer: each retro argparse parser owns its option description.
- Consumer: operators and agents invoking telemetry, planning, and packet CLIs.
- Owning surface: the three public scripts, their packaged mirrors, and focused
  executable readback tests.
- Verdict: single-surface
