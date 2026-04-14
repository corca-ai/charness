# Scenario Blocks

When a product has multiple first-class use cases, `narrative` should help the
durable docs answer one practical question quickly:

What do I bring, what do I run, what comes back, and what do I do next?

This is not a mandate that every README must use one rigid card layout. It is a
prompt to make the main scenario paths scannable for first-time readers.

## When To Use Them

Prefer short scenario blocks when at least one of these is true:

- the adapter declares multiple `scenario_surfaces`
- the repo clearly has multiple first-class use cases or evaluation archetypes
- the durable docs keep mixing several use cases into one abstract section

Do not force the block when the product really has one primary path.

## Slot Template

Use the relevant subset of these slots.
Do not fabricate a CLI slot for a product with no CLI, or an agent slot for a
product that does not expect agent-mediated use.

- `What you bring`
  Concrete files, state, or inputs the reader must already have.
- `Input (CLI)`
  One command and one realistic example argument when a CLI exists.
- `Input (For Agent)`
  One bounded sentence a human can paste to a skill-loading agent.
- `What happens`
  One short sentence about processing, with no implementation-tour detour.
- `What comes back`
  Separate quick signal (`stdout`, status) from durable files or packets.
- `Next action`
  Split what the human decides next from what an agent should do next.

## Fixture-First Rule

When the repo has checked-in fixtures, schemas, or example packets, point at
them directly instead of paraphrasing the shape in abstract language.

The goal is the same benefit that showed up in `Cautilus`: a reader should not
need to guess which file shape matches their situation.

## Coined Jargon

If the product uses coined terms, define them inline at first use.

Good:

- `held-out` (validation runs kept separate from tuning)
- `packet` (a durable machine-readable file that later commands can reopen)

Bad:

- introducing the coined term in the first-run path and only defining it in a
  later glossary or contract doc

Keep the inline definition brief. The point is to remove first-run friction, not
to write a terminology appendix into the README.
