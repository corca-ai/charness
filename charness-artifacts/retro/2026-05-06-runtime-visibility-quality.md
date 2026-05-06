# Session Retro: Runtime Visibility Quality

## Context
This session closed GitHub issue #102 by making empty quality runtime budget and startup probe surfaces visible as weak runtime visibility findings.

## Evidence Summary
Evidence used: issue #102, targeted runtime-budget tests, `../ceal` exported-plugin dogfood, bounded premortem subagents, slice closeout, and full `./scripts/run-quality.sh --read-only`.

## Waste
The first implementation only checked whether `runtime_budget_profiles` existed, so a selected profile with an empty `budgets` map could still hide the same failure mode. The first patch also exceeded the public skill helper length limit until the visibility logic moved into its own helper.

## Critical Decisions
Runtime visibility now keys off effective selected budgets rather than the mere presence of profile configuration. Empty `runtime_budgets:`, empty selected profile budgets, and empty `startup_probes: []` all remain visible but advisory.

## Expert Counterfactuals
Gary Klein would have turned the Ceal incident into an exact regression fixture before trusting the general omitted-field test. Daniel Kahneman would have challenged the "profile exists" shortcut because it made an empty profile feel configured.

## Next Improvements
- workflow: when an issue describes a concrete adapter shape, add one exact fixture for that shape before broadening the implementation.
- capability: keep small quality review lenses in helper modules before they push public skill scripts over length limits.
- memory: exported-plugin dogfood against the affected consumer repo should be cited in closeout when the issue came from that repo.

## Persisted
yes `charness-artifacts/retro/2026-05-06-runtime-visibility-quality.md`
