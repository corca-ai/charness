# Gate Classification

Classify each observed gate or missing gate honestly.

## `healthy`

- currently present
- runnable
- high-signal for the seam it covers

## `weak`

- present but easy to game
- too shallow for the claimed confidence
- duplicated by a better existing gate

## `missing`

- should exist for the current risk surface
- absent or only implied

## `defer`

- would be useful later
- not the next highest-leverage gate for the current repo state
