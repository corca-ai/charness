# Sibling Search

`debug` step 6 (resolve and preserve the learning) walks beyond the immediate
failing surface to find where the same pattern lives elsewhere. This reference
owns the sibling-search substrate: the four scan axes, the mental-model
abstraction rule, and the keyword/proximity-only over-reach guard.

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

## Output

Return the exact patterns searched plus concrete locations the implementer
should inspect, organized by axis. Each location is `file:line` with a one-line
note on why it matches the abstracted pattern, not the keyword. Decide at
artifact close-out whether to bundle into the current fix or defer (record the
deferral with location so the next reader inherits the list).

## Trivial-bug short-circuit

When the fix is a single-file typo, rename, or comment correction and the
abstracted pattern is "this exact literal text," record
`n/a — trivial fix; no plausible siblings` and keep going. The short-circuit
is reviewer-visible, not a default escape.

## Over-reach check

State the simplest evidence that the listed locations are actual instances of
the same pattern, not surface-level keyword matches. A sibling list that
cannot defend each entry against "this only shares a name" is over-reach.
