# Specdown Runtime Budget Debug
Date: 2026-04-16

## Problem

Push-time `./scripts/run-quality.sh` failed at `check-runtime-budget` because
`specdown` recent median moved above the configured budget.

## Correct Behavior

Given a markdown-only retro update, when the pre-push quality gate runs, then
runtime budgets should catch meaningful drift without blocking on a threshold
that is below observed steady-state variance.

## Observed Facts

- Full pre-push first failed with `specdown recent median 5225ms` against a
  `5000ms` budget.
- A targeted `CHARNESS_QUALITY_LABELS=specdown ./scripts/run-quality.sh` sample
  first ran in `3823ms`, then another ran in `7004ms`.
- After a later full pre-push sample, `specdown` ran in `8635ms` and the recent
  median moved to `6284ms`.
- The command passed functionally every time; the failure was budget threshold,
  not spec failure.

## Reproduction

```bash
git push origin main
```

The pre-push hook ran `./scripts/run-quality.sh` and failed at
`check-runtime-budget`.

## Candidate Causes

- The `5000ms` budget was set before enough recent `specdown` samples existed.
- `specdown` has bimodal local runtime from process, filesystem, or cache
  variance.
- Recent repeated full quality runs made the median reflect the slower mode
  rather than a single latest spike.

## Hypothesis

The budget is too tight for current observed `specdown` variance. Raising the
median budget to `8000ms` preserves a drift signal while avoiding a false block
near the old 5s threshold.

## Verification

Run `./scripts/run-quality.sh`; push should pass only if all quality gates,
including `check-runtime-budget`, pass.

## Root Cause

Budget calibration lagged behind newly accumulated `specdown` runtime samples.

## Prevention

When a recent-median runtime budget fails just above threshold, inspect the
sample distribution before retrying or loosening. Adjust the adapter budget only
when repeated samples show the threshold is below normal variance.
