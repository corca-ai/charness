# Asset Refresh

`gather` should refresh an existing asset in place when the source identity is
the same.

## Same Source Signals

- same URL
- same repo path
- same document identity or upstream page

## Rule

Prefer one durable asset per source identity.

If freshness matters, add a concise update note or history entry instead of
creating a sibling file with almost the same contents.
