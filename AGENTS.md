# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://github.com/corca-ai).

## Start Here

- [docs/design-north-star.md](./docs/design-north-star.md) is the governing design standard: the harness briefs a capable judge and keeps teeth only where a wrong answer escapes. Default to judgment on reversible work; at irreversible boundaries (issue/PR close, release publish, external writes, deletions) success is provisional — confirm with a different observer and a different evidence channel, never a terminal green. When a gate, doc, or contract conflicts with this, the north star wins and the conflicting surface is what gets fixed.
- Session-opening routing, capability inventory, the `gather` rule for external sources, and validation-before-`hitl` routing are all owned by `## Skill Routing` below.
- Load matching skills before improvising, and continue active repo work from [docs/handoff.md](./docs/handoff.md).
- Cautilus is eval-only and ask-before-run: before any `cautilus evaluate ...`, consult `python3 scripts/plan_cautilus_proof.py --repo-root . --detail` and use the repo wrapper `python3 scripts/run_cautilus_eval.py` instead of a bare `cautilus evaluate` call. Full eval-only/disabled-surface contract: [skills/public/quality/references/cautilus-on-demand.md](./skills/public/quality/references/cautilus-on-demand.md).
- Read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md) before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts.
- Keep the harness portable: host-specific behavior belongs in adapters, presets, and integration manifests.
- Prefer validators and scripts over prose rituals; leave structured state when a tool cannot finish end-to-end.

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

- The repo owner has a standing request to use a dynamic workflow (the multi-agent Workflow tool / orchestration) when it genuinely earns its cost — fan-out coverage, independent-perspective confidence, adversarial verification, or scale one context cannot hold — when the host permits it. Do not wait for a second user message solely to repeat that request. Appropriateness is your judgment.
- A higher-priority system, developer, or host instruction may prohibit a workflow; this repo request cannot override it.

- Canonical fits: `handoff` chunked-routing over the live backlog, `achieve` goal design / slice decomposition, and review/quality adversarial fan-outs. Any task qualifies when the same cost/benefit holds; this is the orchestration sibling of the delegation standing request.
- Guardrail: scale to the task — scout inline first to find the work-list, then fan out; do not spin up dozens of agents for trivial or single-fact work. A wrong workflow result that ships is still a wrong answer that escaped, so keep the irreversible-boundary safeguards.
- If the host blocks orchestration at the runtime level (Workflow/Agent tool absent, API-level rejection), report the concrete signal explicitly; do not claim that orchestration ran.

## External Side Effects

- **Filing a GitHub issue is a STANDING approval.** Do not ask, and do not make
  an operator re-grant it per goal. Observing something worth filing and not
  filing it because the approval was not restated is the failure this removes: an
  unfiled finding is lost, while an issue is a reversible, low-cost record that
  can be closed.
- **`git push` is NOT standing. Ask for it, every time.** Committing is part of
  finishing repo work; publishing it is a separate act the operator owns, and a
  gate that happens to be green is not a request to push. When a push IS granted,
  the grant is conditional on the gates: `--no-verify`, disarming a check,
  loosening a floor, or shrinking a test's scope to reach a green push all revoke
  it. The gate refuses for real reasons and has been right every time it has.
- A granted push still owes the P4 confirmation: remote CI verified by a
  different observer AND a different channel than the push exit code. A green
  push is not a green build.
- **Closing an issue is a STANDING approval CONDITIONAL ON THE CLOSEOUT FLOOR:
  close it when the work is genuinely finished, and the floor is what defines
  "finished".** Concretely:
  `issue_tool.py validate-closeout-draft` reports `draft_verified`, a DELEGATED
  resolution critique ran BEFORE the close call, the classification's full
  ledger is carried by the carrier (for `bug`: `jtbd`, `root_cause`,
  `debug_artifact`, `siblings` with a decision AND proof, `prevention`), the
  `Behavior #N:` verdict names a channel distinct from the one that produced the
  fix, and `verify-closeout --expect-state CLOSED` reads the state back through
  the adapter. A close that cannot satisfy those is not finished, and the
  approval does not reach it.
  Do not ask when the floor is met; do not close when it is not.
- **The floor is the authorization, not a checklist to route around.** Weakening
  a ledger field to a placeholder, skipping the delegated critique, or reusing
  the fix's own channel for the behavioural verdict all revoke this approval.
- **Still per-request, and NOT covered by the standing approvals above:**
  `git push`, reopening an issue, PR creation, a release publish, a tag, a
  version bump, and any `cautilus evaluate` run. Each needs an explicit grant for
  the goal or phase that wants it, and that grant does not carry forward. The two
  standing ones are carved out because each is reversible AND already has teeth
  in front of it; the rest change state other people depend on.
- An issue filed under this standing approval still owes the `issue` skill's
  shape: the observed problem before any proposed solution, and a real
  reproduction or evidence path rather than a hunch.

## Phase Rules

- Treat `mutate -> sync -> verify -> publish` as hard phase barriers; sync generated, plugin, and export surfaces before validators.
- Treat meaningful `charness-artifacts/` changes as repo state and commit them with the work they support.
- Current-pointer helpers should no-op without canonical content change; unexpected rewrites are invocation drift or helper bugs.
- Treat critique, closeout, and commit as part of task-completing repo work, not optional follow-up.
- After verification passes for task-completing repo work, commit before answering follow-up usage/status questions or checking installed-machine state.
- **Do not pipe a GATE through `tail`/`head`.** Redirect it to a file and read that
  (`cmd > /tmp/x.txt 2>&1; grep -nE '^FAIL ' /tmp/x.txt`). Truncating a gate destroys the
  one fact you need and costs a full re-run to recover. This is reinforcement, not the mechanism — `run-quality.sh` and
  `run_slice_closeout.py` now NAME their failures in the last line, and `run-quality.sh`
  keeps each failing check's full output under `.charness/quality-failure-logs/`, so a
  truncated read stays actionable. The rule matters for gates that have not been taught
  that yet.

## Work Phase Map

- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md); it owns sync-before-verify order, generated surfaces, closeout, and mutation parallelism.
- Before reviewing slow gates, local-vs-CI validation cost, evaluator-backed validation, or quality-contract changes, route through `quality`; it owns validation posture and repo-local quality gate design.
- Before closing task-completing repo work, read [docs/conventions/operating-contract.md](./docs/conventions/operating-contract.md); it owns commit discipline, durable artifact inclusion, mandatory critique closeout, and session repair.
- Before changing repo operating contracts, prompt or skill surfaces, exports, or artifact policy, read [charness-artifacts/retro/recent-lessons.md](./charness-artifacts/retro/recent-lessons.md); it owns recent repeat traps that should change the next move.
- Before SHAPING a slice around a remedy some durable record already names (a deferred decision's "the better repair is X", a sweep row's proposed fix, an issue's suggested approach), verify that remedy's premise first — by reading, as often as by running. [docs/conventions/implementation-discipline.md](./docs/conventions/implementation-discipline.md) Change Discipline owns the rule; it fires at design time, one phase earlier than the rest of that file.
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
