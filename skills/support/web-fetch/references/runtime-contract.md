# Web Fetch Runtime Contract

`web-fetch` owns public-web retrieval tactics below the public-skill surface.

## Goal

Keep blocked-site fetch knowledge in one support seam so public skills can say:

- what source they need
- what durable artifact they produce
- what provenance and freshness they preserve

without growing a site-by-site operational cookbook.

## Route Ladder

Prefer this order:

1. direct public fetch or host web grant
2. domain-specific public API or URL transform
3. authenticated or installed binary when the route explicitly needs one
4. `defuddle` reader extraction for article-like public pages
5. `agent-browser` render/network reconnaissance when the page is JS-rendered,
   weak/partial after cleaner extraction, blocked by repeated challenge signals,
   or the user intent is list/collection and internal public APIs may exist
6. archive/cache fallback
7. clean stop with the failure mode recorded

## Acquisition Invariant

Acquire as much as the request and access boundary safely allow, but never hide
how that result was reached.

Every planned route or fallback stage that could affect the final answer should
be either attempted or represented in the acquisition trace as skipped,
not-implemented, terminal, or otherwise unavailable. The selected proof,
blocker, confidence, and final status should be derived from the selected
attempt rather than from a separate narrative summary.

Reader fallbacks such as `defuddle` are part of this ladder when installed and
appropriate for the page type. When they are missing, the trace should say so
instead of silently collapsing the route.

`agent-browser` reconnaissance is automatic only inside these read-only bounds:

- open the target URL
- wait briefly for render
- extract body text or HTML
- for list/collection intent, inspect network requests for public-looking
  `/api/`, `/graphql`, or `.json` candidates

Do not click through login, submit forms, solve challenges, or persist
discovered internal endpoints as reusable site knowledge unless a maintainer
accepts that source route explicitly.

## Response Classes

The helper classifier should keep at least these distinctions visible:

- `success`
- `partial-content`
- `login-wall`
- `captcha`
- `empty-spa`
- `error-page`
- `unclear`

Classifiers should also expose:

- `confidence`: `strong`, `weak`, or `none`
- `proof`: caller-provided text, regex, or JSON-field evidence that
  justified strong success
- `signals`: WAF/product, login, CAPTCHA, empty-shell, metadata, and size
  signals used to choose the next fallback stage
- `fallback_candidates`: next honest acquisition stages such as `defuddle`,
  `agent-browser-render`, `agent-browser-network-recon`, `archive`, or
  `clean-stop`

## Durable Artifact Expectation

When a public skill uses this seam, the artifact should preserve:

- source URL
- selected route id
- retrieval method actually used
- acquisition trace with stage id, tool id, status, confidence, and error
- response classification
- any remaining access or confidence gaps

The runtime may return selected successful content only when the caller asks for
it. That selected content is extracted text or markdown derived from the
winning attempt; it is not raw response persistence and should not be embedded
inside the acquisition trace JSON by default.
