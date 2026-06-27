# Generative Sequence

Use this lens only when order affects correctness, uncertainty reduction, or
downstream unlocks. First name the capability failure. If the failure is not
sequencing-shaped, do not force this lens.

This reference absorbs the reusable part of `genseq3`: improve a whole by
choosing the next transformation that strengthens the current structure, not by
adding a longer feature list or checklist.

## Applicability Test

Before using this lens, answer:

- What capability is currently weak or missing?
- Does the order of work materially change correctness, reversibility, learning,
  or later options?
- Is there a current center that can be strengthened with one bounded
  transformation?

If the answer is no, use the local workflow's normal judgment path. A generative
sequence is a lens, not a mandate.

## Core Moves

- Perceive the current whole before naming actions.
- Separate centers already present from centers still to create.
- Choose the next center whose strengthening most improves the whole.
- Make one transformation at a time.
- Prefer the smallest live proof that can teach the next step.
- Add durable checkpoints before dependent work.
- Stop at the requested whole; do not expand the scope because the sequence has
  more possible moves.
- Leave the target workflow more usable in place; a move card that only proves
  this vocabulary was applied is not enough.

## Route Shapes

Use route names sparingly to compress the plan when they clarify sequencing:

- `Pilot-and-Scale`: prove one small live case, then generalize.
- `Vertical-Slice-Growth`: grow through a full thin path before widening.
- `Anchor-then-Enclose`: establish the governing center before surrounding
  detail.
- `Align-then-Prototype`: settle commitments before construction.
- `Open-then-Locally-Grow`: keep options open, then deepen where evidence
  appears.
- `Envision-then-Provision`: name the whole, then supply the supports it needs.

When no route shape fits, stay with the core moves instead of inventing a label.

## Quality Move Card

For quality or skill-improvement work, apply this card only to recommended moves,
not every finding:

- capability needed: the user or agent capability this move improves
- current centers: the existing structures that already help
- next center: the one center to strengthen next
- transformation: the bounded action
- proof boundary: the smallest evidence that would show the move worked
- move type: cleanup/delete, ownership split or merge, helper extraction,
  interface narrowing, dogfood/evidence, gate reuse, floor candidate,
  defer/watch, or no-op
- enforcement posture: `advisory`, `describe-first`, `existing-gate-reuse`,
  `candidate-floor`, or `no-gate`

`candidate-floor` is exceptional. It requires the repo's north-star and
floor-addition-restraint records before it can become executable.

## Non-Goals

- Do not turn this into universal project doctrine.
- Do not use it to justify more gates by default.
- Do not embed the full lens inside one public skill when a shared reference can
  serve multiple workflows.
- Do not make every observation produce a card; the card is for recommended
  moves.
