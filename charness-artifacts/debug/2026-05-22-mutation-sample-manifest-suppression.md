# Mutation Sample Manifest Suppression Debug
Date: 2026-05-22

## Problem

`check_mutation_score.py` treated a missing, malformed, or schema-invalid
mutation sample manifest as no changed-file scope gap, so an otherwise passing
mutation score could hide unknown changed-file sampling proof.

## Correct Behavior

Given mutation score closeout depends on the sample manifest for changed-file
scope-gap evidence, when the sample manifest is missing, unreadable, or
schema-invalid, then the score summary must record a blocking signal and the
command must exit nonzero. A valid manifest with `base_sha: null` remains the
explicit representation that changed-file proof was intentionally disabled.

## Observed Facts

- `sample_manifest_scope_gap_details()` returned `([], {})` when the manifest
  was missing, malformed, or not an object.
- `mutation_metrics()` passed when `changed_scope_gap_count == 0`, so unknown
  manifest state became a clean changed-file proof input.
- The sampler-written manifest already carries `base_sha`, which distinguishes
  active changed-file proof from intentionally disabled changed-file proof.
- The sampler previously emitted an empty string when `MUTATION_BASE_SHA` was
  absent, which made the disabled-proof state implicit instead of explicit.
- Focused tests can create an otherwise passing killed-mutant dump with no
  sample manifest, a malformed sample manifest, schema-invalid manifests, or a
  valid `base_sha: null` manifest.

## Reproduction

Run `check_mutation_score.py` with a killed-only Cosmic Ray dump and no
`reports/mutation/sample.json` <!-- reproduction-source -->. Before the fix, the score could pass because no
changed-file scope gaps were found. After the fix, the summary contains
`Blocking signal: mutation sample manifest not found` and exits 1.

## Candidate Causes

- Missing manifest state reused the same empty-list representation as no
  changed-file exclusions.
- The score metrics did not have a separate manifest-proof health flag.
- Existing regressions covered explicit changed-file exclusion keys but not
  missing or malformed sample-manifest input.

## Hypothesis

If sample-manifest parsing returns a manifest issue string for missing,
malformed, non-object, missing-`base_sha`, empty-`base_sha`, or wrong-typed
scope-gap sections, and `mutation_metrics()` requires `sample_manifest_ok`,
then the mutation score cannot pass without explicit sample proof or explicit
disabled changed-file proof.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_quality_mutation_sampling.py tests/quality_gates/test_check_mutation_score_partial.py` passed.
- `ruff check scripts/check_mutation_score.py scripts/mutation_sample_manifest_score_lib.py scripts/sample_mutation_files.py tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_quality_mutation_sampling.py` passed.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.

## Root Cause

The score gate collapsed unknown sample-manifest state into the same data shape
as a valid manifest with no changed-file exclusions.

## Detection Gap

- sample manifest input | no otherwise-passing regression with missing
  `reports/mutation/sample.json` <!-- reproduction-source --> | add a killed-only dump test that exits 1
  and records the missing-manifest blocking signal.
- malformed manifest input | invalid JSON and non-object roots returned no gaps
  | add regressions that exit 1 and record read/parse or root-object blocking
  signals.
- proof-boundary schema | missing or empty `base_sha` and wrong-typed
  exclusion sections could look clean | require `base_sha` to be null or a
  non-empty string and require exclusion sections to be lists of strings.
- disabled changed-file proof | intentional no-base state was implicit | have
  the sampler emit `base_sha: null` when the environment omits the base, and
  allow only that valid disabled-proof representation to pass.

## Sibling Search

- Mental model: no changed-file exclusions found is equivalent to no
  changed-file exclusions present.
- fixed now: missing, malformed, non-object, no-`base_sha`,
  empty-`base_sha`, or wrong-typed scope-gap sections block score closeout.
- checked non-blocker: explicit exclusion arrays still produce the existing
  changed-file scope-gap section.
- deferred: critique artifact changed-path discovery and repo file-listing
  fallback remain separate residuals from the completion audit.

## Seam Risk

- Interrupt ID: mutation-sample-manifest-suppression
- Risk Class: contract-freeze-risk
- Seam: mutation sampler manifest -> score summary -> quality closeout status
- Disproving Observation: killed-only score now exits 1 when the sample manifest
  is missing, malformed, or schema-invalid, and exits 0 only with a valid
  disabled-proof manifest.
- What Local Reasoning Cannot Prove: whether every historical mutation summary
  was generated with a manifest before this gate existed.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep missing proof inputs distinct from empty proof results in score metrics.
When a manifest carries a proof boundary, validate that boundary before using
its absence of findings as a passing signal.

## Related Prior Incidents

- `2026-05-22-mutation-changed-diff-suppression.md`: changed-file diff failure
  could previously become a fill-only mutation sample.
- `2026-05-21-mutation-scope-gap-testability.md`: mutation closeout needed
  clearer distinction between score denominator and scope gaps.
