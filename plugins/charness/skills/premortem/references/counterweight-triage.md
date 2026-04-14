# Counterweight Triage

Premortem should not end as a flat list of fears.

After the angle pass, run one counterweight review that pushes back on
speculation, YAGNI, and maintenance cost amnesia.

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

Counterweight prompts should push especially hard on:

- speculative consumers with no reported user
- "free oracle" arguments that quietly require maintaining two paths forever
- aesthetic claims disguised as contract needs
- "reversal is expensive" when version control or a thinner wrapper would make
  reversal cheap

The purpose is not bravado.
The purpose is to stop a good premortem from turning into an unowned paranoia
backlog.
