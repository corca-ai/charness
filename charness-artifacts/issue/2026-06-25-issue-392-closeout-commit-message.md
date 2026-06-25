issue: clarify X/Twitter exact-source terminal ownership

Closes #392.

Jtbd: When a user asks gather to preserve a specific X/Twitter status URL and
the exact post cannot be fetched, the result tells the operator whether the
source was acquired, blocked by X, needs an authenticated/browser/provider route,
or is unsupported, without substituting adjacent search results or similar posts.

Boundary: This resolves the durable typed terminal-result path. It does not add
autonomous live X fetching, browser profile bootstrap, or a third-party
exact-source provider.

Resolution Brief: #338 completed exact-source identity preservation and terminal
record writing. #392 closes the remaining operator-decision gap by adding
`source_resolution.terminal_state` and route-owner evidence to code, docs, tests,
dogfood, plugin mirrors, and a live gather record for the reported status URL.

Implementation: `twitter_exact_source.py` now classifies terminal ownership as
`exact-post-acquired`, `exact-post-blocked-by-x`,
`authenticated-browser-required`, or `unsupported-route`; acquire/gather helpers
surface that object in JSON and markdown records; gather public docs and
web-fetch routing docs define the non-live/auth/provider boundary; plugin mirrors
were synced.

Prevention: `tests/test_twitter_exact_source.py` now covers all four terminal
states, the reported `x.com/jenzhuscott/status/2063032701087883647` status id,
CLI propagation, and gather record rendering for success, blocked, unavailable,
and unsupported routes.

Critique: charness-artifacts/critique/2026-06-25-issue-392-x-twitter-source-resolution.md

Behavior: verified with focused gather/web-fetch tests, skill/package/dogfood
validators, markdown/link/integration checks, Cautilus planner `next_action:
none`, and the durable record
`charness-artifacts/gather/2026-06-25-x-com-jenzhuscott-status-2063032701087883647-source-resolution.md`
showing `source_identity: exact-unavailable` and
`terminal_state: authenticated-browser-required`.

AI-provenance: Codex agent authored the implementation, tests, docs, artifacts,
and carrier.
