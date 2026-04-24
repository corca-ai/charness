# Counterweight Triage

Premortem should not end as a flat list of fears.

After the angle pass, run one counterweight review that pushes back on
speculation, YAGNI, and maintenance cost amnesia.

In the canonical premortem path, the counterweight reviewer is a separate
subagent spawned by the parent. That reviewer should triage directly and record
`Fresh-Eye Satisfaction: parent-delegated`; it should not spawn a further
reviewer unless the parent explicitly requested recursive delegation.

Use four bins:

- `Act Before Ship`
  The concern changes the decision, acceptance, or release requirement now.
- `Bundle Anyway`
  The concern is real and cheap to fix while touching the surface already.
- `Over-Worry`
  The concern is hypothetical, aesthetic, or unsupported relative to the
  standing maintenance cost.
- `Valid but Defer`
  The concern is real, but deferring it is the honest tradeoff for this slice.

When a concern's evidence basis is easy to overstate, tag it before triage:

- `strong`: current source, a failing or passing gate, measured behavior, or a
  durable artifact directly supports the concern
- `moderate`: repeated local observations or adjacent repo evidence support it,
  but no standing gate owns it yet
- `weak`: the concern is expert judgment, plausible practice, or analogy and
  needs a small experiment before it can drive expensive work
- `contested`: available evidence points in different directions and the next
  move should reduce uncertainty before broad implementation

Counterweight prompts should push especially hard on:

- speculative consumers with no reported user
- "free oracle" arguments that quietly require maintaining two paths forever
- aesthetic claims disguised as contract needs
- "reversal is expensive" when version control or a thinner wrapper would make
  reversal cheap
- authority-only concerns that sound senior but cannot name the repo evidence
  they depend on

The purpose is not bravado.
The purpose is to stop a good premortem from turning into an unowned paranoia
backlog.
