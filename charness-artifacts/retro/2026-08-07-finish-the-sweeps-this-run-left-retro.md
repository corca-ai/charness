# Session Retro
Date: 2026-08-07

Goal: [2026-08-07-finish-the-sweeps-this-run-left.md](../goals/2026-08-07-finish-the-sweeps-this-run-left.md)

## Context

One goal, three slices, three commits, three issues repaired (#494, #493, #492).
All three were residue the 2026-08-06 goal created, and two of the three were
DELIBERATE recorded deferrals rather than mistakes — the goal cashed in scheduled
work and only #494 was an actual miss. Each closeout says which it was.

## Evidence Summary

- 3 commits: `25a8e265` (#494), `86be2df5` (#493), `70e32238` (#492).
  (source: `git log --oneline`, 2026-08-07)
- **6 bounded review rounds** (2 per slice), every window verified `clean` by
  `reviewer_boundary_fingerprint.py`. Each verify ran before the parent's next
  write; the slice logs record the `clean` verdict but not the timing, so the
  ordering is stated as practice followed, not as something the artifacts prove.
- **16 BLOCKERS across 6 rounds — 6 on A, 3 on B, 7 on C.** An earlier draft said
  "5 on B", wrong twice over: it did not sum to 16, and it conflated two metrics.
  B raised 6 acted-on FINDINGS (1 blocker + 4 non-blocking in round 1, 2 blockers
  in round 2), which is the number its Slice Plan row carries. Blockers and
  acted-on findings are separate counts and are now labelled as such.
  (source: recounted from the six reviewer reports and the goal's `## Slice Log`)
- **Every round found something, 6 of 6. Every round that READ REPAIRS found
  something, 3 of 3** — only the three round-2s read repairs, so an earlier
  "6 of 6" overstated the evidence base for this repo's own two-round rule.
- **The broad suite caught 2 defects that the slice gate AND both review rounds
  passed** — slice B's mis-naming predicate, and slice C's gate wiring violating
  the scope-path invariant. (source: `pytest tests/` runs at 7060 / 7068 / 7083)
- Broad suite: 7060 → 7068 → 7083 passed, 0 failed, one full run per slice. The
  deltas reconcile: +8 is slice B's added tests; +15 is slice C's 14 plus the one
  late slice-B control added AFTER B's broad run, in response to the regression
  that run found. (source: three `pytest tests/ -q` runs, 2026-08-07; now written
  back into each slice log, which they were not when this retro was drafted)
- 3 issues filed off-goal: #495, #496, #497. (source: `gh issue create`)
- **1 dup-ratchet family**, classified `intentional` after verifying pre-existence
  by stashing and re-running the ratchet on the base tree, plus 1 ROTATION of that
  same family when a later edit shifted its span. An earlier draft counted the pre-
  and post-rotation ids of one family as two.
  (source: `charness-artifacts/quality/dup-review.json`, one 2026-08-07 entry)
- 0 gates weakened, 0 `--no-verify`, 0 floors loosened.
- New gate `check_standalone_imports.py`: **649 modules, 2.0s full sweep at 16
  workers**; scoped commit run 0.2s. (source: `time` on the check, 2026-08-07)

## Waste

- **A guard went to the wrong boundary FIVE times, across three surfaces.**
  Slice A attached shape checks to the TRANSPORT (`--fields-file`) when the
  property belonged to the VALUE, so the documented-safe argv channel walked past
  them. Slice B guarded a TYPE (`isinstance(x, dict)`) when `{}` is a dict, then
  an EQUALITY (`merged != default`) which mis-named a fully-specified block. Slice
  C's shape fallback was wrong TWICE in opposite directions: it broke on a cycle
  MARKER (too narrow), then unless the error was a wrong-shape SPELLING (too wide).
  That is 1 + 2 + 2 = five, not four; an earlier draft compressed C's two into one
  and then reported four — the same assert-without-counting class this section is
  about. Every one cost a review round or a broad run. The common shape: each cut asked about the form the failure happened to
  take rather than about what the guard was for.
- **A false-positive control varied the wrong axis.** Slice B's control used
  DEFAULT values, so `merged == default` masked the mis-naming bug; the broad suite
  found it. A control is only a control against the inputs it varies, and mine
  varied presence without varying value. (ONE measured instance — an earlier draft
  said "every" and "twice" and could name only this one.)
- **The enumeration in slice C was wrong three times** — repo-root shims imported
  by 135 scripts, then `support/`, then `shared/`. Each was found by an inversion
  test, none by listing. The first cut's completeness test named the families the
  pattern already matched, which cannot fail for a family nobody thought of.
- **A doc correction shipped FALSE.** Slice B's repair of a wrong claim about
  `mutation_testing` asserted a new wrong claim (that every blank sub-key errors;
  a blank nested BLOCK header does not). Caught by round 2. The repair was to pin
  it with a test, not to word it more carefully.
- **Slice A was committed with its broad run recorded as `pending`, and the number
  was never written back** until the closeout review caught it. This retro's own
  thesis is that the broad suite was the only observer that caught two real
  defects, so shipping a slice without recording one is the gap it argues against.
- **Slice 1's `Metrics:` field was left blank** while slices 2 and 3 each recorded
  an explicit "host log exposes no per-slice totals; not claimed". A blank field is
  not a recorded non-claim.
- Not waste, and worth separating: broad-suite wall time was 623.8s / 625.7s /
  623.4s across three runs (source: the `pytest` summary lines). It was the only
  observer that caught two real defects. It earned its cost twice.

## Critical Decisions

- **Filing #496 rather than fixing it.** The slice B recursion newly reports
  hollow refills for inert empty-string defaults. The fix has a real scope
  question (suppress at top level too? is "empty default" the right predicate? or
  is the bug in the warning's remedy text?) that a slice scoped to something else
  should not settle by fiat. The reviewer independently agreed, and added the
  sharper framing: the symptom is that the warning advises a destructive edit.
- **Reconstructing the pre-fix cycle rather than skipping the acceptance.** #492's
  acceptance required the check to FAIL on the real defect, but the pre-fix module
  was never committed — it was found and fixed inside the same commit. Rather than
  weaken the acceptance to "passes on a clean tree", the test reconstructs the
  defect and FIRST proves the reconstruction emits the issue's exact error text.
  That reconstruction is what caught the gate's own masking bug.
- **Blocking, not advisory, for the new gate** — recorded as a Floor-Addition
  Restraint call at the site. The decisive point: an advisory is read by whoever
  is looking, and the defining property of this class is that nobody can see it, a
  passing 4979-test suite included.
- **Stating four blind spots rather than papering over them.** A swallowed cycle
  (`try: ... except ImportError: A = None`) is genuinely undecidable from outside
  the process. Recorded in the docstring with the reason, plus the new
  third-party-dependency precondition that making "imports in no shape" blocking
  imposes. (The docstring said "three" while listing four; corrected on the shipped
  surface at closeout, after the claims review caught it.)

## Improvements

- **A false-positive control must vary the axis the predicate reads.** Slice B's
  control passed because it held constant the exact value the buggy predicate keyed
  on. One instance, but the failure mode is general.
- **Prefer an inversion test to a family pin for any completeness claim.** Three
  missed families in one slice, all found by inverting, none by enumerating.
- **When a fix is a guard, name the invariant before writing the predicate.** Five
  wrong boundaries this run, each cheap to have avoided by asking "what is this
  guard FOR" instead of "what did the failure look like".

## Sibling Search

- The guard-at-the-wrong-boundary class recurred 5× in one goal across 3
  independent surfaces, which is a transferable waste item, not a local slip. Its
  structural destination is classified in the goal's `## Auto-Retro`.

## North Star Alignment

Consulted [design-north-star.md](../../docs/design-north-star.md).

**Held.** P4 governed the whole run and earned it three times. "Success is provisional
at an irreversible boundary; confirm with a different observer AND a different evidence
channel" is exactly why the three issue closes waited on a remote CI read rather than
resting on the local pytest that produced the fixes — the delegated resolution critique
made that a pre-close condition, independently. The same facet is what made slice C's
acceptance non-negotiable: a guard that passes on a clean tree has established nothing,
so the check had to fail on the reconstructed cycle before it could ship.

**Also held: teeth only where a wrong answer escapes.** The new gate is BLOCKING, and
the Floor-Addition Restraint call is recorded with a measured recurrence rather than a
reflex — an advisory is read by whoever is looking, and this class is invisible to a
passing 4979-test suite. By contrast #496 was FILED rather than gated, because its
remedy is a judgment call and a gate that guesses cries wolf.

**Mis-applied, and the run's real failure signature.** "Brief a capable judge" was
applied to the CODE and not to the GUARDS. Five times a predicate was written against
the shape of the observed failure instead of against the invariant — which is the
harness equivalent of a gate that measures the reproduction rather than the property.
Twice the wrong predicate was the REPAIR of a previous wrong predicate. That is
tracked as #499, and the honest reading is that the north star's own standard was not
applied to the surfaces this goal was building.

**A second signature: a verdict surface that did not state what it measured.** The
closeout artifacts carried eight false or unsupported figures until a delegated
reviewer read them — on a run whose three slices were all about making a verdict
state its scope. The gate this run shipped prints `PARTIAL: checked N of M` with
every verdict; the retro that describes it asserted counts it had not recounted.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md
