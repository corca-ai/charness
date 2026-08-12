# Issue 588 Policy-Absent Dogfood Debug
Date: 2026-08-13

## Problem

The shipped public-skill dogfood helper raised an uncaught validation traceback
when run in a consumer repository that does not own Charness's internal public
skill validation policy.

## Correct Behavior

Only a nonexistent `docs/public-skill-validation.json` is a legitimate consumer
boundary: report typed `not-applicable-missing-public-skill-validation-policy`
with an empty matrix. A present-but-invalid or non-file policy remains an error.

## Observed Facts

- The helper loaded the policy before producing a report.
- A synthetic consumer with only `skills/support/x/` reproduced the traceback.
- The policy is producer-owned; its absence does not prove a clean dogfood matrix.

## Reproduction

Create a repository containing only `skills/support/x/`, then run the shipped
quality helper with `--repo-root <consumer> --detail`. Before this repair it
raised `ValidationError: missing docs/public-skill-validation.json`; after it
returns the typed empty-matrix applicability result.

## Candidate Causes

- The CLI treated every validation-policy failure as a producer-repo invariant.
- Matrix construction had no preflight representation for a repository outside
  that policy's ownership boundary.
- The wrapper resolved requested skill IDs before it could report the policy
  boundary, making the legitimate consumer case unreachable.

## Hypothesis

A policy-existence preflight, shared by root and shipped quality wrappers, can
make the legitimate absence explicit without weakening malformed-policy errors.

## Verification

- Root human/detail, quality summary/detail, and plugin detail return the typed
  empty-matrix result for the synthetic consumer.
- A policy path that is a directory remains a validation error.
- Policy-present unknown skill IDs remain errors.
- Focused public-skill dogfood and YAML-output suites: 43 passed.

## Root Cause

The CLI treated producer-owned policy absence as an unhandled exceptional path
instead of a typed applicability boundary.

## Invariant Proof

- Producer proof: `policy_applicability_report` distinguishes nonexistent from
  existing policy paths before matrix construction.
- Consumer proof: subprocess tests exercise root, skill, and plugin entrypoints
  against an actual policy-absent consumer shape.
- Non-claims: malformed-policy error presentation and any real consumer impact
  were not changed or measured.

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: prove
- Handoff Artifact: charness-artifacts/critique/2026-08-13-issue-588-policy-absent-dogfood-resolution.md

## Prevention

Public helpers must model legitimate out-of-scope repository shapes as typed
results, while preserving errors for present but invalid producer-owned state.
