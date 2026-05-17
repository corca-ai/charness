# Sibling Search

`debug` step 6 (resolve and preserve the learning) walks beyond the immediate
failing surface to find where the same pattern lives elsewhere. This reference
owns the sibling-search substrate: the four scan axes, the mental-model
abstraction rule, the sibling decision taxonomy, proof-level separation, and
the keyword/proximity-only over-reach guard.

`debug` is callable directly when no GitHub issue exists; bug-class
`issue resolve` invokes the same substrate through
`../../issue/references/causal-review.md` Lens 3 without re-deriving this body.

## Start from the mental model, not the noun

Start from the mental model that allowed the bug, not from the issue title's
nouns. Keyword and nearby-file search are useful, but they are only the first
pass. A sibling search that stops at keyword and proximity matches has not
done the work.

## The four axes

Scan four axes for each incident:

- **same layer**: the literal same code shape in other modules, scripts, or
  configs (concrete duplications)
- **abstraction up**: the issue is one instance of a more general pattern.
  Name the general pattern in a sentence. Then check whether other instances
  exist (often in different files, different layers, but sharing the
  generalized shape).
- **specialization down**: the issue is the surface of a more specific
  problem. Name the narrower problem and check whether it shows up in finer
  granularity within the same module.
- **mental-model siblings**: name the operator or implementer assumption that
  made the bug plausible, then scan structurally similar traps even when they
  use different names.

## Common mental-model trap shapes

Recurring shapes worth scanning for, regardless of vocabulary:

- missing lifecycle endpoints
- local checks not composed into aggregate surfaces
- mutation paths missing a readiness probe
- renderers hiding failing details
- safety checks that trust current working directory or an implicit default
  as the authority

## Classify each sibling decision

For bug-class work, closeout must classify every concrete sibling surfaced by
the scan. Use exactly one of these decisions per location:

- `same bug, fix now`
- `same class, diagnostic-only for this slice`
- `intentional plain-text or non-rendering boundary`
- `valid follow-up outside the slice`

Keep proof level separate from the decision. A sibling may be a real structural
match even when the current slice only has `static scan only` proof; do not
promote that to runtime confidence. Common proof levels are:

- `static scan only`
- `local payload proof`
- `runtime/provider roundtrip`
- `not inspected`

If provider behavior is the failure boundary, distinguish local serialization
or payload proof from a real provider roundtrip. Local proof can justify a
bounded fix, but it must not be described as end-to-end provider proof.

## Output

Return the exact patterns searched plus concrete locations the implementer
should inspect, organized by axis. Each location is `file:line` with a one-line
note on why it matches the abstracted pattern, not the keyword, followed by
`decision:` and `proof:` fields. Decide at artifact close-out whether to bundle
into the current fix, keep diagnostic-only, mark an intentional boundary, or
defer as a follow-up. Record the decision with location so the next reader
inherits the list.

## Trivial-bug short-circuit

When the fix is a single-file typo, rename, or comment correction and the
abstracted pattern is "this exact literal text," record
`n/a — trivial fix; no plausible siblings` and keep going. The short-circuit
is reviewer-visible, not a default escape.

## Over-reach check

State the simplest evidence that the listed locations are actual instances of
the same pattern, not surface-level keyword matches. A sibling list that
cannot defend each entry against "this only shares a name" is over-reach.
