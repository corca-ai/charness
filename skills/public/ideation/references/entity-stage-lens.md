# Entity/Stage Lens

Use this lens when the idea involves systems, workflows, or evolving state over
time.

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

Do not force the split for a simple idea that is still one compact concept.

## Portable Borrowing Rule

The idea came from Ceal's `entity-stage-design` skill, but `ideation` should
borrow only the conceptual separation. It should not inherit preview-mode
rendering, host-specific environment sections, or step-by-step document
generation as mandatory behavior.
