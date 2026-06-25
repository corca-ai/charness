# Critique Review
Date: 2026-06-25

## Decision Under Review

Resolve issue #403 by making `issue new` closeout report the created issue title
and a short filed-body summary, not only the GitHub link.

## Failure Angles

- Jackson/problem framing: the slice could stop at helper JSON and leave the
  reporter's real JTBD unproven: requester-visible closeout content.
- Weinberg/diagnostic: the helper/schema/reference surfaces could drift if
  `body_preview` were added to code but not to the backend contract.
- Gawande/Minto operations: future agents could still render vague prose unless
  the closeout discipline gives a concrete shape and a deterministic contract
  check.

## Counterweight Pass

- Act-before-ship findings were addressed before this artifact: the closeout
  reference now includes a single-issue template requiring title, `body_preview`
  summary, and a body-verification warning; `test_issue_closeout_discipline.py`
  pins that contract.
- The backend-reference drift was bundled: `issue-backend.md` now documents
  `body_preview` as submitted-body context, not a substitute for
  `body_verified`.
- Requiring proof of a live agent-authored closeout was over-worry for this
  slice. The shipped boundary is helper payload plus contract/test shape; live
  dogfood can happen on the next actual `issue new` filing.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/references/closeout-discipline.md | action: fix | note: #403 needed a closeout shape that makes link-only issue-create reporting incomplete; fixed with template plus deterministic contract test
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/references/issue-backend.md | action: fix | note: document `body_preview` next to `body_verified` so helper behavior and backend reference stay aligned
- F3 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_issue_create.py | action: document | note: live prose-render proof is outside this slice; deterministic helper and contract tests are the honest proof level
- F4 | bin: valid-but-defer | evidence: moderate | ref: docs/public-skill-dogfood.json | action: defer | note: next real issue-create dogfood should observe whether an agent uses the title/body-summary closeout shape

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: three bounded angle reviewers and one separate counterweight
reviewer completed through the host `multi_agent_v1.spawn_agent` surface. The
counterweight found no remaining act-before-ship issues after the closeout
template, backend-reference documentation, dogfood evidence, and focused tests
were updated.
