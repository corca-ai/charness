# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://github.com/corca-ai).

## Start Here

- [docs/design-north-star.md](./docs/design-north-star.md) is the governing design standard: the harness briefs a capable judge and keeps teeth only where a wrong answer escapes. Default to judgment on reversible work; at irreversible boundaries (issue/PR close, release publish, external writes, deletions) success is provisional — confirm with a different observer and a different evidence channel, never a terminal green. When a gate, doc, or contract conflicts with this, the north star wins and the conflicting surface is what gets fixed.
- Session-opening routing, capability inventory, the `gather` rule for external sources, and validation-before-`hitl` routing are all owned by `## Skill Routing` below.
- Load matching skills before improvising, and continue active repo work from [docs/handoff.md](./docs/handoff.md).
- Cautilus is eval-only and ask-before-run: before any `cautilus evaluate ...`, consult `python3 scripts/plan_cautilus_proof.py --repo-root . --json` and use the repo wrapper `python3 scripts/run_cautilus_eval.py` instead of a bare `cautilus evaluate` call. Full eval-only/disabled-surface contract: [skills/public/quality/references/cautilus-on-demand.md](./skills/public/quality/references/cautilus-on-demand.md).
- Read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md) before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts.
- Keep the harness portable: host-specific behavior belongs in adapters, presets, and integration manifests.
- Prefer validators and scripts over prose rituals; leave structured state when a tool cannot finish end-to-end.

## Skill Routing

At session start, a pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment. When hidden support/integration availability is unclear, run the read-only `charness catalog list --repo-root <repo> --json` inventory. If the SessionStart hook is installed it may inject this context; it remains context-only, not a classifier.

External URLs or source links that should become working context for this repo route through `gather` before summarizing, implementing, or deciding from them.

Validation-shaped closeout or operator reading test requests go through `quality` validation recommendations before HITL or same-agent manual review.

Keep this block short. Detailed routing belongs in installed skill metadata and model judgment, not in a long checked-in catalog.

## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are **already delegated** by this repo contract; this is the repo owner's explicit user delegation request for the named bounded reviewer scopes.
- When the host permits spawning, do not wait for a second user message. Task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue` resolution/closeout review runs spawn bounded reviewers immediately when the contract calls for them.
- A higher-priority system, developer, or host instruction may prohibit a spawn; this repo request cannot override it. If the host blocks subagent spawning at runtime (Agent tool absent, API-level rejection), stop and report the concrete host signal explicitly.
- Do not substitute a same-agent pass. Fresh-eye review means a different agent context; if that context cannot be obtained, leave the review unproven.
- Bounded reviewers run in the **shared parent worktree**: inspect prior versions read-only (`git show <ref>:<path>`) and never run index- or worktree-mutating git ops (`git checkout`/`restore`/`reset`/`stash`, or `git add` of files touched only to inspect them). Staging a base reversion silently corrupts the closeout commit (#258); the canonical rule lives in [skills/shared/references/fresh-eye-subagent-review.md](./skills/shared/references/fresh-eye-subagent-review.md).
- Bounded reviewers run read-only: on hosts with typed subagents, spawn them as `bounded-reviewer` ([.claude/agents/bounded-reviewer.md](./.claude/agents/bounded-reviewer.md)), and parents prove worktree+index integrity around each review with [skills/shared/scripts/reviewer_boundary_fingerprint.py](./skills/shared/scripts/reviewer_boundary_fingerprint.py) snapshot/verify (#428); a failed verify quarantines that review's approvals.
- **Subagent default (user standing request):** request `gpt-5.6-terra` with `medium` reasoning effort for every Charness-spawned coding, review, and dynamic-workflow subagent when the host exposes those fields. In Codex MultiAgent V2, pair caller-provided model/reasoning overrides with `fork_turns: "none"` unless a bounded parent-history count is needed: the default `fork_turns: "all"` rejects those overrides. Omit `agent_type` or ensure its role does not override the requested model/effort. When the host exposes no per-subagent controls, or a higher-priority policy restricts them, proceed and state that limitation.

## Dynamic Workflows

- The repo owner has a standing request to use a dynamic workflow (the multi-agent Workflow tool / orchestration) when it genuinely earns its cost — fan-out coverage, independent-perspective confidence, adversarial verification, or scale one context cannot hold — when the host permits it. Do not wait for a second user message solely to repeat that request. Appropriateness is your judgment.
- A higher-priority system, developer, or host instruction may prohibit a workflow; this repo request cannot override it.

- Canonical fits: `handoff` chunked-routing over the live backlog, `achieve` goal design / slice decomposition, and review/quality adversarial fan-outs. Any task qualifies when the same cost/benefit holds; this is the orchestration sibling of the delegation standing request.
- Guardrail: scale to the task — scout inline first to find the work-list, then fan out; do not spin up dozens of agents for trivial or single-fact work. A wrong workflow result that ships is still a wrong answer that escaped, so keep the irreversible-boundary safeguards.
- If the host blocks orchestration at the runtime level (Workflow/Agent tool absent, API-level rejection), report the concrete signal explicitly; do not claim that orchestration ran.

## Phase Rules

- Treat `mutate -> sync -> verify -> publish` as hard phase barriers; sync generated, plugin, and export surfaces before validators.
- Treat meaningful `charness-artifacts/` changes as repo state and commit them with the work they support.
- Current-pointer helpers should no-op without canonical content change; unexpected rewrites are invocation drift or helper bugs.
- Treat critique, closeout, and commit as part of task-completing repo work, not optional follow-up.
- After verification passes for task-completing repo work, commit before answering follow-up usage/status questions or checking installed-machine state.

## Work Phase Map

- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md); it owns sync-before-verify order, generated surfaces, closeout, and mutation parallelism.
- Before reviewing slow gates, local-vs-CI validation cost, evaluator-backed validation, or quality-contract changes, route through `quality`; it owns validation posture and repo-local quality gate design.
- Before closing task-completing repo work, read [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md); it owns commit discipline, durable artifact inclusion, mandatory critique closeout, and session repair.
- Before changing repo operating contracts, prompt or skill surfaces, exports, or artifact policy, read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md); it owns recent repeat traps that should change the next move.
- Before claiming a GitHub issue or operator-facing request is closable, map the requested outcome to executed proof and run the required critique; if the canonical bounded-review path is blocked, stop and report the host restriction.

## Policy Index

- [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md): guiding principles, commit discipline, skill metadata, dogfood, and session rules.
- [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md): validation, change discipline, support/update dry-runs, generated surfaces, and tool state.

## Contract Map

- Current pickup: [docs/handoff.md](./docs/handoff.md), [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md), [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md).
- Operator surfaces: [docs/operator-acceptance.md](./docs/operator-acceptance.md), [docs/development.md](./docs/development.md), [docs/generated/cli-reference.md](./docs/generated/cli-reference.md), [docs/host-packaging.md](./docs/host-packaging.md).
- Architecture and control plane: [docs/harness-composition.md](./docs/harness-composition.md), [docs/control-plane.md](./docs/control-plane.md), [docs/external-integrations.md](./docs/external-integrations.md), [docs/support-skill-policy.md](./docs/support-skill-policy.md), [docs/runtime-capability-contract.md](./docs/runtime-capability-contract.md), [docs/capability-resolution.md](./docs/capability-resolution.md), [docs/agent-task-envelope.md](./docs/agent-task-envelope.md).
- Skill and validation policy: [docs/public-skill-validation.md](./docs/public-skill-validation.md), [docs/public-skill-dogfood.md](./docs/public-skill-dogfood.md), [docs/narrative-announcement-boundary.md](./docs/narrative-announcement-boundary.md), [docs/gather-provider-ownership.md](./docs/gather-provider-ownership.md).
- Memory and deferred work: [docs/artifact-policy.md](./docs/artifact-policy.md), [docs/deferred-decisions.md](./docs/deferred-decisions.md), [docs/retro-self-improvement-spec.md](./docs/retro-self-improvement-spec.md), [docs/support-tool-followup.md](./docs/support-tool-followup.md).
