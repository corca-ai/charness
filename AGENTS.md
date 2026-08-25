# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://github.com/corca-ai).

## Start Here

- [docs/design-north-star.md](./docs/design-north-star.md) governs: brief a
  capable judge and keep teeth only where a wrong answer escapes. At irreversible
  boundaries, confirm through a different observer and evidence channel.
- Load matching skills before improvising, and continue active repo work from [docs/handoff.md](./docs/handoff.md).
- Before changing operating contracts, prompts, skills, exports, or artifacts,
  read [recent lessons](./charness-artifacts/retro/recent-lessons.md).
- Cautilus is eval-only and ask-before-run; use the repo planner/wrapper from
  [cautilus-on-demand.md](./skills/public/quality/references/cautilus-on-demand.md).
- Keep host behavior in adapters/presets/manifests, and prefer executable
  validators plus structured state over prose rituals.

## Skill Routing

At session start, a pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly. When hidden support/integration availability is unclear, run the read-only `charness catalog list --repo-root <repo> --summary` inventory. Treat its facts only as inventory; if the command returns nonzero, report the command failure. If the SessionStart hook is installed it may inject this context; it remains context-only.

External URLs or source links that should become working context for this repo route through `gather` before summarizing, implementing, or deciding from them.

Validation-shaped closeout or operator reading test requests go through `quality` validation recommendations before HITL or same-agent manual review.

Keep this block short. Detailed routing belongs in installed skill metadata and model judgment, not in a long checked-in catalog.

## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are **already delegated** by this repo contract; this is the repo owner's explicit user delegation request for the named bounded reviewer scopes.
- When the host permits spawning, do not wait for a second user message. Task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue` resolution/closeout review runs spawn bounded reviewers immediately when the contract calls for them.
- A higher-priority system, developer, or host instruction may prohibit a spawn; this repo request cannot override it. If the host blocks subagent spawning at runtime (Agent tool absent, API-level rejection), stop and report the concrete host signal explicitly.
- Do not substitute a same-agent pass. Fresh-eye review means a different agent context; if that context cannot be obtained, leave the review unproven.
- **Spawn shape, for EVERY spawn — not only fresh-eye reviews.** Spawn one-shot subagents **without** a host addressing or team `name`. On at least one host a `name` silently routes the spawn onto a teammate protocol: the spawn succeeds, the agent runs correctly, and completion emits an idle notification instead of returning the result — findings the parent can never read, because the matching retrieval tool (`SendMessage`) is often not exposed in that session. Reserve a `name` for an agent you will address repeatedly, and only after confirming the retrieval tool exists in this session. A spawned agent is not a received result: an idle notification reads like success and is not one. If findings do not arrive, that is a delivery failure to report and to retry once unnamed, never a subagent that returned nothing and never grounds for a same-agent substitute. Full rule, upstream lineage, and non-claims: [skills/shared/references/fresh-eye-subagent-review.md](./skills/shared/references/fresh-eye-subagent-review.md).
- Bounded reviewers run in the **shared parent worktree**: inspect prior versions read-only (`git show <ref>:<path>`) and never run index- or worktree-mutating git ops (`git checkout`/`restore`/`reset`/`stash`, or `git add` of files touched only to inspect them). Staging a base reversion silently corrupts the closeout commit; the canonical rule lives in [skills/shared/references/fresh-eye-subagent-review.md](./skills/shared/references/fresh-eye-subagent-review.md).
- **A WRITE-CAPABLE spawn requests its own worktree wherever the host offers one** (owner ruling 2026-08-15, S6). Read-only reviewers may share the parent tree under the rule above; anything that can write must not. This is an INSTRUCTION, not enforcement — charness cannot control where a host places a spawn, and claiming otherwise would repeat the prose-rule-as-enforcement mistake it replaces. What IS executable is the checkout side: `charness worktree create --path <path> --branch <branch> --prepare` asserts isolation as it creates, and `charness worktree doctor --require-isolation` refuses a shared checkout. Where a host exposes no isolation control, record that and keep the shared-tree hygiene rule. The three refusal mechanisms that were measured and rejected, and what the doctor does and does not prove, live in [operating contract](./docs/conventions/operating-contract.md) Critique Discipline.
- Bounded reviewers run read-only: on hosts with typed subagents, spawn them as `bounded-reviewer` ([.claude/agents/bounded-reviewer.md](./.claude/agents/bounded-reviewer.md)), and parents prove worktree+index integrity around each review with [skills/shared/scripts/reviewer_boundary_fingerprint.py](./skills/shared/scripts/reviewer_boundary_fingerprint.py) snapshot/verify; a failed verify quarantines that review's approvals.
- **A slice that changes VERDICT LOGIC on a proof surface (a gate, validator, or any code rendering a verdict about other code or artifacts) owes a SECOND bounded review round reading the repaired surface** — one round is not enough for this class: every measured slice shipped a fix carrying the class it fixed, and the round that read the REPAIRS has caught blockers the first round could not see. The trigger is what the surface decides, not that its file was touched, a first round that produced no repairs discharges the obligation, and the cap is two rounds (round-2 repairs are recorded as accepted-unreviewed). Full rule: [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md) Critique Discipline.
- **Subagent model/effort defaults are per-host, not one global value.** Use the
  host's own subagent controls and its typed agents where they exist
  (`bounded-reviewer` for read-only review scopes), inheriting the session model
  by default; choose a different tier only when the task clearly warrants it. A
  host-specific model or flag request belongs in that host's adapter or preset,
  not here — naming one in this file bakes a model id into the contract and it
  goes stale silently. When a higher-priority policy restricts per-subagent
  controls, proceed and state that limitation.

## Dynamic Workflows

- **Parallel execution is the default shape of work here**, not an optimization.
  Decompose a request into its independent parts and run them concurrently;
  running independent parts one at a time now needs a reason.
- Dynamic workflow/orchestration use is standing-approved, subject to
  higher-priority system/developer/host instructions and host capability, when
  fan-out, independent confidence, adversarial review, or context scale earns
  its cost. Do not wait for a second user message solely to repeat the standing
  request. Report a concrete host block; never claim an unavailable workflow ran.
- Which channels this covers, why host product names are examples rather than
  contract, the disjoint-writer rule, and the proof floor a fan-out must still
  clear: [parallel execution](./docs/conventions/parallel-execution.md). The
  canonical root-doc shape lives in
  [agent-docs-policy.md](./skills/public/setup/references/agent-docs-policy.md#dynamic-workflow-standing-request).

## External Boundaries

- Filing an issue is standing-approved. Closing one is standing-approved only
  after the `issue` closeout floor; details live in
  [External Side-Effect Discipline](./docs/conventions/operating-contract.md#external-side-effect-discipline).
- Push, reopen, PR creation, tag, version bump, release publish, and Cautilus
  evaluation each require an explicit phase-scoped grant. Never infer one from a
  green gate.
- A grant is revoked by `--no-verify`, a weakened floor, or narrowed proof.
  Push/release still require distinct-channel hosted/public readback.

## Execution Discipline

- Follow [implementation discipline](./docs/conventions/implementation-discipline.md)
  for `mutate -> sync -> verify -> publish`, generated surfaces, and premise
  checks. Follow the [operating contract](./docs/conventions/operating-contract.md)
  for commits, artifacts, critique, closeout, and session repair.
- Treat task-completing critique, closeout, and commit as work, not follow-up.
  Commit after verification before switching to status/installed-machine checks.
- Do not pipe a gate through `tail`/`head`; redirect to a file and inspect it.
  This repo's `run-quality.sh` retains per-check failures under
  `.charness/quality-failure-logs/` and names recovery in its final receipt.
  Consumer hook configuration follows
  [hook-failure-visibility.md](./skills/public/setup/references/hook-failure-visibility.md).

## Work Routing

- Slow gates, local-vs-CI cost, evaluator-backed validation, and quality-contract
  changes route through `quality` before implementation or HITL.
- Issue/PR close, release, deletion, and proof-surface changes require the
  irreversible-boundary review named by the north star and operating contract.
- Before claiming an issue or operator request closable, map requested outcomes
  to executed proof and run the required fresh-eye critique.

## Documentation Principles

- [docs/index.md](./docs/index.md) is the canonical entry point for the flat
  documentation wiki; [docs/README.md](./docs/README.md) is only a compatibility
  pointer.
- Evergreen `docs/` pages state their status (`current`, `conditional`, or
  `generated`), own one question, name their source of truth, and describe
  current behavior. They are written like code: small changes, explicit
  ownership, relative links, deterministic link/graph checks, and generated
  pages changed only through their producer.
- Live session state (`docs/handoff.md`), active plans, and operator acceptance
  are labeled exceptions. Dated proposals, superseded decisions, raw evidence,
  and retros belong under `charness-artifacts/`; they explain history but do
  not silently override current docs.
- A stale or duplicate page is classified before it is moved or deleted:
  update inbound links, preserve a compatibility pointer when needed, then run
  `check_doc_links.py`, `check_docs_graph.py`, and the quality doc gates. Graph
  reachability is not proof that a page is accurate or current.

## Repository Map

- Current state: [handoff](./docs/handoff.md), [quality](./charness-artifacts/quality/latest.md), [recent lessons](./charness-artifacts/retro/recent-lessons.md).
- Documentation entry point: [docs/index.md](./docs/index.md); architecture audit and migration contract: [evergreen documentation spec](./charness-artifacts/spec/2026-08-25-docs-architecture-evergreen.md).
- Operator path: [acceptance](./docs/operator-acceptance.md), [development](./docs/development.md), [CLI reference](./docs/generated/cli-reference.md), [host packaging](./docs/host-packaging.md).
- Architecture/control plane: [composition](./docs/harness-composition.md), [control plane](./docs/control-plane.md), [external integrations](./docs/external-integrations.md), [runtime capabilities](./docs/runtime-capability-contract.md), [capability resolution](./docs/capability-resolution.md).
- Policy/memory: [public skill validation](./docs/public-skill-validation.md), [dogfood](./docs/public-skill-dogfood.md), [artifact policy](./docs/artifact-policy.md), [deferred decisions](./docs/deferred-decisions.md).
