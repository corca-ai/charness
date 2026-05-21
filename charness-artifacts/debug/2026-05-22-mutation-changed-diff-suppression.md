# Mutation Changed-File Diff Suppression Debug
Date: 2026-05-22

## Problem

Mutation sampling treated a failed changed-file `git diff` as an empty changed
set, so the sampler could replace the changed-file obligation with fill samples.

## Correct Behavior

Given `MUTATION_BASE_SHA` is set, when
`git diff --name-only <base>..<head> -- <mutation pathspecs>` fails, then
`scripts/sample_mutation_files.py` must exit nonzero with the failed command
details before writing `reports/mutation/sample.json`, <!-- reproduction-source -->
`reports/mutation/sample.md`, <!-- reproduction-source --> or rewriting
`cosmic-ray.toml`. Without a base SHA, the existing no-changed-priority
behavior should remain a no-op.

## Observed Facts

- `list_changed()` caught `subprocess.CalledProcessError`, wrote stderr, and
  returned `[]`.
- `main()` filtered that empty list into `changed_before_coverage`, then selected
  from the fill pool and published the sample manifest/config.
- The release diff/base-ref fixes established the same fail-closed rule: failed
  proof-input discovery must not be represented as an empty input.
- Fresh-eye review required a focused unit test, a CLI mutation-boundary test,
  and compatibility tests for empty base SHA and successful empty/non-empty diff
  output.

## Reproduction

Create a fixture repo with one mutation-pool file and `cosmic-ray.toml`, set
`MUTATION_BASE_SHA=base-sha` and `MUTATION_HEAD_SHA=head-sha`, put a fake `git`
first on `PATH` that exits `42` for `git diff --name-only`, then run
`scripts/sample_mutation_files.py --repo-root <repo> --skip-coverage`.

## Candidate Causes

- The sampler treated changed-file discovery as optional because changed-file
  prioritization itself is optional when no base SHA is provided.
- The score checker made changed-file exclusions fatal later, but the sampler
  could suppress discovery failure before exclusions were recorded.
- Tests covered changed-file exclusion classification and manifest reporting,
  but not the git diff command failure path.

## Hypothesis

If `list_changed()` raises `SystemExit` with base/head/command/exit/stdout/stderr
when git diff fails, then the sampler cannot silently publish a fill-only sample
from an unknown changed-file set.

## Verification

- Focused pytest passed for mutation sampling, including unit coverage for
  successful diff parsing, empty-base no-op, failed diff diagnostics, and CLI
  no-write behavior on failed changed-file diff.
- `ruff check scripts/sample_mutation_files.py tests/quality_gates/test_quality_mutation_sampling.py`
  passed.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.

## Root Cause

The sampler conflated two states: "no base SHA was provided, so changed-file
priority is disabled" and "a base SHA was provided, but changed-file discovery
failed." Only the first state is safe to treat as an empty changed set.

## Detection Gap

- mutation changed-file discovery | failed git diff returned `[]` | add
  unit-level fail-closed diagnostics.
- sampler publication boundary | no CLI regression proved failure happened
  before manifest/config writes | add fake-git CLI no-write regression.
- compatibility | empty base SHA no-op and successful diff parsing were
  implicit | pin both with focused tests.

## Sibling Search

- Mental model: optional changed-file prioritization means changed-file
  discovery failure can be advisory.
- fixed now: mutation sampler changed-file diff failure exits before
  manifest/config publication.
- fixed earlier: release unreleased-path diff and release base-ref lookup/fetch
  failures exit before dry-run output or execute mutation.
- still open: read-only quality changed-path discovery uses shell `|| true`
  fallbacks and needs a separate gate design.
- still open: release post-create verification records `not_checked` after
  external mutation and needs recovery design.

## Seam Risk

- Interrupt ID: mutation-changed-diff-suppression
- Risk Class: contract-freeze-risk
- Seam: GitHub/scheduled mutation base SHA -> local changed-file discovery -> mutation sample manifest
- Disproving Observation: fake `git diff` failure exits before sample manifest
  or `cosmic-ray.toml` writes.
- What Local Reasoning Cannot Prove: whether the next scheduled run's selected
  base/head pair has zero changed-file eligibility exclusions after this local
  hardening.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Differentiate "feature disabled" from "discovery failed" in sampling and quality
helpers. When a later gate makes missing changed-file coverage fatal, the
upstream discovery command must fail closed instead of publishing empty input.

## Related Prior Incidents

- `2026-05-22-release-diff-failure-suppression.md`: release diff failure
  collapsed unknown release delta into no real-host proof.
- `2026-05-22-release-base-ref-fallback-suppression.md`: release base-ref
  lookup/fetch failure collapsed unknown previous-tag state into a branch
  fallback.
- `2026-05-21-mutation-subprocess-coverage.md`: mutation sampling made
  changed-file exclusions visible but still deferred this diff-failure path.
