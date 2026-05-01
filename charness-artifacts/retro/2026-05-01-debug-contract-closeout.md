# Debug Contract Closeout Retro
Date: 2026-05-01

## Mode

session

## Context

Issue #90 exposed the same source-of-truth drift pattern seen in the recent
closed-issue analysis: `debug` scaffold output, skill docs, validator behavior,
and exported consumer layouts were not one tested contract.

## Evidence Summary

- GitHub issue #90.
- Bounded premortem reviewers for compatibility, exported-layout coverage, and
  operator clarity.
- Focused debug scaffold and validator tests.
- `run_slice_closeout.py` completed after plugin export sync.

## Waste

- The first fix tried a hyphenated Python alias for old materialized paths, but
  the repo's filename gate correctly rejected non-snake-case Python files.
- The better structural fix was to make scaffold resolution tolerate old
  hyphenated layouts without adding a new non-conforming source file.

## Critical Decisions

- Keep `latest.md` strict as the current pointer schema.
- Treat dated debug records as legacy debug memory: core sections and order are
  checked, but older extra sections do not block new investigations.
- Prove the consumer path by running the exported plugin scaffold and its
  emitted validator command from a clean target repo.

## Expert Counterfactuals

- Gary Klein lens: start from the field failure and ask which cue would have
  made the wrong path obvious. The missing cue was the artifact path in
  validator errors, so path-bearing failures became ship criteria.
- Daniel Kahneman lens: avoid overcorrecting from one Ceal failure into a broad
  migration project. Historical debug artifacts stay readable; new strictness
  applies only to the current pointer.

## Next Improvements

- workflow: when a scaffold emits a command, test that exact emitted command
  from an exported plugin layout, not only from the source checkout.
- capability: keep compatibility in resolution logic when possible instead of
  adding duplicate helper files that violate repo conventions.
- memory: preserve this as another example of fixing source-of-truth drift by
  turning the consumer journey into an executable fixture.

## Persisted

yes `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`
