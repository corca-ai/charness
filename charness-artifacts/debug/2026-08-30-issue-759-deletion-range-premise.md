# Issue #759 Deletion-Range Debug Premise Check
Date: 2026-08-30

## Problem

A critique packet bound to a commit or endpoint range used to require every changed path while also requiring current file bytes for every path. A range containing a deletion therefore had no valid declaration.

## Correct Behavior

Added and modified paths bind their reviewed bytes. Deleted paths remain members of the exact changed-path set and bind the removed pre-image plus a typed `deleted` disposition. Omitting a changed path or changing a bound input must refuse verification.

## Observed Facts

- Commit `67555154eeb90766857125b34ac30151dc18d4ad` introduced deletion pre-image binding in `scripts/reviewed_input_identity.py` with direct regression coverage.
- The current public reference documents `reviewed_content[].disposition: deleted` and states that the hash answers what was removed.
- The implementation remains on published main `e7a7d2f25b2839b3c392789fb44d3fad2d2c2fcf`.

## Reproduction

Focused tests construct temporary Git repositories, commit one edit and one deletion, then exercise both `HEAD^..HEAD` and single-commit `HEAD` identity modes. Separate negative controls declare the wrong path set and mutate a declared input after capture.

## Candidate Causes

- Treating every reviewed path as current filesystem bytes made deletion unrepresentable.
- Removing deleted paths from the manifest broke exact range membership instead of repairing identity semantics.
- Replacing the range with an unbound `prepared-for` label avoided the crash but weakened the evidence identity.

## Hypothesis

If deletion is a typed reviewed-content disposition whose digest binds the range pre-image, the exact changed-path set can include deletions without weakening range identity.

## Verification

The following focused run passed four tests on published main:

```text
pytest -q \
  tests/test_reviewed_input_identity_binding.py::test_a_committed_range_with_a_deletion_binds_the_preimage_instead_of_refusing \
  tests/test_reviewed_input_identity_binding.py::test_a_single_commit_that_deletes_resolves_its_preimage_from_the_parent \
  tests/test_critique_verify_packet.py::test_committed_ref_packet_refuses_mismatched_declared_paths \
  tests/test_reviewed_input_identity_binding.py::test_reviewed_input_binding_stales_only_for_declared_input
```

Result: `4 passed in 1.07s`.

## Root Cause

The identity owner modeled a reviewed path only as present content. It did not model removal as a first-class state with a readable pre-image, so two individually sound checks formed an impossible intersection.

## Prevention

Keep range membership exact, retain typed deletion pre-image tests for range and commit forms, and retain independent omission and staleness refusals. Consumer-repository Git topology remains outside this capability proof.
