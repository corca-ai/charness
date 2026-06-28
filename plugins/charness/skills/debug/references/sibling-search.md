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
`decision:`, `proof:`, and a `follow-up:` field when the decision defers the
sibling outside the slice. Decide at artifact close-out whether to bundle into
the current fix, keep diagnostic-only, mark an intentional boundary, or defer
as a follow-up. Record the decision with location so the next reader inherits
the list.

## Declare cross-file scope

A sibling search that never leaves the subject file has not done the `same layer`
or `abstraction up` axes — both look for the pattern "in different files,
different layers." To keep that requirement enforceable rather than aspirational,
the closeout of the current artifact (`debug/latest.md`) must record an explicit
marker in `## Sibling Search`:

- `cross-file: <path-or-axis note>` — name at least one sibling location that
  lives outside the subject file (the file the bug was found in). This can be a
  standalone bullet or an inline `| cross-file: ...` field on an axis bullet.
- `no cross-file sibling: <reason>` — the justified escape when the pattern
  genuinely cannot exist outside the subject file (e.g., a config unique to one
  module). State why, so a reviewer can judge the claim.

The trivial-fix short-circuit (`n/a — trivial fix; no plausible siblings`) also
satisfies the marker. `validate_debug_artifact.py` enforces this on the
`latest.md` form only (forward-only — the dated corpus stays immutable). The
marker is **authored**, not parsed from the prose axis bullets: the schema has no
`Subject:` source-file field to diff a foreign `file:line` against, so a parser
would either mass-regress correct artifacts or collapse to a gameable "any path
mention" check. Like `follow-up:`, the marker is an honesty contract that
surfaces the cross-file judgment for fresh-eye review, not an anti-gaming gate.

## Persist `valid follow-up` decisions

When a sibling is classified `valid follow-up outside the slice`, the closeout
must record a `follow-up:` identifier so the deferred work cannot disappear
into the artifact:

- `follow-up: <issue-url>` — preferred. File via the `issue` skill's
  adapter-resolved backend (`gh`, `acme github`, or whatever the host
  configured); do not invent a parallel filing path. The new issue body links
  back to this debug artifact so reviewers can re-derive the invariant.
- `follow-up: deferred <docs/handoff.md anchor>` — acceptable when the repo
  has no issue tracker or the next session will pick it up immediately. The
  handoff anchor is enough; chat-only deferral is not.

A sibling marked `valid follow-up outside the slice` with no `follow-up:`
identifier silently exports the cost of the scan to the next session. The
`validate_debug_artifact.py` validator fails closeout when this happens.

The other three decision values resolve their disposition inside the current
slice and so do not require a `follow-up:` field:
`same bug, fix now`;
`same class, diagnostic-only for this slice`;
`intentional plain-text or non-rendering boundary`.

For the `abstraction up` axis, `same class, diagnostic-only for this slice`
means an inspected no-action finding, not deferred ownership. If the entry names
unresolved repo-level or structural work, record one owner instead: bundle the
fix now, mark an intentional boundary with reason, give a proof-backed
no-action reason, or add a valid `follow-up:` identifier. The debug artifact
validator blocks abstraction-up diagnostic-only entries that describe unresolved
structural work without a follow-up, and blocks entries that lack a no-action
reason.

For schema alignment across skills, see
`../../critique/references/counterweight-triage.md` (the `action: file-issue`
field maps to a `follow-up:` URL here) and
`../../impl/references/verification-ladder.md` (the `Lint Gate`
`ran-fail-deferred` state takes the same `<issue|anchor>` identifier).

## Trivial-bug short-circuit

When the fix is a single-file typo, rename, or comment correction and the
abstracted pattern is "this exact literal text," record
`n/a — trivial fix; no plausible siblings` and keep going. The short-circuit
is reviewer-visible, not a default escape.

## Over-reach check

State the simplest evidence that the listed locations are actual instances of
the same pattern, not surface-level keyword matches. A sibling list that
cannot defend each entry against "this only shares a name" is over-reach.
