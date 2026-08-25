# Pattern Ladder

Use this reference when a reported failure was reproduced or the same seam has
failed more than once. The ladder prevents a debug artifact from stopping at a
local symptom or jumping directly to an untested grand theory.

## Four Levels

Record one row per level:

```text
Level: observed failure | local pattern | interface sibling | pattern of patterns
Location: <file:line, command, or artifact>
Evidence: <what was actually observed>
Proof: static scan only | local payload proof | executable fixture | runtime/provider roundtrip
Disconfirming question: <what would show this level is wrong>
Decision: same bug, fix now | same class, diagnostic-only for this slice | intentional boundary | valid follow-up outside the slice
```

1. **Observed failure** — reproduce the exact report at the final consumer.
2. **Local pattern** — identify the code path that permits or hides it; include
   state transitions such as `missing → empty` or `skipped → passed`.
3. **Interface sibling** — find another producer/consumer boundary with the same
   contract shape, even if the names and files differ.
4. **Pattern of patterns** — name the shared mental model, such as “a local
   success signal is treated as an established verdict.” If a prevention
   surface is reached earlier, record later levels as `not-applicable` or
   `unproven` rather than silently stopping the ladder.

## Five Whys Discipline

For each why, cite the evidence that makes the next why necessary. Continue past
“human error,” “edge case,” or “race condition” to the missing contract,
invariant, gate, or observation surface that made the mistake easy to accept.
Stop when the next why is outside the slice, already owned by another gate, or
untestable; record that boundary explicitly.

## Anti-Generalization Rules

- A keyword match is not an interface sibling.
- One symptom is not a pattern of patterns without a second location, an
  external-seam observation, or an explicit `unproven` non-claim.
- Static similarity can justify a diagnostic-only decision, not runtime
  confidence.
- A deferred sibling needs a `follow-up:` owner per `sibling-search.md`.

The ladder complements, rather than replaces, `invariant-first-review.md`,
`detection-gap.md`, and `sibling-search.md`: the invariant proves both ends,
the detection gap identifies the missed gate, and this ladder explains why the
same failure shape can recur across layers.
