# HITL Review: AGENTS.md Craken Refactor

Date: 2026-04-25

## Review Goal

Carry the handoff's first implementation slice forward: inventory `docs/`,
decide each document's fate conservatively, and rewrite `AGENTS.md` as a
craken-style map-first entry without changing Charness policy semantics.

## Target

- [AGENTS.md](../../AGENTS.md)
- [docs/conventions/operating-contract.md](../../docs/conventions/operating-contract.md)
- [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
- [CLAUDE.md](../../CLAUDE.md)

## Accepted Rules

- The user asked to implement [docs/handoff.md](../../docs/handoff.md); that is
  treated as approval to apply the handoff's AGENTS refactor slice.
- No `docs/` file satisfies the spec's stale deletion criterion because all
  markdown docs had a meaningful git change in April 2026. Deletion requires
  explicit user agreement, so every existing doc stays.
- The docs net-file-count limit is preserved by using two convention files
  instead of one file per old AGENTS subsection.
- Host-entry normalization follows `init-repo`: with `AGENTS.md` present and
  `CLAUDE.md` missing, create `CLAUDE.md -> AGENTS.md`.
- Because `CLAUDE.md` is now an intentional host-entry alias, add it to the
  repo markdown and prompt-behavior surfaces in [.agents/surfaces.json](../../.agents/surfaces.json).
- Refresh the compact synthetic Cautilus instruction-surface cases so final
  proof exercises the new Start Here / Subagent Delegation / Phase Rules shape.

## Docs Inventory Decisions

- Current pickup: keep [docs/handoff.md](../../docs/handoff.md).
- Operator surfaces: keep [docs/operator-acceptance.md](../../docs/operator-acceptance.md), [docs/development.md](../../docs/development.md), [docs/cli-reference.md](../../docs/cli-reference.md), and [docs/host-packaging.md](../../docs/host-packaging.md).
- Architecture and control plane: keep [docs/harness-composition.md](../../docs/harness-composition.md), [docs/control-plane.md](../../docs/control-plane.md), [docs/external-integrations.md](../../docs/external-integrations.md), [docs/support-skill-policy.md](../../docs/support-skill-policy.md), [docs/runtime-capability-contract.md](../../docs/runtime-capability-contract.md), [docs/capability-resolution.md](../../docs/capability-resolution.md), and [docs/agent-task-envelope.md](../../docs/agent-task-envelope.md).
- Skill and validation policy: keep [docs/public-skill-validation.md](../../docs/public-skill-validation.md), [docs/public-skill-dogfood.md](../../docs/public-skill-dogfood.md), [docs/narrative-announcement-boundary.md](../../docs/narrative-announcement-boundary.md), and [docs/gather-provider-ownership.md](../../docs/gather-provider-ownership.md).
- Memory and deferred work: keep [docs/artifact-policy.md](../../docs/artifact-policy.md), [docs/deferred-decisions.md](../../docs/deferred-decisions.md), [docs/retro-self-improvement-spec.md](../../docs/retro-self-improvement-spec.md), and [docs/support-tool-followup.md](../../docs/support-tool-followup.md).

## Next State

After the AGENTS/docs implementation settles, run the final Cautilus proof
against the refreshed scenarios, run quality gates, update handoff with the new
first move, then commit and push the accumulated branch.
