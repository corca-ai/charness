# Angle Selection

Pick angles that create different failure stories, not five copies of "what if
this breaks."

Good default angles for a non-trivial decision:

- `customer-of-this-capability`: what the user or downstream agent experiences
  on the first real use, including missing setup, stale adapters, thin defaults,
  confusing next actions, and silent fallback behavior
- `blast-radius`: what breaks for current users, operators, or consumers
- `implementation integrity`: what hidden coupling or duplicate logic makes the
  plan less safe than it looks
- `future maintainer`: what a new reader will misread, reopen, or delete
- `doc and source-of-truth cascade`: what named docs, examples, or packaged
  mirrors become misleading after the change
- `devil's advocate`: strongest argument for keeping the current design

Subagent sizing:

- minimum: two contrasting angle subagents plus one separate counterweight
  subagent
- default: three angle subagents plus one counterweight subagent
- widen to four angle subagents only when the decision spans multiple durable
  surfaces, a breaking migration, or a release/install/doc cascade
- if you cannot name four meaningfully different angles, stay at two or three
  instead of inventing filler

The parent review coordinator owns spawning those angle and counterweight
subagents. A delegated angle reviewer should run the assigned lens directly and
should not spawn another reviewer unless the parent explicitly asks for
recursive delegation.

Canonical execution uses subagents. Before a parent reports that path as unavailable, run the capability check in `subagent-capability-check.md` — attempt the bounded subagent setup, resolve availability uncertainty, and cite the concrete host signal. If the host still cannot provide subagents, say the canonical premortem path is unavailable and leave the host-side contract gap visible. Do not collapse into a same-agent self-review.

Rotate or swap angles when the decision is narrower:

- skill, adapter, bootstrap, or example changes where the main risk is a bad
  first run for the skill's customer
- breaking change boundary
- release-time operator proof
- external consumer migration
- install/update/support behavior
- policy or security posture

Keep the angle set bounded.
Three strong angles plus one counterweight pass is usually better than six weak
angles and no triage.
