# Ideation vs Spec

`ideation` and `spec` are adjacent but different.

## Ideation

Use `ideation` to answer:

- what problem are we really solving?
- who is it for?
- what is the concept shape?
- which assumptions are still unstable?
- what is the right wedge or structure?

Outputs are concept-oriented.

## Spec

Use `spec` to answer:

- what exactly should be built?
- what counts as success?
- what constraints and acceptance criteria apply?
- what should implementation handoff look like?

Outputs are execution-oriented.

## Handoff Rule

`handoff` here does not require a separate ceremony or a brand-new artifact.
It means `spec` should be able to consume the current ideation documents or
summary with minimal reinterpretation.

Move from `ideation` to `spec` when:

- the concept is coherent
- the biggest assumptions are named
- the user-facing wedge or system shape is stable enough to describe clearly
- the current ideation docs are good enough for `spec` to refine rather than
  rediscover

If those are not true yet, stay in `ideation`.
