# World Modeling

Use this lens when the concept involves systems, workflows, or evolving state.

## Durable Entities

Entities are the persistent parts of the concept:

- actors
- roles
- resources
- runtimes
- data stores
- capabilities
- boundaries

They answer: what exists, where does it live, who uses it, and what
relationships matter?

## Stages

Stages are the chronological parts:

- events
- transitions
- checkpoints
- resulting state changes

They answer: what happened, when, and what changed because of it?

## When To Split

Split entities from stages when:

- the user is mixing structure and chronology together
- a workflow has multiple checkpoints or phases
- the same durable object appears across several stages
- contradictions become easier to see when the timeline is separated
- the concept needs a cumulative world model rather than a flat summary

Do not force the split for a simple idea that is still one compact concept.

## Portable Borrowing Rule

The entity/stage separation pattern informed this design, but `ideation` should
borrow only the conceptual separation and cumulative world-model discipline. It
should not inherit preview rendering, host-specific environment sections, or
step-by-step document generation as mandatory behavior.
