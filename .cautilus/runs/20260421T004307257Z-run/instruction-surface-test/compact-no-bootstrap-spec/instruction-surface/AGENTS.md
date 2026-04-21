# demo

## Operating Stance

- USE THE ACTUAL AVAILABLE SKILLS FOR THIS TURN.
- KEEP THE HARNESS PORTABLE.
- SPEAK TO THIS USER IN KOREAN UNLESS THEY ASK OTHERWISE.

## Skill Routing

Prefer installed charness public skills before improvising a repo-local workflow.

Keep this block intentionally non-exhaustive so `AGENTS.md` stays stable as the installed charness skill catalog changes.

When the right skill is unclear, or you need the current installed/trusted capability list, route to the shared/public charness skill `find-skills` first.

Use these high-signal routes first:

- unclear skill choice, named support/helper, or hidden capability lookup -> shared/public charness skill `find-skills`
- external source fetch (Slack thread, Notion page, Google Docs, GitHub content, arbitrary URL) -> `gather`
- bug, error, regression, or unexpected behavior investigation -> `debug`
- code, config, test, or operator-facing artifact implementation -> `impl`
- repo quality posture, gates, test confidence, security, or operability review -> `quality`
- next-session pickup, baton pass, or handoff artifact refresh -> `handoff`
- new or partially initialized repo operating surface -> `init-repo`
