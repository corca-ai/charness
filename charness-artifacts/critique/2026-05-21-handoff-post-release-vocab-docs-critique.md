# Handoff Post-Release Vocabulary And Docs Ergonomics Critique

## Change

Update the active handoff so the next operator pushes/releases the current local
commits before enabling usage episodes, then decides the usage-episode
vocabulary in the first post-release pickup. Tighten the docs ergonomics
follow-up so it separates generated CLI reference noise from first-touch README
prose before adding any gate.

## Fresh-Eye Satisfaction

Blocked.

host signal: active developer-level tool contract for this session prohibits
`spawn_agent` use without a direct delegation request in the live user turn.
This pass therefore records the host restriction instead of substituting a
same-agent fresh-eye review.

## Concerns

- Wrong next action: the next session might enable the adapter before the
  release lands. Mitigation: the handoff now makes push/release step 1 and
  vocabulary step 2.
- Workflow trigger ambiguity: "docs ergonomics" could be read as a generated
  [docs/generated/cli-reference.md](../../docs/generated/cli-reference.md) rewrite. Mitigation:
  the handoff and quality latest name
  [docs/generated/cli-reference.md](../../docs/generated/cli-reference.md) as generated reference
  noise and point first to [README.md](../../README.md) route/procedure trim.
- Scope creep: usage-episode vocabulary could accidentally imply immediate
  runtime capture. Mitigation: the handoff requires either a runtime emitter or
  an explicit follow-up contract before flipping `enabled: true`.

## Counterweight

The change is intentionally advisory. It does not modify release mechanics,
adapter state, or generated docs. The only required action before ship is to
verify the handoff stays within its size/shape gate and links remain valid.
