# Five Whys / Causal Chain

`debug` step 4 (enumerate diverse causes) and step 5 (test a falsifiable
hypothesis) walk from a reported symptom to a structural cause that a guard,
test, contract, or observability surface could prevent. This reference owns
that RCA substrate: the causal-chain heuristics, the structural-cause
classification, and the "common bottoms that count vs. do not count" check.

`debug` is callable directly when no GitHub issue exists; bug-class
`issue resolve` invokes the same substrate through
`../../issue/references/causal-review.md` Lens 1 without re-deriving this
body.

## The walk

Walk from the reported symptom to a structural cause. Stop when the next "why"
would be either out of scope (organization-level), already mitigated by a
different gate, or untestable. The bottom of the chain should be something a
guard, test, or contract change could prevent — not "the developer made a
mistake."

## Common bottoms that count

- a missing invariant (no single source of truth for X)
- a missing contract (caller and callee agree implicitly, drift on edits)
- a missing gate (existing tests do not cover the failure mode)
- a missing observability surface (the bug was undetectable until manual)

## Common bottoms that do not count and should keep the chain going

- "human error" — the next why is "what made the error easy to commit"
- "race condition" — the next why is "what synchronization contract is missing"
- "edge case" — the next why is "what classifier put it outside the test set"

## Output

Produce a chain of ~3–7 whys with `file:line` evidence and end at a structural
cause that maps cleanly to a prevention surface. When the chain reaches a
candidate bottom, decide whether it counts (above) or keeps going. The
structural cause is the substrate that close-ledger lenses
(`../../issue/references/causal-review.md` Lens 1) consume; do not re-derive
this walk inside causal review.
