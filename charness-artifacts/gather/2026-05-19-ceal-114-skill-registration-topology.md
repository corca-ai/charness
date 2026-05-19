# Gather: Ceal #114 Skill Registration Topology

Source: https://github.com/corca-ai/ceal/issues/114
Related Charness issue: https://github.com/corca-ai/charness/issues/178
Access mode: GitHub `gh` authenticated direct-cli
Freshness: fetched 2026-05-19; issue open, one CodeRabbit auto-plan comment present.

## Requested Scope

Capture the downstream Ceal source issue behind Charness #178 while preserving the boundary between Ceal-specific channel adapter behavior and Charness portable skill-authoring guidance.

## Source Facts

Ceal #114 reports that creating `idea-backlog` for two Slack channels was initially interpreted as two channel-local skill copies. The requester expected one canonical skill implementation with additional channel registrations referencing it, for example via symlink.

The Ceal-specific failure involved a workspace layout under `control/skills/channels/<channel-id>/...`, which made it easy to treat one channel registration as one skill directory. The issue distinguishes three concepts that were collapsed in the initial flow:

- canonical implementation location
- channel registration or trigger surface
- aliases or symlinks from other channels

Ceal's desired behavior is that skill creation or update requests mentioning multiple registered channels default to one canonical skill implementation plus multiple channel registrations, and only create separate per-channel copies when channel-specific behavior or data isolation is explicitly requested. Completion replies should state whether the implementation is shared or intentionally forked, and avoid wording that implies two independent skills when the same skill is registered in two channels.

## Portability Boundary For Charness

Ceal-specific terms such as Slack channels, channel ids, `control/skills/channels/<channel-id>/...`, and channel registration verification belong in Ceal's adapter/runtime/spec layer, not in Charness portable `create-skill` guidance.

The Charness-level lesson is more abstract: when one skill is requested across multiple registration targets, trigger surfaces, packages, hosts, or placements, decide implementation topology before writing files. The portable default should preserve one canonical implementation with multiple registrations or aliases pointing at it. Separate copies are intentional forks and require explicit behavior, data ownership, or isolation reasons.

## Open Gaps

The triggering Slack thread was not fetched. Ceal #114 says to re-read the Slack source before resolving Ceal itself; Charness #178 can likely proceed from the GitHub source issues because the portable rule does not depend on Slack-specific content.
