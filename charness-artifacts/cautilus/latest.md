# Cautilus Dogfood
Date: 2026-04-19

## Trigger

- slice: migrate the checked-in chatbot proposal and benchmark consumer
  surfaces to the upstream full-truth packet contract by removing the local
  `limit` workaround and naming `attentionView` as the bounded human-facing
  shortlist
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
  shifted from a default-cap complaint to a full-`proposals` versus
  `attentionView` contract reminder

## Follow-ups

- re-run the checked-in chatbot proposal and benchmark summaries with the first
  public release that includes the `#15` packet shape so the repo stops
  depending on a pre-release sibling checkout for this consumer proof
- keep watching for downstream surfaces that still slice `proposals` directly
  when they really want the bounded human shortlist from `attentionView`
