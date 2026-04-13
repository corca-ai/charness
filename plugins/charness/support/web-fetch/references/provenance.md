# Web Fetch Provenance

This support seam was informed by the public `insane-search` plugin and skill:

- upstream repo: `fivetaku/insane-search`
- inspected on 2026-04-13 UTC

What `charness` borrowed:

- the value of an explicit blocked-site routing table
- the fetch escalation ladder for public-web failures
- the distinction between real content, partial content, login walls, CAPTCHA,
  and empty SPA shells

What `charness` did not borrow as runtime ownership:

- the full upstream plugin surface
- a claim that upstream helper commands are installed automatically
- a claim that `charness` now owns every platform-specific fetch implementation

`charness` uses this repo as a design reference, not as a runtime owner.
