# Standing Pytest Dedup Retro

- Date: 2026-04-22
- Trigger: user correctly pointed out that the duplicated install/update test should be deleted or merged before being moved behind a slower gate.

## What I Missed

I treated a known duplicate as a routing problem (`standing` vs `ci_only`) before treating it as a proof-shape problem.

## Correction

- delete the duplicated managed-checkout binary refresh test
- keep the stronger remaining refresh test as the single standing proof
- only then move high-cost non-duplicate integration tests behind `ci_only`

## Next Time

When a slow-test triage already identifies `delete/merge` candidates, apply that change before introducing marker-based routing.
