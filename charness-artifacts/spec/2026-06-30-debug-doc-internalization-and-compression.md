# Debug skill: internalize method into structure + compress reference docs

Status: draft scope for NEXT session (operator-committed 2026-06-30). Not started.
Owner intent: bae.hwidong@corca.ai — "do this next session; also aggressively
compress/delete reference docs, there are too many files."

## Why (evidence from the 2026-06-30 debug re-capture)

The re-capture (`charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/`)
graded `pass_rate 0.8` on the SUBSTANCE outcome set, and the pass/fail split fell
exactly on one boundary:

- Sections whose scaffold seed carries a RICH method hint AND/OR a validator check
  (`## Detection Gap` seed `surface | what did not fire | smallest change`,
  `## Sibling Search` seed + the cross-file/decision/follow-up validator,
  `## Candidate Causes` ≥3) → the run produced PASS-quality content **without
  opening the reference doc**. The load-bearing rule is already internalized.
- Sections whose scaffold seed is a bare `TODO` with NO validator check
  (`## Reproduction`, `## Hypothesis`, `## Verification`) → the run filled them
  shallowly (`static scan only`, non-falsifiable). The one substance FAIL
  (`falsifiable-hypothesis-before-fix`) lands here.

That FAIL maps exactly to the two `five-steps.md` method rules NOT internalized:
"build the smallest honest reproduction" (step 3) and "verify a FALSIFIABLE
hypothesis; don't call intuition a diagnosis" (step 5). Conclusion: **doc-opening
is a weak proxy because a good scaffold internalizes the doc; the run follows
scaffold hints but skips docs. So move load-bearing rules INTO the structure, keep
docs as on-demand depth, and verify via the substance assertion — not doc-opening.**

## Plan A — internalize the missing method (the real fix)

- Give `## Reproduction` and `## Hypothesis`/`## Verification` rich scaffold seeds
  the way Detection Gap/Sibling Search have them, e.g.
  `## Reproduction → smallest reproduction, or 'n/a — could not reproduce: <why>'`
  and `## Hypothesis → falsifiable claim | disconfirmer: <cheapest refutation tried>`.
- Add an honesty-MARKER validator check (presence of the repro/disconfirmer marker),
  modeled on `validate_cross_file_sibling_marker` — an honesty contract surfaced for
  fresh-eye review, NOT an anti-gaming hard gate (the run escaped the bare section
  with "static scan only"; a hard gate would just collect `n/a`).
- Keep the `falsifiable-hypothesis-before-fix` outcome assertion as the real bar.
- Sync plugin mirror; extend `tests/test_debug_artifact.py`.

## Plan B — compress/delete reference docs (operator wants fewer files)

11 docs, 633 lines today. Assess EACH against one criterion: *is the load-bearing
rule already carried by the scaffold seed + validator (or another skill's
reference)?* If yes → compress to a pointer or delete; if it carries unique depth a
competent run still needs → keep but slim. Do the per-doc verdict in the next
session (this is review-then-act, not a pre-decided cut). Starting hypotheses:

- `sibling-search.md` (156) — heaviest; large parts restate validator-enforced
  rules (4-decision taxonomy, cross-file marker, follow-up identifiers). Strong
  COMPRESS candidate: keep the four-axis + mental-model abstraction depth, cut the
  rule-restatement the validator already owns.
- `detection-gap.md` (53) — rule is in the scaffold seed; COMPRESS to the shapes +
  over-reach check.
- `five-whys-causal-chain.md` (42) — already re-pinned OUT of the floor (one of 3
  causal lenses). Merge/slim with `disconfirmer-first.md`?
- `disconfirmer-first.md` (53) — RELEVANT to Plan A (the falsifiable method); fold
  its core into the Hypothesis seed, keep the rest as depth.
- `five-steps.md` (29) / `debug-memory.md` (17) — the floor. Slim once their rules
  are internalized (five-steps' repro/falsifiable → Plan A; debug-memory's format
  is already validator-enforced, but its "read near-matches before starting over"
  CONSUME-prior behavior is NOT internalized and the run skipped it — separate).
- `adapter-contract.md` (88), `invariant-first-review.md` (78),
  `named-target-verification.md` (75), `document-seams.md` (29),
  `anti-patterns.md` (13) — on-demand; assess for overlap/merge.

## Plan C — reconsider the floor

Once a rule is internalized (Plan A) and substance-asserted, requiring its doc to
be OPENED (`requiredCommandFragments`) tests the wrong thing. Candidate: retire
`five-steps.md` from the floor and let the substance assertion be the bar. NOT yet
— see caveats.

## Caveats

- n=1: one re-capture. Confirm the "scaffold elicits substance" pattern on 1-2 more
  captures before retiring any floor doc.
- `debug-memory.md` consume-prior-memory behavior is a SEPARATE gap (run skipped
  prior-incident reads too); structural enforcement is harder — planner emphasis,
  not a scaffold seed. Do not conflate with Plan A.
- Gaming risk: honesty marker + substance judge, never a hard mechanical gate.

## Acceptance

- Reproduction/Hypothesis carry method seeds + a marker check; a re-capture's
  `falsifiable-hypothesis` assertion can PASS for a run that actually reproduces/
  disconfirms (and still FAIL a static-only run).
- Debug reference doc count/line total meaningfully reduced, each cut justified by
  "rule already in scaffold/validator" — no load-bearing rule lost (validator +
  substance assertion still green).
- Source: this session's analysis + the re-capture finding
  (`charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/finding.md`).
