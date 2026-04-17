# Angle Selection

Pick angles that create different failure stories, not five copies of "what if
this breaks."

Good default angles for a non-trivial decision:

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

Canonical execution uses subagents. If the host cannot provide them, stop and
say the canonical premortem path is unavailable rather than collapsing into a
same-agent self-review.

Rotate or swap angles when the decision is narrower:

- breaking change boundary
- release-time operator proof
- external consumer migration
- install/update/support behavior
- policy or security posture

Keep the angle set bounded.
Three strong angles plus one counterweight pass is usually better than six weak
angles and no triage.
