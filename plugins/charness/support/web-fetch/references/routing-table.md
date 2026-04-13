# Initial Routing Table

This is the initial route surface extracted from the `insane-search` review and
reduced to tactics `charness` is willing to carry locally.

## Domain Families

- `x.com`, `twitter.com`
  - prefer search for discovery plus Syndication API or oEmbed for retrieval
- `reddit.com`
  - prefer `.json` endpoints with a mobile user agent
- `news.ycombinator.com`
  - prefer the Firebase API
- `stackoverflow.com`, `stackexchange.com`
  - prefer Stack Exchange API over raw HTML
- `github.com`
  - prefer runtime grant or authenticated `gh`; public REST fallback remains possible
- `youtube.com`, `youtu.be`, `vimeo.com`, `twitch.tv`, `tiktok.com`, `soundcloud.com`
  - prefer `yt-dlp` metadata or subtitle paths
- `blog.naver.com`
  - prefer mobile URL transform plus mobile user agent
- `news.naver.com`, `n.news.naver.com`, `finance.naver.com`
  - prefer reader-style fallback rather than raw fetch
- generic public URLs
  - prefer direct fetch first, then reader, metadata-only, archive

## Scope Rule

This table is intentionally incomplete.

Add a route only when:

- the domain appears repeatedly enough to justify a checked-in tactic
- the tactic is stable enough to explain honestly
- `charness` is willing to maintain the route or name the real external owner
