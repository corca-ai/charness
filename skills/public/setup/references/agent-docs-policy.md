# Agent Docs Policy

`setup` owns one explicit repo-level host policy:

- `<repo-root>/AGENTS.md` is the canonical repo instruction file
- `CLAUDE.md` should symlink to `<repo-root>/AGENTS.md` when Claude compatibility is needed
- when the repo requires bounded fresh-eye or critique-style subagent review
  as a stop gate, `<repo-root>/AGENTS.md` should carry a dedicated
  `## Subagent Delegation` section that says this review is the explicit user
  delegation request for that bounded scope and is already delegated by the
  repo contract
- for Charness-managed repos, that rule should also name all repo-mandated
  bounded-review gates as authorized to spawn bounded reviewers: task-completing
  `setup`, `quality`, `critique`, `release`, and GitHub `issue`
  resolution/closeout runs. A Critique-only heading is too narrow for this
  policy
- when adapter-declared policy sources imply delegated review but
  `<repo-root>/AGENTS.md` lacks the explicit host-spawn rule, emit a reviewable
  recommendation instead of treating phrase matching as a hard fact
- the `AGENTS.md` section is rung 1 of an authorization ladder, not its only
  rung. A repo may instead carry a structured grant in
  `<repo-root>/.agents/subagent-delegation.json` (rung 2), or be asked once
  (rung 3) — see `../../../shared/references/fresh-eye-subagent-review.md`,
  *Where The Delegation Request Comes From*. Do not report a repo that granted
  at rung 2 as lacking the delegation surface, and do not write the `AGENTS.md`
  block over a recorded `declined` without surfacing the conflict: writing rung 1
  silently overrides the user's recorded answer
- when the dedicated `## Subagent Delegation` section acknowledges that a
  higher-priority system, developer, or host policy may prohibit spawning,
  accept that boundary as truthful; emit an advisory only when the wording
  defers the standing request for a future user approval, authorization, or
  consent event before spawning
- compact AGENTS contracts are valid when the section carries the irreducible
  host-read-time invariant: a `standing delegation request`, `canonical scopes`,
  concrete host block reporting, no `same-agent` substitute, and the
  `spawn shape` rule (a named spawn can strand its result silently, so the rule
  has to bind before any spawn, not only on the review path). The expanded
  template below remains the safest copy-paste default, but validators should
  not force every consumer repo to keep the full rationale in root AGENTS.
- when `<repo-root>/AGENTS.md` carries Charness goal/skill routing (a
  `## Skill Routing` block that names installed skill metadata/catalog facts, or explicit Charness
  goal/achieve routing), it should carry a compact `## Commit Discipline` rule:
  commit meaningful implementation/workflow slices as they finish, keep commits
  scoped, and do not report a task-completing goal as done while meaningful work
  remains uncommitted unless deferral is explicit. Distinguish this from the
  durable-artifact rule below — slices are committed as they finish, while
  meaningful `charness-artifacts/` changes are repo state and commit targets.
  When a goal-routed body lacks this rule, the inspector emits a reviewable
  `commit_discipline_drift` finding instead of rewriting the existing body
- when a repo uses Charness durable artifacts, `<repo-root>/AGENTS.md` should say
  meaningful `charness-artifacts/` changes are commit targets, and
  current-pointer helpers should no-op when canonical content has not changed
- when a repo uses Charness announcement or release-note workflows,
  `<repo-root>/AGENTS.md` should ask agents to preserve announcement-ready
  commit bodies for meaningful behavior changes: issue linkage,
  human-visible value, verification, and operator/apply notes when relevant
- when a repo uses Charness dynamic workflows / multi-agent orchestration,
  `<repo-root>/AGENTS.md` should carry a `## Dynamic Workflows` standing
  pre-authorization: dynamic-workflow use is pre-approved when it genuinely earns
  its cost (fan-out coverage, adversarial confidence, scale one context cannot
  hold), appropriateness stays the agent's judgment, canonical fits are named
  (handoff chunked-routing, achieve goal design/decomposition, review/quality
  fan-outs), and a scale-to-the-task guardrail is included. This is the
  orchestration sibling of the delegation standing request and exists because the
  Workflow tool otherwise requires an explicit per-session opt-in. Keep it
  affirmative like the delegation block; a generic "only orchestrate when the
  user explicitly asks" host default is satisfied by the repo contract
- for Charness-managed Codex spawning, `<repo-root>/AGENTS.md` should apply the
  Codex default profile to every coding, review, and dynamic-workflow subagent:
  `gpt-5.6-terra`, `medium` reasoning effort, and `fork_turns: "none"` when
  caller-provided model/reasoning overrides are used. A consciously bounded
  parent-history count is the exception: Codex V2 defaults to `fork_turns: "all"`,
  which rejects caller-provided model/reasoning overrides. This is a
  Codex-specific host mapping; other hosts use their own adapter mappings.

## Deterministic Cases

For a narrow host-docs-only normalization, use
`$SKILL_DIR/scripts/normalize_host_docs.py --repo-root <repo> --execute`
instead of hand-writing only `AGENTS.md`; it preserves the same deterministic
cases below and blocks when a real `CLAUDE.md` needs a merge decision.

- no `<repo-root>/AGENTS.md`, no `CLAUDE.md`
  - create `<repo-root>/AGENTS.md`
  - create `CLAUDE.md -> AGENTS.md`
- `<repo-root>/AGENTS.md` exists, `CLAUDE.md` missing
  - create the symlink
- `CLAUDE.md` already symlinks to `<repo-root>/AGENTS.md`
  - leave it alone

## Ask-The-User Cases

- `CLAUDE.md` exists as a real file and `<repo-root>/AGENTS.md` is missing
  - ask whether to promote `CLAUDE.md` content into `<repo-root>/AGENTS.md` and replace
    `CLAUDE.md` with a symlink
- both exist as real files
  - ask whether to merge the meaningful Claude-only content into `<repo-root>/AGENTS.md`
    and replace `CLAUDE.md` with a symlink

## Rule

Do not silently overwrite or merge meaningful user-authored host instructions.

When the repo uses bounded fresh-eye or critique-style subagent review as a
stop gate, prefer a dedicated `## Subagent Delegation` section that records the
repo owner's standing request for the named scopes. The request does not
override system, developer, or host instructions with higher priority; a
runtime prohibition must be reported rather than worked around.

Recommended template (copy verbatim, then adapt scope names if the repo adds
or renames bounded reviewer scopes):

```markdown
## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are **already delegated**
  by this repo contract; this is the repo owner's explicit user delegation
  request for the named bounded reviewer scopes.
- When the host permits spawning, **do not wait for a second user message**.
  Task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue`
  resolution/closeout review runs must spawn bounded reviewers when the
  contract calls for them.
- A higher-priority system, developer, or host instruction may prohibit a
  spawn; the repo request cannot override it. If the host blocks subagent
  spawning at runtime (Agent tool absent or API-level rejection), stop and
  report the concrete host signal explicitly.
- **Do not substitute a same-agent pass.** Fresh-eye review means a different
  agent context; if that context cannot be obtained, leave the review
  unproven.
- **Spawn shape, for every spawn — not only reviews.** Spawn one-shot subagents
  **without** a host addressing or team name. On at least one host a name
  silently routes the spawn to a mailbox channel: the spawn succeeds, the agent
  runs correctly, and completion emits an idle notification instead of returning
  the result, with no retrieval tool exposed to read it. Reserve a name for an
  agent you will address repeatedly, and only after confirming the retrieval tool
  exists in this session. A spawned agent is not a received result; an idle
  notification reads like success and is not one. Missing findings are a delivery
  failure to report and to retry once unnamed, never a subagent that returned
  nothing and never grounds for a same-agent pass.
- For Codex spawning, apply `gpt-5.6-terra` with `medium` reasoning effort to
  every coding, review, and dynamic-workflow subagent when the host exposes
  those controls. With caller-provided model/reasoning overrides, use
  `fork_turns: "none"` unless a bounded parent-history count is needed: the
  Codex V2 default `fork_turns: "all"` rejects those overrides. Other hosts use
  their own adapter mappings.
```

The block above keeps every required substring the inspector checks for:
`explicit user delegation request`, `already delegated`, `second user message`,
`host blocks`, `same-agent pass`, plus `setup`, `quality`, `critique`,
`release`, and `issue`. It also makes the higher-priority instruction boundary
explicit so the standing request is not mistaken for an override.

Compact form is accepted when a repo deliberately keeps root AGENTS short:

```markdown
## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are a standing delegation
  request. Canonical scopes: task-completing `setup`, `quality`, `critique`,
  `release`, and GitHub `issue` resolution/closeout review runs. Report a host
  block explicitly; same-agent substitutes are forbidden.
- Spawn shape, for every spawn: spawn one-shot subagents without a host
  addressing or team name. A name can route the spawn to a mailbox channel with
  no reader, so the spawn succeeds and the findings never arrive; an idle
  notification is not delivery. Missing findings are a delivery failure to
  report and retry once unnamed.
- For Codex spawning, apply `gpt-5.6-terra` with `medium` reasoning effort to
  every coding, review, and dynamic-workflow subagent when the host exposes
  those controls. Use `fork_turns: "none"` for caller-provided
  model/reasoning overrides unless a bounded parent-history count is needed;
  the Codex V2 default `fork_turns: "all"` rejects those overrides. Other hosts
  use their own adapter mappings.
```

Do not hide `setup`, `quality`, `critique`, `release`, or `issue` spawn
authorization under a Critique-only heading or a generic operating list.

The standing request may acknowledge that higher-priority instructions can
prohibit spawning. Do not defer the request for a future consent event, such as
`once the user authorizes subagents`; report a concrete runtime block when one
actually occurs instead.

### Dynamic Workflow Standing Request

When the repo uses Charness dynamic workflows / multi-agent orchestration, add a
sibling standing-request section. It is judgment-gated, not a named-scope
allowlist — appropriateness is the agent's call, subject to higher-priority
instructions and actual host capability:

```markdown
## Dynamic Workflows

- The repo owner has a standing request to use a dynamic workflow (the
  multi-agent Workflow tool / orchestration) when it genuinely earns its cost —
  fan-out coverage, independent-perspective confidence, adversarial
  verification, or scale one context cannot hold — when the host permits it.
  Do not wait for a second user message solely to repeat that request.
- A higher-priority system, developer, or host instruction may prohibit a
  workflow; the repo request cannot override it.

- Canonical fits: `handoff` chunked-routing, `achieve` goal design / slice
  decomposition, and review/quality adversarial fan-outs. Any task qualifies
  when the same cost/benefit holds.
- Guardrail: scale to the task — scout inline first, then fan out; do not spin
  up dozens of agents for trivial or single-fact work.
- Report a runtime block (Workflow/Agent tool absent, API-level rejection)
  explicitly; do not claim that orchestration ran when the tool was unavailable.
```

A repo may raise this from judgment-gated to a default — parallel first, serial
only for a real data dependency or a single-writer surface — by saying so in its
own block. Two properties travel with that stronger form: name the *capability*
(fan-out, independent confidence, adversarial review, detached execution) rather
than one host's product word for it, since those names go stale exactly as a
pinned model id does; and keep the proof floor, because N agents reporting
success is not N verified outcomes. Repos that adopt the stronger default should
keep the detail in a linked convention doc rather than growing the root file.

When the repo routes work through Charness goals or skills, prefer a short
`## Commit Discipline` rule like:

- Commit meaningful work slices as they finish; keep each commit scoped to one
  understandable unit instead of one giant end-of-run commit.
- Treat meaningful `charness-artifacts/` changes as repo state and commit them
  with the work they support.
- Do not report a task-completing goal as done while meaningful implementation,
  workflow, or artifact work remains uncommitted, unless the deferral is
  explicit.

Keep this rule compact in root `<repo-root>/AGENTS.md`; the rationale (a long
autonomous run otherwise leaves the whole implementation uncommitted until a
human notices) belongs here, not in the root file. The two policies are
distinct: meaningful `charness-artifacts/` changes are commit targets, and
meaningful implementation/workflow slices are committed as they finish.

When the repo uses Charness artifacts, prefer a short rule like:

- Treat `charness-artifacts/` as repo state, not scratch.
- Commit meaningful durable artifact changes with the work they support.
- Current-pointer helpers should no-op when canonical content has not changed.
- If a helper rewrites an artifact without canonical change, treat that as
  invocation drift or a helper bug to fix.

When the repo uses Charness announcement or release-note workflows, prefer a
short commit-message rule like:

- For meaningful behavior changes, write a commit body when the subject alone
  does not preserve the announcement-ready intent.
- Include issue linkage, human-visible value, verification, and operator/apply
  notes when relevant.
- Merge commits that close issues should include close keywords and a summary
  body when the implementation branch commits are terse.
