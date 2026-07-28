# Why the Evidence-Surface Class Stayed Invisible
Date: 2026-07-28
Status: evidence gathered; the structural decision it feeds is OPEN and recorded
in [docs/handoff.md](../../docs/handoff.md) `## Discuss`.

## The question

Thirty defects across the repo's proof surfaces, in a repo with a large test
suite and many gates. Why did none of them surface before a one-off hunt went
looking, and are the fixes addressing the cause or the instances?

## What the evidence says

**They are not regressions. They were introduced already broken.**
`git log -S` on the defective expressions shows most were written once and never
revised — `scripts/check_coverage.py`'s `coverage = covered / total if total
else 1.0` dates to 2026-04-22 and was untouched until 2026-07-28. The defect was
the *original* code, not decay in it.

**The sharpest single data point.** D4 — the distinct-channel HTTP probe that
confirmed on any HTTP 200 with at least one body byte — was introduced by commit
`e45f71d2` (2026-06-20), titled:

```text
achieve(phase4 WS-1): release publish non-terminality
  — rung-1 presence floor + rung-2 distinct-channel observer
```

That is the commit implementing north-star **P4** (at irreversible boundaries,
confirm through a different evidence channel). Implementing P4 produced a P4
violation: an observer that confirms without observing. The principle was
understood and written down; the code that carried it out did not inherit it.

## Why nothing surfaced

Three mechanisms, and they compound:

1. **A fail-open gate emits no signal, by construction.** A wrong PASS produces
   no failure, no log line, no ticket. There is nothing for anyone to notice, so
   elapsed time is unbounded — months, here.
2. **A large suite is not many independent observations along this axis.** The
   author of a gate writes that gate's tests in the same sitting, from the same
   mental model. The blind spot in the code and the blind spot in its test are
   the *same* blind spot. Test count measures breadth, not independence.
3. **Every defect lives in the negative space** — what the check answers when
   there is nothing to check. At authoring time the example in front of you is
   non-empty, so the question does not arise. And the natural expression is the
   defective one: `if total else 1.0`, `if status == 200 and body`,
   `if tag == target_tag` are all what a careful person writes first.

## Are the fixes structural?

Partly, and the effective part is process, not code.

**Working, and structural:** the mandated bounded fresh-eye review per slice.
Hit rate **6 of 6 slices** — every slice's review found defects inside that
slice's fix, several of them the exact class under repair (the D1 fence-blind
fix, the E5 gate its own fix hard-broke, the D7 scope that stopped at the
payload and never reached the artifact). This is P4 applied to the *fix*, and it
is the only mechanism in this run that caught the class reliably.

**Working, and structural:** requiring a claim to state what it does NOT
establish — D4's `does_not_establish`, B2's `REVIEW: … was SKIPPED`, D7's
`evaluation_scope`. This is P5 read correctly: a gate may force a question; it
may not declare completion.

**Not structural:** everything else is instance repair. Nothing prevents the
next gate from having the same hole. The `scope: evaluated | empty |
not-configured` vocabulary is hand-applied at a handful of sites with nothing
requiring the next one to carry it, and the thirty were found by a one-off hunt
with five reviewers that is wired into nothing.

## What the north star forbids as a remedy

The obvious move — *add a gate that requires every gate to declare its
empty-scope behavior* — is the anti-pattern this repo's own diagnosis names:
the bloat is "the cost of meeting that failure with ever more bespoke gates".
Meeting a gate-quality problem with another gate applies the anti-pattern to
itself.

Candidate directions instead, for the open decision:

- **Make the correct shape the natural one (P1/P3).** An affordance, not a gate:
  a verdict constructor that already carries its scope, so writing one *without*
  a scope is more work than writing one with it.
- **Keep fresh-eye review at the gate-authoring boundary.** It is already 6/6;
  the change is recognizing it as the mechanism rather than a per-slice ritual.
- **Treat gate authoring as irreversible under the north star's own
  definition** — "a wrong success propagates somewhere you do not control … it
  enters shared history others build on". A gate that fails open ships to every
  consuming repo and every future session trusts it. If any teeth are justified,
  that is the argument for them.

## What is NOT claimed here

- The `git log -S` archaeology was run for four representative defects, not all
  thirty. Two of those four had later touches that did not change the defective
  expression; the "introduced already broken" claim is established for the ones
  checked and is a strong inference, not a census.
- The 6-of-6 review hit rate counts slices in this working session only.
- No claim that the candidate directions above are correct — they are the
  options the evidence supports, and the choice is the operator's.
