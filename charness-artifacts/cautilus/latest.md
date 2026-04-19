# Cautilus Dogfood
Date: 2026-04-19

## Trigger

- slice: fix `find-skills` startup artifact drift by keeping installed-plugin
  invocation aligned with repo-owned source inventory, and add an explicit
  session rule for classifying `find-skills/latest.*` rewrites before treating
  them as commit candidates
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: this slice tightens startup discovery and session discipline, but it
  should not disturb the maintained instruction routing contract for
  `find-skills -> impl` or direct `spec` routing

## Prompt Surfaces

- `AGENTS.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/run-evals.py --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in surface still preserves `find-skills -> impl`
  on the workspace path, compact direct implementation still routes to `impl`,
  and checked direct contract-shaping still routes to `spec`

## Follow-ups

- keep treating `charness-artifacts/find-skills/latest.*` as canonical
  capability inventory only when the inventory itself changed; startup
  invocation churn should now be handled as a bug
- if `find-skills` later needs to mix installed public skills with
  repo-specific integrations for non-source consumer repos, add that as a
  separate contract change instead of regressing the source-repo path again
