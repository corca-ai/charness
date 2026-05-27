# Fresh-Eye Subagent Review

The canonical fresh-eye review path spawns bounded subagents. Before reporting
that path as blocked, confirm the host actually cannot provide them. Guessing
from priors is the exact failure mode this reference exists to stop.

Use this for bounded reviewer scopes owned by another skill, including
`critique`, `spec`, `quality`, `handoff`, and any skill that names a
fresh-eye subagent review as its canonical path.

## Reviewer Tier

When a skill spawns a bounded fresh-eye reviewer, it declares a reviewer *tier*
that expresses leverage, never a provider model name:

- `high-leverage`: reasoning-heavy judgment — critique angles and counterweight,
  release / issue / quality closeout review, and deployment-confidence scans.
- `standard`: routine bounded checks where the host's default reviewer model is
  enough.

The portable contract names only the tier. A host that exposes subagent model
overrides resolves the tier to concrete spawn fields (model, reasoning effort,
service tier); a host without that capability ignores the tier and spawns its
default reviewer. The tier is a request, never a hard requirement, so a host
that cannot honor it is not blocked for that reason.

Do not hardcode provider model names, reasoning-effort values, or service tiers
in skill prose or in this reference. The tier is host-plural: each host adapter
maps it to that host's strongest reviewer — for example a Codex host and a
Claude Code host resolve `high-leverage` to their own top reasoning model and
their own spawn fields — so the concrete values are host-specific and live in
the consuming skill's adapter, never here. The mapping is recorded once, under
`reviewer_tiers` in the critique adapter example at
`<repo-root>/skills/public/critique/adapter.example.yaml`; other skills cite this
policy and reuse the same tier names instead of repeating the mapping.

## Delegation Context

The caller that owns the review decides whether it needs fresh-eye subagents and
spawns them. Once a parent agent has delegated a bounded review task to a
subagent, that delegated subagent is already the fresh-eye reviewer for its
assigned lens. Critique angle and counterweight reviews are examples of bounded
review tasks; other skills may reuse the same parent-delegated rule for their
own fresh-eye reviewers.

Delegated reviewers should perform the assigned lens directly. They should not
try to spawn another subagent unless the parent explicitly requested recursive
delegation.

First branch for delegated reviewers:

- if your prompt says you are an angle reviewer, counterweight reviewer, or
  bounded fresh-eye reviewer, complete that lens directly
- do not run this capability check
- do not report `blocked` because nested subagent tools are unavailable
- return the requested findings or triage to the parent

Record the fresh-eye satisfaction context in the review result:

- `parent-delegated`: the parent spawned this reviewer, and the reviewer
  completed the assigned lens directly
- `nested-delegated`: the assigned task explicitly required recursive
  delegation, and that nested delegation ran
- `blocked <host-signal>`: required delegation could not run; include the
  concrete missing tool, host refusal, policy block, or exhausted budget

Parent sessions that never spawned a fresh-eye reviewer cannot claim
`parent-delegated`. They must run the capability check below before calling the
canonical path blocked.

If `<repo-root>/AGENTS.md` contains a dedicated `Subagent Delegation` contract
that says repo-mandated bounded fresh-eye reviews are already delegated, treat
that as the explicit delegation request for those named bounded reviewer
scopes. Do not block merely because the live user message did not repeat the
word "subagent"; first try the host spawn tool under the repo contract. Only a
real tool refusal, missing spawn surface, exhausted host budget, or higher
priority instruction that forbids honoring repo delegation is a blocker.

## Required Before Declaring The Canonical Path Blocked

1. Attempt the bounded setup the skill calls for.
   - Try to open one fresh-eye or critique subagent with a tight scope and
     time box. A single probe is enough; you are not required to spawn the full
     reviewer set just to prove availability.
   - If you are already a bounded fresh-eye subagent spawned by a parent, do not
     run this probe again unless your assignment explicitly requires nested
     delegation. This includes assigned angle and counterweight reviewers.
   - Treat refusal-to-spawn, a concrete host error, or a missing agent-spawn
     tool as evidence. Prior belief is not evidence.
   - Availability means an actual host-exposed subagent/spawn tool or a real
     tool event from that tool. A shell-only runner, routing-only proof, or
     model self-report that subagents were "used" is not evidence that the
     canonical path ran.
2. Resolve availability uncertainty before assuming a cap.
   - If the host exposes an agent-count budget, a "maybe available" signal, or
     a tool surface you are unsure about, probe it first: read the relevant
     setting, inspect the tool surface, or ask the host.
   - A vague sense that agents "might be rate-limited" is not a cap. Unread
     documentation is not a cap.
3. Only then report the canonical path as blocked.
   - Cite the concrete signal: which tool was missing, what error the host
     returned, which operator instruction forbids subagents for this run, or
     which agent-count budget is already exhausted.
   - If the blocker is recorded in a durable artifact, write it as
     `host signal:` or `tool signal:` so validators can distinguish a real host
     block from the old "no explicit subagent request" misread.

## If The Canonical Path Is Blocked

Stop and record the concrete host signal. Treat it as a host/runtime contract
gap for this run, not as permission to replace the review with a same-agent
local pass. Do not present a local pass as the canonical fresh-eye review, and
do not call a same-agent substitute "good enough" just because the probe
failed.

## Do Not

- Do not assume subagents are unavailable from model priors.
- Do not require recursive subagent spawning from an already delegated reviewer
  unless the parent task explicitly asks for nested delegation.
- Do not treat "I am uncertain if the host supports this" as a block; resolve
  the uncertainty first.
- Do not claim bounded subagents ran unless the runtime actually exposed and
  used a subagent/spawn tool. If the only observed tool is shell execution,
  report the canonical path as blocked by the missing spawn tool surface.
- Do not silently collapse into a same-agent review and call it the canonical
  path.
- Do not name the blocker as "canonical path unavailable" without the concrete
  signal that made it unavailable.
- Do not report "the user did not explicitly allow subagents" when repo
  `Subagent Delegation` instructions already delegated bounded fresh-eye review
  scopes.
