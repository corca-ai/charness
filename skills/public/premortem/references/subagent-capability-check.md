# Subagent Capability Check

The canonical premortem workflow spawns bounded subagents. Before reporting
that path as blocked, confirm the host actually cannot provide them. Guessing
from priors is the exact failure mode this reference exists to stop.

Other skills that use subagents as their canonical path (for example `spec`,
`quality`, `handoff`, and any caller of `premortem`) should reuse this protocol
instead of rewriting ad hoc availability wording.

## Delegation Context

The caller that owns the review decides whether it needs fresh-eye subagents and
spawns them. Once a parent agent has delegated a bounded review task to a
subagent, that delegated subagent is already the fresh-eye reviewer for its
assigned lens. Premortem angle and counterweight reviews are examples of bounded
review tasks; other skills may reuse the same parent-delegated rule for their
own fresh-eye reviewers.

Delegated reviewers should perform the assigned lens directly. They should not
try to spawn another subagent unless the parent explicitly requested recursive
delegation.

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

## Required before declaring the canonical path blocked

1. Attempt the bounded setup the skill calls for.
   - Try to open one fresh-eye or premortem subagent with a tight scope and
     time box. A single probe is enough; you are not required to spawn the full
     angle set just to prove availability.
   - If you are already a bounded fresh-eye subagent spawned by a parent, do not
     run this probe again unless your assignment explicitly requires nested
     delegation.
   - Treat refusal-to-spawn, a concrete host error, or a missing agent-spawn
     tool as evidence. Prior belief is *not* evidence.
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

## If the canonical path is blocked

Stop and record the concrete host signal. Treat it as a host/runtime contract
gap for this run, not as permission to replace premortem with a same-agent
local pass. Do not present a local pass as the canonical premortem, and do not
call a same-agent substitute "good enough" just because the probe failed.

## Do not

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
- Do not turn a concrete spawn failure into an excuse for a degraded
  premortem; the next action is to surface the host-side contract gap.
- Do not name the blocker as "canonical path unavailable" without the concrete
  signal that made it unavailable.
