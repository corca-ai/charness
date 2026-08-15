# S6b-2 cost as a proof surface

Date: 2026-08-16

## Context

S6b-2 of the 6.0.0 release scope: make a dominated command refusable at the
seams a document never reaches (SC14, SC15, SC16, SC17, SC19), plus S6b-1's
carried sampler remainder. Built and committed as one amended commit.

Round 1 closed after this retro was first written and is folded in below: three
bounded reviewers, six blockers, nine majors, all repaired. What matters next is
NOT this slice: round 2 is owed because the slice changes verdict logic on proof
surfaces, the classification ledger still does not exist, and S7 has not started.
The release is not cuttable.

## Window

`0037dbcfd..bb55b5e03` — one slice, one commit, amended four times so the
changed-line proof landed inside it rather than in follow-up commits.

## Evidence Summary

- Standing suite, four runs, final green: 9605 passed in 80.7s
  (`python3 scripts/run_standing_pytest.py --repo-root .`).
- `ruff check --no-cache .` clean. Cached `ruff check .` was never trusted, per
  the contract's Constraints.
- Changed-line mutation coverage, re-counted from the four saved reports rather
  than recalled: run 1 `ok: false`, 7 blocking files, 65 uncovered changed
  lines; run 2 → 2 files, 2 lines; run 3 → 1 file, 1 line; run 4 `ok: true`,
  `blocking: []`. Command in the S6b-2 contract entry.
- Duplicate ratchet: hard-block on new code families, resolved by one real fix
  (three copies of a skill-script resolver collapsed into
  `runtime_bootstrap.skill_script`) plus seven families classified `intentional`
  with reasons in [dup-review](../quality/dup-review.json).
- Ten repo gates run individually to exit 0, including the two new ones:
  `check_command_dominance.py`, `check_runtime_budget_universe.py`.
- Gate timing measured three times before it was written into the timing table:
  0.10s, 0.08s, 0.07s.

## Waste

- **Three repo completeness guards fired only at full-suite time**, not when the
  surface they guard was added: a queued gate needs a seeded harness stub, a
  timing-layer verdict, and a catalog entry for a new reference. Each cost a
  full suite run (~85s) to discover. They are exactly the right guards; the
  waste is that nothing prompts them at the moment of the edit.
- **`ruff` C901 complexity surfaced after the code was written**, forcing a
  decomposition pass on two functions. The decomposition was an improvement, so
  this is cheap waste, not pure loss.
- **A commit message with backticks was evaluated by the shell**, silently
  dropping a clause. Caught by reading the stored message back — a different
  channel than the one that wrote it, which is the only reason it was caught.
- **Near-miss, not waste, recorded because it nearly was**: the retro planner's
  default `next_action` was `continue-existing-retro` pointing at
  `2026-08-16-session-retro.md`, with the scaffold packet declaring
  `write_artifact_effect: overwrite_existing_content`. That artifact belongs to
  the PREVIOUS session (committed in `0037dbcfd`) and merely shares today's
  date. Passing `--title` routed the scaffold to a new path and the prior record
  survived. This is the producer-scaffold class S2 of this very release
  exists to fix, arriving through the planner's default rather than the
  scaffold's write path.

## Critical Decisions

- **The blind class was written before the detector**, as the carried lesson
  asks, and the first acceptance test is the wrong-noun test. It earned its
  place immediately: the registry's replacement is
  `python3 scripts/run_standing_pytest.py`, whose own path contains `pytest`, so
  a substring reader reports the fix as the defect.
- **The exemption is keyed to a SITE and requires a reason, and an exempt site
  stays in the report.** Declaration must not equal silence; both directions are
  pinned by tests, because declaration-satisfies-the-criterion is precisely how
  S6c's dependency arm was falsified one slice earlier.
- **`cosmic-ray.toml`'s literal was exempted, not converted.** Substituting the
  standing runner there is plausibly faster and is unmeasured under cosmic-ray;
  converting a mutation pipeline on an unmeasured assumption is the regression
  shape S6 recorded. The reason is written at the site.
- **The changed-line proof ran before the commit was final**, via amend rather
  than follow-up commits. The previous session paid two extra commits to learn
  this ordering.
- **The registry is a denylist that measures nothing**, and says so. It records
  authored claims; `measured:` is evidence a human collected and nothing
  re-runs it.

## Trends vs Last Retro

The previous durable retro
([2026-08-16-session-retro.md](./2026-08-16-session-retro.md)) is titled around
one finding: reviewers found every blocker and the implementer found none.

This session moved on that, and the move is attributable to a mechanism rather
than to effort. Four defects in the slice's own work were found by its OWN tests
and gates before any reviewer read a line: a library resolved from the analysed
tree instead of the tool's own (three instances, the third caught by a test
written for the second); a duplicated config reader that matched a whole
assignment line and reported clean over a dominated literal; a coerced list
field that turned inline YAML into a string and matched nothing; and a module
re-exec'd per call so `except RegistryError` never caught its own error.

That hedge was right, and round 1 settled it AGAINST the flattering reading.
Three reviewers returned six blockers and nine majors. Two are decisive:

- **SC15's new direction computed a different predicate than the sentence it
  printed** — a "label" scraped from the tail of a site string, compared against
  the runner universe instead of the budgeted set, under an advisory claiming "no
  bar can ever fail on them". Two reviewers reached it independently.
- **`mutation_manifest_lib` published a command that never ran** into a CI
  artifact and into auto-filed issue bodies.

So the honest trend is narrower still: **the tests moved earlier in the loop and
did not replace review.** My suite was green over a gate whose central claim was
false, and over a durable record naming the wrong command. Every test I wrote for
the surfaces reviewers found was green on the defect — two of them pinned the
defect as intended semantics. Review remains the only thing that has ever found
this class here, for the fourth slice running.

## North Star Alignment

**P4 held, at the code layer, and it is the session's clearest result.** The
standing suite was green over 65 changed lines that no test executed. The
changed-line proof is a genuinely DIFFERENT evidence channel — mutation-line
coverage rather than pass/fail — and it found them. Not a different observer
re-reading the same proxy, which the north star records as the shape that
rubber-stamps.

The most valuable of those 65 was structural, not incidental: the exported
inventory's entire scan loop had never executed, because every SC19 acceptance
test drove it with a registry-less tmp repo. A criterion asserting a consumer
"can answer" the cost question was resting on dead code while the suite and two
gates were green.

**P5 held by construction.** The new gate forces a question and does not declare
completion: `did_not_judge` states on every run that a green means "no
registered shape at the listed sites", never "no dominated command here", and
that an exempt site is still a dominated command.

**P4 on PROSE was routed to a different observer, and the observer found the
failure I could not.** The operator's carried lesson was that P4 was applied
rigorously to code and not at all to what was written about the code. Routing it
to a briefed reviewer rather than self-checking was correct, and it returned:
five surfaces carried "13 of 14 discovered snippets are wrapped", labelled
*Measured*, never counted. Running the discovery gives 8 wrapped and 6 unwrapped.
The reviewer counted the tree by hand.

And the correction repeated the class: the round-1 repair fixed four of the five,
then wrote "Corrected everywhere" into the contract. Both round-2 reviewers found
the survivor independently — still labelled *Measured*, on the acceptance surface
of the mechanism it justified. The lesson is therefore NOT "re-measure", which
was done. It is that **a correction claiming completeness needs the same proof as
the original claim**, and the only proof that holds is the assertion.

That is the operator's lesson walked into inside the session it was given, on the
one class the session was warned about. The repair that holds is not the
corrected number — it is
`test_the_wrapped_snippet_ratio_this_repo_documents_is_the_measured_one`, which
makes the next drift a red test instead of a stale sentence. The generalisable
form: a quantity in prose about a file still being edited needs an assertion, not
a re-read.

Also found on the prose surface, and the same class: a `# pragma: no cover`
naming a test that never referenced the file — verbatim the defect three
reviewers caught in the sibling guard one slice earlier, shipped again by the
slice that cites the repair.

## Expert Counterfactuals

**Engelbart (system-improving-itself) — treat H + LAM + T as one unit.** Round 1
sharpened this lens rather than softening it: writing the blind class first DID
change the action and the paragraph STILL shipped missing its whole
false-POSITIVE direction, which a reviewer supplied. Habit produced a partial
artifact; only a gate would have asked "is this list complete in both
directions?". The
lesson "state the blind class before writing the detector" was carried this
session by author habit plus a docstring paragraph. That is LAM without T, and
it is the same "correct rule, no carrier" shape the last two retros named and
nothing built. What Engelbart's lens changes: the T already exists in this repo
and I found it mid-slice by accident, not by design —
`validate_inference_interpretation.py` plus
`.agents/inference-interpretation-surfaces.json` enforce a four-field
declaration whose load-bearing field is `blind_spots`, and a leak scan refuses
an unregistered declaration. I registered the exported inventory there. I did
NOT register the library or the gate, whose blind classes live in prose
docstrings that nothing enforces and a later edit can silently delete. The
counterfactual move is to have asked "what surface already gates this class of
claim?" before writing the paragraph, and to extend that registry to modules
that render a verdict — which converts the habit into a gate for every future
detector, not just this one.

**Pre-mortem (Klein) on the registry, six months out — divergent second lens.**
Assume the registry is stale and wrong and nobody noticed. What happened: every
entry is an authored claim with a free-text `measured:` field, nothing
re-measures, and the mechanism has no way to notice its own rot. A replacement
that got slower, or was renamed, produces a refusal pointing at a command that
no longer helps — and the refusal still reads authoritative. The cheap T is a
dated `measured_at` plus a staleness advisory on the gate's own output; the
expensive one is re-measuring, which the blind class explicitly declines to do.
This is a real residual, not a hypothetical, and it is stated here rather than
in the registry where it would read as covered.

## Sibling Search

- abstraction-up: helper resolved from the ANALYSED tree rather than the tool's own tree | decision: fixed in slice | proof: three instances found in this slice (`scripts/check_command_dominance.py`, `scripts/validate_handoff_artifact.py`, `scripts/check_runtime_budget_universe.py`), all collapsed onto `runtime_bootstrap.skill_script`; the third was caught by an acceptance test written for the second
- same-shape scan across repo scripts: `repo_root / "skills" / ...` resolution in sibling gates | decision: valid follow-up outside the slice | proof: grep over `scripts/*.py` and `skills/public/*/scripts/*.py` returns further sites including `scripts/build_debug_seam_risk_index.py:29-30`, `scripts/build_retro_lesson_selection_index.py:23-24`, and `scripts/check_seed_fixture_budget.py:25-26`; each resolves a skill script from the passed root, which is correct where the tool only ever runs on its own repo and wrong the moment it is pointed elsewhere, and distinguishing those two cases is per-site judgment rather than a sweep | follow-up: deferred s6b-2-sibling-tree-resolution
- carrier axis: a detector's blind class carried by docstring prose rather than by a gated declaration | decision: valid follow-up outside the slice | proof: `.agents/inference-interpretation-surfaces.json` registers `command-dominance-inventory` but not `command_dominance_lib.py` or `check_command_dominance.py`, whose blind classes are unenforced prose; the registry's `leak_scan` only refuses an unregistered DECLARATION, so a module with no declaration at all is invisible to it | follow-up: deferred s6b-2-blind-class-carrier

## Next Improvements

- workflow: after adding a queued gate or a new skill reference, run the repo's
  declaration guards immediately (`test_quality_run_planner.py`,
  `test_quality_runner.py`, `test_timing_layer_completeness.py`,
  `test_closeout_bundle.py`, `validate_surfaces.py`) before the first full
  suite. Measured this session: they fired at full-suite time and cost two
  otherwise-unnecessary suite runs.
- capability: extend the inference-interpretation registry's requirement from
  "a module that DECLARES an interpretation must be registered" to "a module
  that renders a verdict about other code must declare its blind class", so the
  blind-class habit becomes a gate. This is the carrier two retros have asked
  for and nothing has built; it is now cheap because the registry, the
  validator, and the leak scan all exist.
- memory: the retro planner's default `next_action` can point at another
  session's record that merely shares today's date, with the scaffold packet
  declaring `overwrite_existing_content`. Always pass `--title`. Recorded in
  `## Waste` above with the commit that owns the endangered artifact.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":2,"session_id":"2026-08-16-s6b-2","status":"effect-recorded"}

Both events are `changed-an-action`, both cite the action they changed, and both
are recorded with their limit rather than as clean wins. `detector-blind-class-unstated`
changed the authoring order and the first acceptance test — and round-1 reviewers
still found a SIXTH blind class the paragraph missed, the false-positive
direction, so the lesson moved the action without making the result complete.
`changed-line-proof-before-broad-quality` changed the commit ordering and paid
for itself on the first run.

The eight other presented lessons were read and did not bear on this slice; no
score is appended for them, because a sparse honest ledger is the contract.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-16-s6b-2-cost-as-a-proof-surface.md
