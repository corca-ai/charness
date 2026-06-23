# Critique Review
Date: 2026-06-24

## Decision Under Review

Allow `gather_public_url.py --execute` to write durable trace-only records for
X/Twitter exact-source terminal verdicts (`exact-blocked`,
`exact-unavailable`) while preserving the generic rule that ordinary
blocked/degraded public URLs do not refresh `latest.md`.

Diff scope: `skills/public/gather/scripts/gather_public_url.py`,
`skills/public/gather/scripts/gather_plan.py`,
`skills/public/gather/references/capability-contract.md`,
`docs/public-skill-dogfood.json`, plugin mirrors, and
`tests/test_twitter_exact_source.py`.

## Failure Angles

- Problem framing: the intended problem is durable evidence for named status
  exact-source failures, not a broad license to persist every X/Twitter
  degraded route.
- Diagnostic: `source_identity: exact-unavailable` is too coarse by itself; it
  can mean "status endpoint route did not run live" or "this X URL was not a
  status URL at all."
- Operational: a false durable `latest.md` for a profile/timeline URL would
  make later agents treat a non-status clean stop as a gathered exact-source
  result.

## Counterweight Pass

- Act Before Ship: fresh-eye review found the initial predicate was too broad:
  a non-status X profile URL could emit `exact-unavailable` and write a
  terminal record. Fixed before closeout by requiring a
  `domain-specific-route` attempt with both `details.endpoint` and
  `details.requested_status_id`, and by adding a regression that
  `https://x.com/acme` does not write `latest.md`.
- Bundle Anyway: strengthened the blocked-record test so the direct captcha
  body, raw HTML marker, `selected_content`, and `content_text` are absent from
  the trace-only record.
- Over-Worry: no new support module or live X proof is needed for this slice;
  the behavior is deterministic over seeded/direct-response fixtures.
- Valid but Defer: the taxonomy still overloads `exact-unavailable`. A later
  slice can split non-status X URLs into a clearer non-applicable verdict, but
  the current predicate and regression close the shipping risk.

## Cautilus Scenario Registry Review

`plan_cautilus_proof.py --repo-root . --json` reported `next_action: none`.
The maintained `gather` scenario is still `gather-adapter-bootstrap`; this
slice changes helper-owned exact-source terminal-record behavior, not first
skill routing, adapter bootstrap, or evaluator prompt expectations. Dogfood
evidence was updated and deterministic tests own the new semantic behavior.

## Pre-Merge Action

- Fixed: narrow terminal-record writes to status-id keyed endpoint attempts.
- Fixed: prove non-status X URLs do not write durable terminal records.
- Fixed: prove trace-only terminal records do not persist substituted/raw
  content.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/gather/scripts/gather_public_url.py | action: fix | note: terminal write predicate required status-id endpoint evidence before closeout
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_twitter_exact_source.py | action: fix | note: no-substitution assertions now cover direct body, raw HTML, selected_content, and content_text
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/support/web-fetch/scripts/twitter_exact_source.py | action: defer | note: exact-unavailable taxonomy still covers no-live-fetch and non-status-url cases

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye code critique.
- Requested spawn fields: `fork_context=true`; no model override; scoped prompt named changed files, success criteria, and requested four-bin triage.
- Host exposure state: applied
- Application state: host-confirmed: `multi_agent_v1` completed result for agent `019ef6d7-76ec-7d11-a5c5-b631f3986abe`.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The bounded reviewer found one
Act-Before-Ship issue, which was fixed before closeout; remaining concerns were
classified as Bundle Anyway, Over-Worry, or Valid but Defer above.
