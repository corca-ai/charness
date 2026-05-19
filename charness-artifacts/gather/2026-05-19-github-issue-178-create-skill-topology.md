# Gather: GitHub Issue #178 Create-Skill Multi-Channel Topology

Source: https://github.com/corca-ai/charness/issues/178
Access mode: GitHub `gh` authenticated direct-cli
Freshness: fetched 2026-05-19T11:01:06Z issue creation state; no comments were present at fetch time.

## Requested Scope

Capture the primary issue context for discussing and possibly implementing Charness #178 in an isolated worktree.

## Source Facts

Issue #178 reports a `create-skill` convention gap surfaced by Ceal issue corca-ai/ceal#114. When a user asks for one skill to be registered in multiple channels, agents can interpret that as one channel-local implementation directory per channel.

The desired default is one canonical skill implementation plus multiple channel registration surfaces, such as symlink or alias registrations. Separate channel-local copies should be treated as explicit forks only when channel-specific behavior or data isolation is requested.

The issue says this belongs in Charness because `create-skill` is the source of truth for portable skill authoring conventions. Ceal may add a runtime guide overlay and topology verifier, but its skill-authoring spec already points back to `create-skill` for this convention.

## Desired Behavior

When `create-skill` handles multi-channel registration requests:

1. Decide topology before writing files.
2. Default to one canonical implementation plus channel registrations pointing to it.
3. Fork or copy per channel only when the user explicitly asks for channel-specific behavior or data isolation.
4. Before completion, verify and report topology in user-facing terms: shared implementation versus intentional fork.

## Non-Goals

- Do not require workspace-scope canonical placement; a channel implementation plus another channel symlink can still be a single canonical implementation.
- Do not forbid explicit forks.

## Source Links

- Charness issue: https://github.com/corca-ai/charness/issues/178
- Ceal source issue: https://github.com/corca-ai/ceal/issues/114

## Open Gaps

Ceal #114 was not fetched in this record. Fetch it if implementation needs the exact downstream failure transcript rather than the Charness issue's summarized source.
