# Cautilus Dogfood
Date: 2026-04-19

## Trigger

- slice: expose the full long-context chatbot proposal set locally by setting
  explicit `limit: 12` in the checked-in packet and updating the benchmark
  honesty prompt to name the upstream default-cap seam directly
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the local slice changes the checked-in chatbot proposal packet and
  one adapter prompt, but it should not disturb the maintained instruction
  routing contract for `find-skills -> impl` or direct `spec` routing

## Prompt Surfaces

- `.agents/cautilus-adapters/chatbot-benchmark.yaml`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: checked-in routing still preserves `find-skills -> impl` on
  the workspace surface, direct compact implementation still routes to `impl`,
  and both checked `spec` routes still pass after the benchmark prompt wording
  shifted from a local top-five complaint to an upstream default-cap warning

## Follow-ups

- keep the local explicit `limit: 12` override until upstream `cautilus`
  documents the default cap more honestly in help/schema/docs
- track the upstream visibility fix in `corca-ai/cautilus` so this repo can
  later decide whether the checked-in packet still needs the override
