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
