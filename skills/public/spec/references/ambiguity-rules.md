# Ambiguity Rules

The goal of `spec` is not zero ambiguity. The goal is to remove the ambiguity
that would cause churn in implementation.

## Ask When

Ask follow-up questions when ambiguity affects:

- user-visible behavior
- implementation scope
- risk level
- dependency choice
- migration or rollout path

## Decide Autonomously When

Choose a default and explain it when:

- one option is already implied by the concept docs
- the repo has a clear established pattern
- the difference is stylistic and not product-defining

## Defer When

Explicitly defer a decision when:

- implementation can proceed safely without it
- the choice belongs to a later rollout stage
- the user has not signaled enough product preference yet

Deferred items must stay visible in `Open Questions` or `Deferred Decisions`.
