# Run Quality Changed-Path Suppression Debug
Date: 2026-05-22

## Problem

Read-only quality used changed-path discovery to decide whether
`check-coverage` could be skipped, but failed git discovery commands were
treated as empty output.

## Correct Behavior

Given `./scripts/run-quality.sh --read-only` is deciding whether coverage is
needed, when local changed-path discovery fails, then the runner should treat
coverage relevance as unknown and queue `check-coverage` fail-closed. A failed
discovery command should print the command, exit code, stdout, and stderr.
Successful discovery with no coverage-relevant paths should still skip
`check-coverage`.

## Observed Facts

- `collect_quality_changed_paths()` used `|| true` after upstream diff,
  unstaged diff, staged diff, and untracked file listing.
- `coverage_relevant_changes_present()` consumed the collector with process
  substitution, so a producer failure would not reach the caller even if the
  collector started returning nonzero.
- In read-only mode, the main queue only added `check-coverage` when
  `coverage_relevant_changes_present()` returned success.
- Fresh-eye review confirmed the cheapest safe behavior is to run coverage on
  discovery failure, not make every read-only run run coverage.

## Reproduction

Use a seeded quality-runner repo with `repo/bin/git` first on `PATH`. Make fake
`git diff --name-only` exit `42` with `forced changed-path failure`, then run
`./scripts/run-quality.sh --read-only` with `QUALITY_FAIL_LABEL=check-coverage`.
Before the fix, `check-coverage` could be skipped. After the fix, the runner
prints the changed-path discovery diagnostic and queues `check-coverage`, whose
planted failure surfaces as `FAIL check-coverage`.

## Candidate Causes

- The changed-path collector treated optional upstream absence and required
  local discovery failures as the same kind of non-blocking condition.
- Process substitution hid the collector exit status from the coverage selector.
- The read-only coverage decision optimized for local cost before proving the
  selector's input state.

## Hypothesis

If changed-path discovery output is materialized before classification, and
required git command failures make the collector return nonzero, then
read-only quality can fall back to `check-coverage` when changed state is
unknown while preserving the README-only skip path.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_quality_runner.py -k 'read_only or full_runs_check_coverage or full_surfaces_planted_check_coverage_regression'` passed.
- `ruff check tests/quality_gates/test_quality_runner.py` passed.
- `./scripts/check-shell.sh` passed.

## Root Cause

The coverage selector represented failed changed-path discovery as an empty
changed-path set. The shell implementation also used process substitution, so
the caller could not distinguish "no relevant paths" from "the discovery
producer failed."

## Detection Gap

- read-only quality runner | no fake-git test for changed-path discovery
  failure before the coverage skip decision | add a regression that plants a
  coverage failure and proves failed discovery queues `check-coverage`.
- affected-test selection guidance | no explicit rule for selector input
  discovery failure | document that failed selector discovery must run the
  broader gate or fail with diagnostics.

## Sibling Search

- Mental model: an optimization that produces no candidates is equivalent to
  an optimization that could not compute candidates.
- fixed now: mutation changed-file diff failure no longer publishes a fill-only
  sample.
- fixed now: read-only quality changed-path discovery no longer skips coverage
  when git diff/listing fails.
- still open: shell markdown, internal-link, and secret gates can pass empty if
  their tracked-file listing fails.
- checked non-blocker: Python changed-surface helpers use `surfaces_lib.py`
  and already fail closed; the follow-up there is diagnostic richness, not
  swallowed failure.

## Seam Risk

- Interrupt ID: run-quality-changed-path-suppression
- Risk Class: contract-freeze-risk
- Seam: git changed-path discovery -> read-only quality coverage selection
- Disproving Observation: fake `git diff --name-only` failure now queues
  `check-coverage` and surfaces a planted coverage failure.
- What Local Reasoning Cannot Prove: whether maintainers prefer hard failure
  instead of running the broader safety gate for every selector failure.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Changed-path and affected-test selectors must not collapse failed input
discovery into an empty set. For cost-saving selectors, the safe fallback is to
run the broader deterministic gate; for publish/proof selectors, fail nonzero
before publishing derived state.

## Related Prior Incidents

- `2026-05-22-mutation-changed-diff-suppression.md`: failed changed-file
  discovery was represented as an empty mutation sample priority set.
- `2026-05-22-release-diff-failure-suppression.md`: failed release diff
  discovery was represented as an empty release delta.
