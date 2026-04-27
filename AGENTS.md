# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://github.com/corca-ai).

## Start Here

- Always call `charness:find-skills` once at the start of each task-oriented session; use [charness-artifacts/find-skills/latest.md](./charness-artifacts/find-skills/latest.md) as the local capability map.
- Load matching skills before improvising, and continue active repo work from [docs/handoff.md](./docs/handoff.md).
- Read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md) before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts.
- Keep the harness portable: host-specific behavior belongs in adapters, presets, and integration manifests.
- Prefer validators and scripts over prose rituals; leave structured state when a tool cannot finish end-to-end.
- Route evaluator-backed validation through `quality` before `hitl` or same-agent manual review.

## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract; this is the explicit user delegation request for named bounded reviewer scopes.
- Do not wait for a second user message. Task-completing `init-repo` and `quality` review runs may spawn bounded reviewers.
- If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.

## Phase Rules

- Treat `mutate -> sync -> verify -> publish` as hard phase barriers; sync generated, plugin, and export surfaces before validators.
- Treat meaningful `charness-artifacts/` changes as repo state and commit them with the work they support.
- Current-pointer helpers should no-op without canonical content change; unexpected rewrites are invocation drift or helper bugs.
- Treat premortem, closeout, and commit as part of task-completing repo work, not optional follow-up.

## Work Phase Map

- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md); it owns sync-before-verify order, generated surfaces, closeout, and mutation parallelism.
- Before reviewing slow gates, local-vs-CI validation cost, evaluator-backed validation, or quality-contract changes, route through `quality`; it owns validation posture and repo-local quality gate design.
- Before closing task-completing repo work, read [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md); it owns commit discipline, durable artifact inclusion, mandatory premortem closeout, and session repair.
- Before changing repo operating contracts, prompt or skill surfaces, exports, or artifact policy, read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md); it owns recent repeat traps that should change the next move.
- Before claiming a GitHub issue or operator-facing request is closable, map the requested outcome to executed proof and run the required premortem; if the canonical bounded-review path is blocked, stop and report the host restriction.

## Policy Index

- [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md): guiding principles, commit discipline, skill metadata, dogfood, and session rules.
- [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md): validation, change discipline, support/update dry-runs, generated surfaces, and tool state.

## Contract Map

- Current pickup: [docs/handoff.md](./docs/handoff.md), [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md), [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md).
- Operator surfaces: [docs/operator-acceptance.md](./docs/operator-acceptance.md), [docs/development.md](./docs/development.md), [docs/cli-reference.md](./docs/cli-reference.md), [docs/host-packaging.md](./docs/host-packaging.md).
- Architecture and control plane: [docs/harness-composition.md](./docs/harness-composition.md), [docs/control-plane.md](./docs/control-plane.md), [docs/external-integrations.md](./docs/external-integrations.md), [docs/support-skill-policy.md](./docs/support-skill-policy.md), [docs/runtime-capability-contract.md](./docs/runtime-capability-contract.md), [docs/capability-resolution.md](./docs/capability-resolution.md), [docs/agent-task-envelope.md](./docs/agent-task-envelope.md).
- Skill and validation policy: [docs/public-skill-validation.md](./docs/public-skill-validation.md), [docs/public-skill-dogfood.md](./docs/public-skill-dogfood.md), [docs/narrative-announcement-boundary.md](./docs/narrative-announcement-boundary.md), [docs/gather-provider-ownership.md](./docs/gather-provider-ownership.md).
- Memory and deferred work: [docs/artifact-policy.md](./docs/artifact-policy.md), [docs/deferred-decisions.md](./docs/deferred-decisions.md), [docs/retro-self-improvement-spec.md](./docs/retro-self-improvement-spec.md), [docs/support-tool-followup.md](./docs/support-tool-followup.md).
