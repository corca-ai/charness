# Issue #510 Markdown Negotiation Resolution Critique
Date: 2026-08-06

## Decision Under Review

Add a generic content-negotiated Markdown acquisition stage for public URLs
whose direct HTML representation is a login wall or whose path is Markdown-
looking. The stage must preserve the representation/route trace and feed the
existing classifier and gather persistence boundary.

## Failure Angles

- Direct-attempt identity: a prior review found that domain-route attempts
  could hide the direct login-wall and suppress the required retry.
- Stage-plan parity: the declared acquisition plan and executable order could
  drift, making a green unit test describe a route the operator never gets.
- Boundary honesty: a failed Markdown retry must remain blocked/degraded, and
  seeded fixtures must not pretend to perform a second live read.

## Counterweight Pass

- The direct-attempt/order defect was a real blocker and was repaired before
  this round: the direct attempt is captured before any later attempt, the
  generic/domain path runs direct -> Markdown -> domain, and the plan matches.
- The remaining lack of dedicated Reddit-order and seeded-skip tests is a
  bounded coverage improvement, not evidence that the repaired path is wrong;
  source inspection plus the 34 focused tests cover the current acceptance bar.

## Structured Findings

- F1 | bin: valid-but-defer | evidence: strong | ref: skills/support/web-fetch/scripts/acquire_public_url.py:297-379; tests/test_web_fetch_route_and_classify.py:170-260 | action: defer | note: repaired direct-attempt identity and direct -> Markdown -> domain ordering are bound by domain-route failure and plan-order regressions; the round-2 reviewer found no blocker.
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_web_fetch_route_and_classify.py:170-260 | action: defer | note: add dedicated seeded-skip and Reddit execution-order tests if this route family expands; current skip behavior is observable in the implementation and the focused acceptance suite proves the generic consumer roundtrip.

## Reviewer Tier Evidence

- Requested tier: gpt-5.6-terra / medium reasoning.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_context=false, unnamed one-shot.
- Host exposure state: applied
- Application state: host-confirmed: spawn returned reviewer `019fd452-da1a-7091-9cd8-1564b868c22f` and delivered the repaired-surface verdict.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; round 1 found the direct-attempt/order blocker and round 2
read the repaired surface and returned clean. Both reviewer boundary windows
verified clean before parent writes.

## Reviewed Input Identity

## Boundary Ownership

- Producer: `acquire_public_url_io.py` selects the requested representation and
  `acquire_public_url.py` produces ordered acquisition attempts and disposition.
- Consumer: `gather_public_url.py` selects persistence only from the acquisition
  disposition and selected attempt.
- Owning surface: support/web-fetch acquisition plan and trace boundary.
- Verdict: owned-correctly
