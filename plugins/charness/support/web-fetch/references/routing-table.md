# Initial Routing Table

This is the initial route surface extracted from the `insane-search` review and
reduced to tactics `charness` is willing to carry locally.

## Domain Families

- `x.com`, `twitter.com`
  - for a status URL, the `domain-specific-route` stage fetches the EXACT post
    through identity-keyed endpoints — the Syndication CDN keyed on the status
    id, then oEmbed — and accepts a result only when the returned status id
    matches the requested one (`identity_proof.matched`)
  - a mismatch is recorded as `invalid-proof` and never substituted; an
    all-blocked outcome stops honestly so a merely-similar public source is not
    passed off as the original
  - live fetching is injected, so the default is non-live: tests and host grants
    seed responses; an operator opts into live fetch explicitly
- `reddit.com`
  - prefer `.json` endpoints with a mobile user agent
- `news.ycombinator.com`
  - prefer the Firebase API
- `stackoverflow.com`, `stackexchange.com`
  - prefer Stack Exchange API over raw HTML
- `github.com`
  - route per `gather_provider.github.mode` in `.agents/gather-adapter.yaml`:
    `direct-cli` → `github-grant-or-cli` (authenticated `gh`);
    `host-mediated` → `github-host-mediated` (host's github capability
    command, never direct `gh`); `none` → `github-missing-capability`
    (stop with missing-capability or public REST only)
- `youtube.com`, `youtu.be`, `vimeo.com`, `twitch.tv`, `tiktok.com`, `soundcloud.com`
  - prefer `yt-dlp` metadata or subtitle paths
- `blog.naver.com`
  - prefer mobile URL transform plus mobile user agent
- `news.naver.com`, `n.news.naver.com`, `finance.naver.com`
  - prefer reader-style fallback rather than raw fetch
- generic public URLs
  - prefer direct fetch first, then `defuddle`, then read-only `agent-browser`
    render/network reconnaissance, then metadata-only or archive fallback

## Reader And Browser Fallbacks

- `defuddle`
  - use for article-like pages, blogs, news, and documentation when direct HTML
    is weak, cluttered, or only partially useful
  - skip for dashboards, app UIs, private SaaS, and structured APIs
- `agent-browser`
  - use after direct/reader extraction is insufficient for JS-rendered pages,
    empty SPA shells, repeated challenge signals, or list/collection tasks
    where runtime network requests may reveal public JSON/API endpoints
  - keep it read-only by default: render, inspect text/HTML, and record network
    candidates; do not click through auth or mutate source state

## Scope Rule

This table is intentionally incomplete.

Add a route only when:

- the domain appears repeatedly enough to justify a checked-in tactic
- the tactic is stable enough to explain honestly
- `charness` is willing to maintain the route or name the real external owner
