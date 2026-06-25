# Critique Review
Date: 2026-06-25

## Decision Under Review

Resolve issue #392 by keeping X/Twitter exact-source acquisition honest when the
post body cannot be fetched: preserve source identity, write a durable terminal
record for the reported status URL, and expose who owns the next unblock through
`source_resolution.terminal_state`.

## Failure Angles

- Jackson/problem framing: the slice could falsely claim that Charness can fetch
  the exact X post text when the implemented boundary is typed terminal
  acquisition, not content capture.
- Weinberg/diagnostic: `source_identity: exact-unavailable` alone could leave
  the operator unable to tell whether the next step belongs to Charness gather,
  browser/profile access, an external provider, or caller input.
- Gawande/Minto operations: the new taxonomy could land in code but not in
  durable records, docs, plugin mirrors, and regression fixtures.

## Counterweight Pass

- Act-before-ship issue 1 was addressed: `authenticated-browser-required` is now
  documented as the terminal bucket for default non-live exact-source endpoints,
  meaning an operator-approved live X route, authenticated browser/profile, or
  exact-source provider is required before retrying.
- Act-before-ship issue 2 was addressed: success-path coverage now asserts
  `source_resolution.terminal_state == exact-post-acquired` through both
  `acquire_public_url.py` and a `gather_public_url.py --execute` record test.
- Requiring live X post text was over-worry for this issue. The issue's accepted
  fallback was a durable typed unsupported/blocked result with route trace, and
  live X fetching remains operator-authorized instead of autonomous.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/twitter_exact_source.py | action: fix | note: `authenticated-browser-required` needed an explicit umbrella definition for non-live exact endpoint policy and operator-approved live/auth/provider routes
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_twitter_exact_source.py | action: fix | note: `exact-post-acquired` needed CLI and gather-record coverage, not only pure classifier coverage
- F3 | bin: bundle-anyway | evidence: moderate | ref: docs/public-skill-dogfood.json | action: fix | note: `reviewed_on` was refreshed to 2026-06-25 so dogfood metadata matches the #392 evidence entry
- F4 | bin: valid-but-defer | evidence: strong | ref: docs/gather-provider-ownership.md | action: defer | note: a working live X/provider acquisition route remains outside this slice because it needs an operator-approved live route, authenticated browser/profile, or external exact-source provider

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye closeout review
- Requested spawn fields: inherited parent model and reasoning effort
- Host exposure state: requested_fields_sent
- Application state: two fresh-eye reviewers completed; one found no blockers,
  one found two blockers that were fixed before validation

## Fresh-Eye Satisfaction

parent-delegated: two bounded reviewers completed through the host
`multi_agent_v1.spawn_agent` surface. The closeability reviewer found the slice
honest to close and did not require live X fetching. The implementation reviewer
identified the `authenticated-browser-required` definition gap and missing
success-path CLI/record coverage; both were fixed and the focused gather/web-fetch
test bundle passed afterward.
