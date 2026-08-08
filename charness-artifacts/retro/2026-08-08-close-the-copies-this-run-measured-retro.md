# Session Retro
Date: 2026-08-08

Goal: charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md

## Context

The `close-the-copies-this-run-measured` goal: three slices against three filed
issues. `#562` retire the owner-inspection locator content pin (a proof-surface
deletion two prior goals refused on budget grounds), `#561` put the
equality-versus-invariant probe-pin choice to D47's owner with both costs measured
without taking it, `#560` build the bundle-ready fixture the preflight contract had
declared with nothing implementing it. All three slices reached; `#562` closed and
verified; `#561` and `#560` resolved as their acceptance defined.

## Window

Commits `e6a4d67c` (slice 1), `841d1ceb` (slice 2), `2a545fe9` (slice 3),
`ac7b9ab2` (the `#562` closeout carrier), on `main` from base `475c532f`.

## Evidence Summary

- FIVE delegated `bounded-reviewer` rounds: two on slice 1, one on slice 2, one on
  slice 3, and the `#562` resolution critique. 43 findings total. FOUR carried a
  boundary fingerprint (`reviewer_boundary_fingerprint.py` snapshot/verify BEFORE any
  repair) — windows `w-20260808T080751Z-45979`, `w-20260808T081659Z-66276`,
  `w-20260808T084443Z-149124`, `w-20260808T090259Z-192061`, every verify `clean` with
  empty drift. The resolution critique has NO fingerprint of its own; that is a gap in
  this run, not a window reused, and it is stated rather than papered over.
- 29 mutants run against SOURCE files (never the `plugins/` mirror); all killed
  after repair (16 on slice 1, 6 on slice 2, 7 on slice 3). NINE of slice 1's had to
  be re-run because the harness was broken, and three of those nine had SURVIVED.
- Construction proofs rather than assertions: the `stale_inspection` refusal string
  quoted before and its exit-0 acceptance after; `snapshot_not_rederivable` and
  `missing_file` still firing; a refusing `refreeze` shown mutating three
  checked-in artifacts; the residual drift message rendered and read back three
  times; `2 failed, 37 passed` -> `2 failed, 40 passed` with the live repo blocked.
- Broad suite at the bundle boundary: `1 failed, 7913 passed`, and the one failure was
  invisible from every slice gate — `test_issue_critique_observer` refused this run's
  own new resolution-critique artifact as `absent` because it carried no
  `## Fresh-Eye Satisfaction` record. Repaired in `ac7b9ab2` (the closeout carrier) by
  adding that section plus `## Reviewer Tier Evidence` and `## Boundary Ownership`.
  Final broad run: `Closeout verdict: completed`, broad pytest PASS in 60.7s under
  `--verification-lock`.
- `#562`: `validate-closeout-draft` -> `draft_verified`; `close-with-comment` ->
  `CLOSED`; `verify-closeout --expect-state CLOSED` -> `verified`.

## Waste

**The single largest waste was a broken mutation harness reporting nine false
kills.** `python3 -m pytest -q $T` with `T` holding two space-separated paths: zsh
does not word-split unquoted parameters, so pytest received one nonexistent path,
exited non-zero, and every mutant read as `killed`. Re-run correctly, three of nine
had SURVIVED. Cost: one wasted sweep plus a re-run, and it very nearly shipped a
slice claiming pinned repairs that were not pinned.

**Second: the same defect class three times, one per slice.** Each slice pinned a
repair's BEHAVIOUR and left its WIRING unpinned, and each was caught only by
mutation, never by reading:
- slice 1: `stamp_inspection`'s existence check (mutant F survived).
- slice 2: the exit-code assertion — the only one a stub artifact actually reaches,
  because the script exits 1 before the messaged assertions (mutant L survived, and
  the first repair had messaged the four assertions that never fire).
- slice 3: deleting the re-stamp call from the builder survived the entire suite,
  because the fixture copies bytes identically so the effect is invisible.

**Third: writing by analogy imported the analogy's facts.** The residual drift
message was modelled on the inventory one and inherited an inventory KEY NAME
(`kinds[*].count`, which the residual probe does not have) and an
inventory-sized surface list (one entry where five surfaces carry the figures).

Not waste: the four delegated rounds. 32 findings including three blockers that
each invalidated a claim already written down as proven. Nor the bundle boundary —
one failure (`test_issue_critique_observer`) was invisible from every slice gate.

## Critical Decisions

- **Paying `#562`'s budget instead of shrinking the work.** Two goals refused it;
  this one planned two rounds as a COST. Round 2 found the partial-write CLASS that
  round 1's instance fix did not reach — a refusing `refreeze` mutating three
  checked-in artifacts including the closeout-authorization crosswalk.
- **Binding the artifact's PROSE into `inspection_identity`.** Round 1's blocker
  was a false `purpose` in the one region no identity covered; rewriting it moved
  no identity at all. Rewriting the prose fixes an instance; binding it fixes the
  class.
- **Not deciding `#561`.** The measurement reframed the question — the entire
  re-record tax is paid for a corpus COUNTER while every toll figure the deferral
  turns on is stable — but the choice stayed the owner's.
- **Not closing `#547`.** Its literal subject was deleted by slice 1 and its
  generalized form was WIDENED by it. Closing it would have been adopting work a
  Non-Goal declined. It went to the operator decision queue with the re-scope.

## North Star Alignment

The run is mostly a P5 story and it held. `#562` is a gate that *declared
completion* on a proxy it could not support — a whole-file digest standing in for
"the thing I relied on" — and had become the wolf-crier the diagnosis names, with
0 of 5 true positives training the reflex that defeats it. Retiring it while
keeping existence, containment, and set-binding is teeth narrowed to form and
irreversibility rather than teeth removed.

P4 held at the one irreversible boundary crossed. `#562`'s close used a DIFFERENT
channel from the one that produced the fix: the CLI exit code and rendered refusal,
verified as distinct by checking that no test in either freeze module reaches
`main()`, argparse, or `RefusalError` rendering. The state was read back through
the adapter rather than inferred from the close call's own success.

The facet this run kept re-learning is P4's own warning that **a distinct observer
re-reading the same proxy still rubber-stamps.** Three times a repair was pinned by
a test that read the same proxy the repair wrote, and only a mutant on a DIFFERENT
channel — deleting the wiring — exposed it. The failure signature is P4 applied to
code review but not to test adequacy.

One mis-application, self-inflicted and caught: the first justification for binding
the prose was frequency ("this artifact's prose changes almost never"), and the
commit asserting it edited that prose seven times. The surviving argument is
incidence, not frequency — a refusal that can never be incidental to the editor's
own work is not a wolf-crier however often it fires. P3: the principle, not the
tally, is what transfers.

## Trends vs Last Retro

The predecessor measured "eighteen blockers across ten delegated rounds, and NOT
ONE in a first diagnosis." This run: 32 findings across four rounds, and again
every blocker was in a REPAIR, not a first diagnosis. The rule is now measured
twice on independent work and should stop being re-derived.

Its "a repair inherits HALVES" theme recurred literally — the writer holding
weaker rules than the reader, `malformed_locator` guarding `path` but not `role`,
the prose pulled inside the identity while the structured `issue` claim beside it
stayed out. What is NEW this run is the wiring variant: not half a rule, but a
whole rule with no live caller-side proof.

## Expert Counterfactuals

**Engelbart, `system-improving-itself` (the briefed lens): treat H + LAM + T as one
unit, and design T alongside LAM.** This run improved the LAM (the freeze's rules,
the drift message, the fixture) and left the TOOLING for verifying its own repairs
hand-built each time. The mutation harness was re-authored inline three times, once
wrongly, in a repo that already owns `check_changed_line_mutation_coverage.py` and
a cosmic-ray config. Engelbart's move would have been to notice on slice 1 that
"mutate the repair, confirm the baseline reports a real test count" is the T-half of
this goal's own verification plan and to build it once, rather than to remember the
rule three times and get the shell wrong once. The plan named the rule; nothing
named the tool.

**Direct counterfactual: an adversary who owns the CI, not the diff.** Given only
"which of these repairs survives having its call site deleted," they would have
found all three unwired repairs in one pass at slice 1, without reading any
rationale. Every one of them was invisible to careful reading and visible to one
mechanical question. That question belongs in the verification plan as a step, not
as a lesson.

## Sibling Search

- axis: by-content | location: repo-wide grep for inline mutation sweeps in shell
  heredocs vs the owned `check_changed_line_mutation_coverage.py` /
  `cosmic-ray.toml` path | decision: valid follow-up outside the slice | proof: this
  run hand-authored three separate inline mutation harnesses, one of which reported
  nine false kills from an unquoted zsh variable, while the repo already owns
  mutation tooling that was never invoked | follow-up: issue — a repo-owned
  "mutate-and-verify-the-baseline" affordance so the harness is not re-authored per
  slice
- axis: by-entity | location: repairs whose only proof calls the repaired function
  directly rather than through its caller | decision: valid follow-up outside the
  slice | proof: three instances this run (`stamp_inspection`'s existence check,
  the residual exit-code assertion, the fixture re-stamp call), each surviving a
  wiring-deletion mutant until a source-level pin was added | follow-up: issue —
  make "delete the call site, not the body" an explicit step in the verification
  plan the goal template seeds

## Next Improvements

- workflow: add one line to the goal template's `## Agent Verification Plan` —
  **a mutation sweep states its baseline test COUNT before its first mutant**, and
  **at least one mutant per repair deletes the CALL SITE rather than the body**.
  Both are this run's measured misses and neither is currently written anywhere.
- capability: a repo-owned mutate-and-restore helper that refuses to report a kill
  unless the unmutated baseline first reported a passing test count. This is the
  Engelbart T-half; three hand-rolled harnesses in one run is the trigger.
- memory: the two-round rule for verdict-logic slices is now measured twice on
  independent goals (18/10 then 32/4, blockers always in repairs). It belongs in
  `recent-lessons.md` as settled rather than re-derived per goal.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md
