---
name: web-fetch
description: "Internal support capability for routing public-web fetch requests through the strongest honest access path and classifying blocked or partial fetch responses without turning those tactics into a public workflow concept."
---

# Web Fetch

This is a support capability, not a public workflow concept.

Users should still reach this through a public skill such as `gather` when a
public URL needs stronger retrieval tactics than a plain direct fetch.

## Runtime Contract

- prefer a host-provided web grant or direct public fetch first
- use domain-specific public APIs or URL transforms when direct fetch is
  blocked or known to be weaker
- keep public-web routing and response classification here so public skills do
  not duplicate blocked-site heuristics
- preserve retrieval method and confidence in any durable artifact that uses
  this support capability

Use the helpers:

```bash
python3 "$SKILL_DIR/scripts/route_public_fetch.py" --url "https://www.reddit.com/r/python/"
python3 "$SKILL_DIR/scripts/classify_fetch_response.py" --path /tmp/fetch-response.html
```

## Guardrails

- Do not present a routing recommendation as proof that the site is currently
  reachable.
- Do not hide external binary dependencies such as `gh` or `yt-dlp`; record
  them in the selected route.
- Do not turn `gather` into a giant site-by-site cookbook when this support
  seam can carry the fetch tactics.

## References

- `references/runtime-contract.md`
- `references/routing-table.md`
- `references/provenance.md`
- `<repo-root>/scripts/route_public_fetch.py`
- `<repo-root>/scripts/classify_fetch_response.py`
