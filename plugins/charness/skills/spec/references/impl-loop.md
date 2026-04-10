# Impl Loop

`spec` and `impl` are different responsibilities, but they are allowed to
iterate.

## Core Rule

If implementation discovers a fact that changes scope, behavior, acceptance, or
risk, update the canonical spec artifact.

Do not leave the truth only in chat or in commit history.

## Healthy Loop

1. write or refine the current contract
2. implement the smallest meaningful slice
3. observe what became clearer or turned out false
4. update the contract
5. continue or escalate back to `ideation` if the concept itself changed

## Escalate Back To `Ideation`

Do not keep patching the spec if implementation reveals:

- the real user or operator was misidentified
- the wedge or system shape changed materially
- the product posture changed
- the effort is now solving a different problem than the concept artifact claims

That is concept drift, not normal spec refinement.
