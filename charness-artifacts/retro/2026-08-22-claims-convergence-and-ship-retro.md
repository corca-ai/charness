# Retro: make claims review converge, then ship

Goal: charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md

## Context

Two slices: declare what a claims verdict is about, then publish the bundle
three earlier slices had produced and could not ship.

## Window

From the predecessor goal's closeout to the published tag.

## Evidence Summary

The claims round itself, the release gate's two refusals, and two bounded
fresh-eye rounds on the scope split. Publication verified through the GitHub
API rather than tag state.

## Waste

**The dominant waste was gating by enumeration.** Six times this run the answer
to a red gate was "add your new thing to a hand-maintained list": an ownership
allowlist, a consumer-validator catalog entry, a validator-count pin, three
duplicate-family classifications, a link-only-line bar, and a runtime budget.
Each took a round trip, and none of them made a future instance safer — the next
new validator will summon the next person in exactly the same way.

The validator-count pin is the clearest case. The assertion above it already
states the real property ("every packaged validator has a decision"); the count
adds a chore and proves nothing further.

The scope classifier I wrote has the same disease and paid for it in review: a
hand-maintained prefix list plus "`.md` means narrative" classified a rolling
gate-input pointer as session narrative. The repair that held was a PROPERTY —
a dated filename stem — not a longer list.

**Second: reading instead of running.** Every defect I shipped this run would
have surfaced in seconds from the gate I did not run. The release gate refused
twice and was right both times.

## Critical Decisions

Fixing the convergence loop BEFORE publishing, on four rounds of evidence that
the other order does not terminate. Splitting by scope rather than by reviewing
less. Requiring a `pass` to carry what it waived, because the obvious failure of
a scope split is that it becomes a way to launder findings out of a release.

## North Star Alignment

The split is the north star's own shape: brief a capable judge, and keep teeth
only where a wrong answer escapes. A wrong blocker tally in a retro does not
escape; a false claim in a published record does.

## Expert Counterfactuals

Engelbart's system-improving-itself lens: I improved the artifact (the tool)
repeatedly and only once improved the process that produced the wrong artifact.
The counterfactual is to treat every "add it to the list" as a defect report
about the gate, not as a chore — which is what the next goal takes up.

## Next Improvements

- workflow — treat a hand-maintained enumeration inside a gate as a defect.
  When a gate asks to be extended, ask what property it is approximating.
  `tracked issue: #586`
- capability — the mutation harness has not run on `main` for days and its
  failure reads as a step failure rather than as unmeasured coverage.
  `tracked issue: #612`

## Sibling Search

The enumeration pattern is transferable and its siblings are named above: the
ownership allowlist, the consumer catalog, the count pin, the duplicate ledger,
the link-only bar, the runtime budget, and my own scope prefixes. All seven are
in this repo; none is portable-skill-shaped yet.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md

## Lesson Evaluation

Added 2026-08-23, after the pre-push continuity gate refused on this artifact for
having no such section. The disposition is derived, not guessed: both lesson-session
receipts dated 2026-08-22 (`b-release`, `proof-cost-portability-cadence`) are already
claimed by their own retros, so this retro's session has no receipt to claim and the
`missing-start` form is the accurate one.

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}
