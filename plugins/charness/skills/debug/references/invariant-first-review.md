# Invariant-First Review

`debug` step 6 uses this reference for workflow-boundary bugs where a producer
emits a diagnostic, readiness state, closeout claim, or status value that a
later operator-facing consumer must honor. It sits before ordinary sibling
search: first prove the cross-boundary invariant, then scan siblings by
interface shape.

Bug-class `issue resolve` consumes this substrate through
`../../issue/references/causal-review.md` without re-deriving the body.

## Name the invariant

Write one sentence in this shape:

```text
When <producer> emits <signal>, <final consumer> must <surface/refuse/act on>
that signal before the workflow can claim success.
```

Use concrete nouns for:

- the producer
- any transport, generated mirror, adapter, or durable artifact in the path
- the final consumer that determines operator-visible success, refusal, or
  readiness

Intermediate transport proof is useful, but it is not the final proof.

## Prove both ends

For propagated diagnostics and readiness decisions, producer-only proof is
insufficient. The debug artifact or causal-review input must record:

- **Producer proof**: the smallest fixture, command, or observation showing the
  source emits the intended signal.
- **Final-consumer proof**: the smallest fixture, command, or observation
  showing the final consumer surfaces, refuses, or acts on that signal.
- **Non-claims**: any host, adapter, generated mirror, provider roundtrip, or
  runtime path not proven, with a reason.

If final-consumer proof is unavailable, say so explicitly and decide whether
the slice can still ship as diagnostic-only, must defer with a `follow-up:`
identifier, or must stop for stronger evidence. Do not describe producer proof
as end-to-end workflow proof.

## Scan by interface shape

After both ends are named, scan siblings by interface shape, not issue numbers,
filenames, or exact keywords. Common matching shapes:

- the same producer/consumer contract
- a propagated diagnostic, readiness, status, or closeout field
- a generated or exported mirror of the same signal
- an adapter boundary that translates the signal
- a final operator-facing gate that can claim success while missing the signal

Use `sibling-search.md` for the four-axis classification, proof-level labels,
and follow-up rules. This reference narrows what counts as a real sibling for
workflow-boundary propagation bugs: the location must share the interface
shape, not just vocabulary.

## Output

Record:

- `Invariant:` one sentence naming producer, signal, and final consumer
- `Producer proof:` command, fixture, observation, or artifact path
- `Final-consumer proof:` command, fixture, observation, or artifact path
- `Interface-shape sibling scan:` patterns searched and concrete locations
- `Non-claims:` unproven hosts, adapters, mirrors, providers, or runtime paths

## Over-reach check

State the simplest evidence that the final consumer is the workflow surface
that decides success, refusal, or readiness. If that cannot be defended, the
review is still at producer or transport scope and must not claim final
workflow coverage.
