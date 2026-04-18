# Browser-Mediated Private Sources

Use this reference when the user starts from a private SaaS URL or a stable UI
path and expects honest acquisition rather than owner-only escalation.

## Decision Ladder

1. Check whether the same source already exists in a local durable artifact.
2. Prefer a host grant, authenticated binary, or official API/export path.
3. Use browser-mediated fallback through `agent-browser` only when the stronger
   official path is absent, insufficient, or still gated behind the same
   authenticated browser session.
4. Stop cleanly when the browser auth/bootstrap path is still missing.
5. Degrade only when partial value remains honest and explicitly marked.

## First-Class Auth / Bootstrap Modes

Accept these as legitimate gather-compatible bootstrap stories when they come
 from approved local operator state:

- imported auth state
- persistent profile path
- session-name persistence
- auth vault login
- origin-scoped headers
- human-only manual bootstrap

Do not ask the user to paste raw credentials into chat or checked-in docs.

## Remote / Headless Rule

Explain the host story honestly:

- local desktop profile reuse may be fine for one operator machine
- remote or CI-like Linux runners often need a different bootstrap path
- some flows can continue headless after state exists
- others still require one-time manual or headed bootstrap before headless use
- if no approved bootstrap path exists, stop and name the missing step

## Artifact Notes

When browser mediation happens, the durable gather artifact should say:

- what source identity was targeted
- which stronger paths were attempted first
- which browser auth/bootstrap mode was used
- what was captured successfully
- what still needs human confirmation

## Example: Private HR Roster

For a private HR SaaS roster:

1. check whether a local roster artifact already exists
2. ask whether the roster lives behind an official export, CSV, or API path
3. prefer that official path when it is available
4. if the operator only has a stable authenticated URL and no usable export,
   use `agent-browser` as a read-only acquisition fallback
5. if the browser session still needs manual login or headed bootstrap, stop
   with that explicit next step instead of claiming the roster was acquired
