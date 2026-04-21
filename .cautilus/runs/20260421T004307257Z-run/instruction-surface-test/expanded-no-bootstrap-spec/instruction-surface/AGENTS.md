# demo

## Operating Stance

- USE THE ACTUAL AVAILABLE SKILLS FOR THIS TURN.
- KEEP THE HARNESS PORTABLE.
- SPEAK TO THIS USER IN KOREAN UNLESS THEY ASK OTHERWISE.

## Skill Routing

When one of these shows up in a request, prefer the named skill first:

- release-note style summary or chat-ready human update -> `announcement`
- new or upgraded repo-owned CLI, bootstrap script, or command runner -> `create-cli`
- new or updated charness skill, support skill, profile, preset, or integration -> `create-skill`
- bug, error, regression, or unexpected behavior investigation -> `debug`
- unclear skill choice, named support/helper, or hidden capability lookup -> `find-skills`
- external source fetch (Slack thread, Notion page, Google Docs, GitHub content, arbitrary URL) -> `gather`
- next-session pickup, baton pass, or handoff artifact refresh -> `handoff`
- bounded human review loop or deliberate human judgment checkpoint -> `hitl`
- early product, system, workflow, API, or agent concept shaping -> `ideation`
- code, config, test, or operator-facing artifact implementation -> `impl`
- new or partially initialized repo operating surface -> `init-repo`
- source-of-truth docs and current repo story alignment -> `narrative`
- before-the-fact failure review for a non-trivial decision -> `premortem`
- repo quality posture, gates, test confidence, security, or operability review -> `quality`
- cut, bump, or verify a release surface -> `release`
- retrospective after a meaningful work unit or missed issue -> `retro`
- turn a concept or design into a living implementation contract -> `spec`
