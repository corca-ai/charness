# Expert Lens

The expert lens is mandatory, but it should stay lightweight by default.

## Goal

Produce a counterfactual that upgrades the next session:

- stronger question framing
- better evidence discipline
- better sequencing
- better failure prevention

## Default Pattern

Use two named experts with different lenses:

- one expert for the domain itself
- one expert for decision quality, operating discipline, or system design

Examples:

- software design: John Ousterhout + Charity Majors
- engineering management: Camille Fournier + Andrew Grove
- decision quality under uncertainty: Gary Klein + Daniel Kahneman

## Rules

- choose names that actually fit the domain
- do not always reuse the same pair when the work domain changed
- if the named experts would say effectively the same thing, pick a more
  divergent second lens
- synthesize the actionable difference, not just the persona voice

## Sub-Agent Use

If the retro is deep enough to justify it and sub-agents are available:

1. pick two named experts
2. give each a distinct question
3. merge their outputs into one `Expert Counterfactuals` section

If sub-agents are not used, write the two counterfactuals inline.
