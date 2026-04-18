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

## When a degraded local pass is acceptable

Run the same-agent local pass only when one of these is explicitly true:

- the caller asked for a degraded fallback in the same turn
- an operator-level instruction (handoff, adapter config, session note) says
  subagents are off for this run
- the capability check above produced a concrete block and the caller already
  agreed that a degraded pass is better than stopping

Label the result as the degraded variant and record *why* the canonical path
was skipped. Do not present a local pass as the canonical premortem.

## Do not

- Do not assume subagents are unavailable from model priors.
- Do not treat "I am uncertain if the host supports this" as a block; resolve
  the uncertainty first.
- Do not silently collapse into a same-agent review and call it the canonical
  path.
- Do not name the blocker as "canonical path unavailable" without the concrete
  signal that made it unavailable.
