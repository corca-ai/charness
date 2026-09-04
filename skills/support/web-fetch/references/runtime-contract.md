# Web Fetch Runtime Contract

`web-fetch` owns public-web retrieval tactics below the public-skill surface.

## Goal

Keep blocked-site fetch knowledge in one support seam so public skills can say:

- what source they need
- what durable artifact they produce
- what provenance and freshness they preserve

without growing a site-by-site operational cookbook.

## Acquisition Invariant

Acquire as much as the request and access boundary safely allow, but never hide
how that result was reached.

Every planned route or fallback stage that could affect the final answer should
be either attempted or represented in the acquisition trace as skipped,
not-implemented, terminal, or otherwise unavailable. The selected proof,
blocker, confidence, and final status should be derived from the selected
attempt rather than from a separate narrative summary.

Route ladder stages, response classes, headless bounds, and durable artifact
fields are owned by the helpers under `scripts/` (`route_stage_catalog.py`,
`classify_fetch_response.py`, `acquire_public_url.py`), not restated here.
