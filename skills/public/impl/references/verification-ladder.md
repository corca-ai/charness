# Verification Ladder

Use the lightest honest check that proves the behavior.

## Common Levels

- read-only reasoning against the code path
- local unit or integration test
- smoke script or CLI check
- end-to-end or browser path
- eval or scenario-based check

## Rules

- prefer an executable check over a claim when a local check is available
- if a branch matters to user-visible behavior, symbol existence is not enough
- when a check is missing, add the smallest one that prevents the branch from
  going unproven

## Closeout

At the end of the slice, state:

- what was verified directly
- what was inferred but not executed
- what remains unverified and why
