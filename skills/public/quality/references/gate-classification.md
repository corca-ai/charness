# Gate Classification

Classify each observed gate or missing gate honestly.

This happens after enforcement triage:

- `AUTO_EXISTING`
- `AUTO_CANDIDATE`
- `NON_AUTOMATABLE`

## `healthy`

- currently present
- runnable
- high-signal for the seam it covers

## `weak`

- present but easy to game
- too shallow for the claimed confidence
- duplicated by a better existing gate
- still paying standing runtime after a cheaper and more direct proof exists

## `missing`

- should exist for the current risk surface
- absent or only implied

## `defer`

- would be useful later
- not the next highest-leverage gate for the current repo state

## Recommended Next Gates

Every recommended next gate should also carry an execution posture tag:

- `active`: install or change now as the next bounded proof move
- `passive`: monitor, wait, or defer with an explicit reason

The ordering of `Recommended Next Gates` is an **inference-layer** ranking, not a
verdict, so it falls under
[advisory-interpretation-contract.md](../../../shared/references/advisory-interpretation-contract.md).
It measures *your* judged leverage of each candidate gate against the current
risk surface; it proxies for "the single highest-value next proof move"; it is
blind to maintenance burden you have not yet weighed and to risks no inventory
surfaced. Before presenting the ranking, answer its interpretation question
first, in your own words against this repo: does the top-ranked gate genuinely
fit THIS repo's current state and burden tolerance, or is it a generic default
the ranking cannot contextualize? Verified gate *results* (a green/red gate, an
exact count) stay trusted — only the recommendation ordering is re-interpreted.
