# Issue #510 Markdown Negotiation Debug
Date: 2026-08-06

## Problem

`gather_public_url.py` reports a public Markdown-capable page as blocked after
the HTML-oriented direct request receives a login wall.

## Correct Behavior

Given a public URL whose HTML representation is a login wall and whose public
Markdown representation is readable, when acquisition runs, it must try the
Markdown representation before terminal refusal, select it on success, and
preserve the selected representation and route in the trace. A failed retry
must remain blocked or degraded without credentials.

## Observed Facts

- Issue #510 reports `Accept: text/html,...` for the current direct path and a
  successful `Accept: text/markdown` response for the same public URLs.
- `acquire_public_url_io.py` sends only the HTML-oriented header.
- `classify_fetch_response.py` emits `login-wall`; the policy has no alternate
  representation stage, and gather refuses non-success acquisitions.
- A delegated causal review read the exact code path and did not claim a new
  live provider roundtrip.

## Reproduction

- Small local path: direct attempt -> `login-wall` -> no representation retry ->
  fallback policy/gather terminal blocked result. The provider body is
  issue-supplied evidence; local transport tests will provide the deterministic
  HTML/Markdown split.

## Candidate Causes

- The request header selects only HTML, so a public Markdown representation is
  never offered to the provider.
- The classifier's `login-wall` status is treated as terminal before a public
  representation-selection stage exists.
- The acquisition plan and trace omit the alternate stage, so gather cannot
  distinguish inaccessible content from an untried representation.
- A provider or local transport difference could make the issue behavior
  non-reproducible outside the captured evidence.

## Hypothesis

- If the same URL is retried with `Accept: text/markdown` after a direct
  `login-wall`, then a deterministic transport returning Markdown will produce
  a successful selected attempt and gather persistence | disconfirmer: run a
  two-response local transport fixture and a failed-retry fixture before
  relying on the implementation.

## Verification

- confirmed as the leading local hypothesis by source inspection and causal
  review: the representation is never requested and the policy has no stage;
  the transport fixture and end-to-end gather test are the required repair
  proof. Live provider behavior remains unverified.

## Root Cause

The generic public acquisition contract has no representation-selection
invariant. It sends one HTML-oriented request, maps a login wall to a blocked
attempt, and proceeds directly to fallbacks/terminal disposition. The missing
stage—not a claim that all login walls are negotiable—causes public Markdown
sources to be rejected without trying their declared representation.

## Invariant Proof

- Invariant: a blocked direct representation must not be treated as proof that
  the public source is inaccessible until the bounded Markdown representation
  is tried when eligible.
- Producer Proof: direct IO sends the HTML Accept header; classifier and policy
  show the login-wall status is currently terminal to this missing stage.
- Final-Consumer Proof: gather persists only success and otherwise returns
  blocked/degraded with no record; the repaired fixture must bind success to
  selected Markdown content.
- Interface-Shape Sibling Scan: direct IO, route stage catalog, policy, and
  gather consumer were inspected; same-class plain GET siblings are diagnostic
  only, while the generic route is the repair owner.
- Non-Claims: no live provider, browser, installed plugin, remote CI, or
  universal Markdown-negotiation behavior is proven here.

## Detection Gap

- Existing tests cover login-wall classification and no-write behavior, but no
  test supplies two representations for one URL. Add a transport fixture that
  asserts the Accept header, selected stage, persistence, and failed-retry
  trace.

## Sibling Search

- Mental model: representation selection is a stage before disposition, not a
  classifier exception.
- same layer: impersonated fetch also uses a plain GET | decision: diagnostic
  only; follow-up: `gather-routing-provider-discovery` | proof: static read.
- abstraction up: route catalog defines fallback stages | decision: add the
  generic stage there | proof: source and route fixture.
- cross-file: `gather_public_url.py` final consumer | decision: preserve its
  success/no-write boundary | proof: source read and integration test.

## Seam Risk

- Interrupt ID: gather-510-markdown-representation-selection
- Risk Class: external-seam
- Seam: public provider representation -> acquisition classifier -> gather record
- Disproving Observation: a local alternate Markdown response is selected and
  persisted, while a failed retry remains non-success.
- What Local Reasoning Cannot Prove: provider negotiation, live source bodies,
  installed-consumer parity, and remote CI.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-06-issue-510-markdown-negotiation-contract.md

## Prevention

Keep representation selection explicit in the acquisition plan and trace, and
retain paired success/failure transport fixtures at the gather boundary. Defer
provider-specific discovery under the named follow-up rather than silently
expanding the generic route.
