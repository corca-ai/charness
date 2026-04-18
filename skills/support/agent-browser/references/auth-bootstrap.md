# Auth Bootstrap Modes

Use this reference when `agent-browser` is acting as the runtime beneath
`gather` for a private SaaS source.

## First-Class Modes

These are legitimate bootstrap stories when they come from approved local
operator state rather than pasted secrets:

- imported auth state
- persistent profile path
- session-name persistence
- auth vault login
- origin-scoped headers
- one-time manual or headed bootstrap

## Remote / Headless Guidance

Do not blur these together:

- local desktop profile reuse
- remote Linux runner with saved state already present
- remote Linux runner that still needs a one-time manual bootstrap

Some flows can continue headless once state exists. Others cannot honestly
start until a human performs the first login or state import.

## Gather Expectation

When this support seam is used for acquisition:

- record which auth/bootstrap mode was used
- say which stronger official paths were tried first
- stop cleanly when bootstrap is still missing
- do not claim browser-mediated acquisition succeeded if the page only loaded
  to an unauthenticated or partially authenticated state
