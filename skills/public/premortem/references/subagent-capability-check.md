# Subagent Capability Check

The canonical premortem workflow spawns bounded subagents. Before reporting
that path as blocked, confirm the host actually cannot provide them. Guessing
from priors is the exact failure mode this reference exists to stop.

Other skills that use subagents as their canonical path (for example `spec`,
`quality`, `handoff`, and any caller of `premortem`) should reuse this protocol
instead of rewriting ad hoc availability wording.

## Required before declaring the canonical path blocked

1. Attempt the bounded setup the skill calls for.
   - Try to open one fresh-eye or premortem subagent with a tight scope and
     time box. A single probe is enough; you are not required to spawn the full
     angle set just to prove availability.
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
