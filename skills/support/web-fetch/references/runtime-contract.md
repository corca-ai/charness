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
4. generic reader or metadata-only fallback
5. archive/cache fallback
6. clean stop with the failure mode recorded

## Response Classes

The helper classifier should keep at least these distinctions visible:

- `success`
- `partial-content`
- `login-wall`
- `captcha`
- `empty-spa`
- `error-page`
- `unclear`

## Durable Artifact Expectation

When a public skill uses this seam, the artifact should preserve:

- source URL
- selected route id
- retrieval method actually used
- response classification
- any remaining access or confidence gaps
