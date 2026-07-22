# Critique Review
Date: 2026-07-23

## Decision Under Review

Resolve #451 (mutation score regression, 79.2% < 80% threshold, 25 survived
mutants in `build_payload`/`render_markdown`/`build_parser`/`_split_values` in
`skills/public/quality/scripts/recommend_behavior_test.py` and `build_items`/
`main` split across that file and
`skills/public/announcement/scripts/init_adapter.py`) by adding test-only
assertions to `tests/quality_gates/test_quality_behavior_recommendation.py`
and `tests/test_announcement_adapter_lib.py`. No production code changed.

## Failure Angles

- Michael Jackson (problem framing): does each new assertion actually
  constrain the named survived-mutant branch, or does it pad coverage with
  adjacent, non-constraining checks?
- Gerald Weinberg (diagnostic): is "missing assertions" the true root cause,
  or does a structural/pipeline cause mean this recurs regardless of this fix?
- Atul Gawande (checklist/operational): any silent-failure/tautological new
  test, and is the interning-defeating `subprocess.run` conversion reasoning
  actually sound?

## Counterweight Pass

- Act Before Ship: none.
- Bundle Anyway: broaden `test_init_adapter_scaffolds_public_body_shape` to
  assert more of `build_items`'s ~14 literal fields (weak evidence — the
  scoped mutation re-run already shows 0 survivors without it); left
  undone, see Deliberately Not Doing.
- Over-Worry: "test-writing theater" concern — rejected; every new
  assertion maps to a genuine, user-observable branch (weak evidence
  supporting the concern, so it does not survive).
- Valid but Defer: (1) the scheduled mutation-score CI gate re-samples a
  different file pool every run (`MUTATION_SAMPLE_SEED` keyed on
  `run_id`), so an undertested branch elsewhere in the sampler pool can
  trip the gate again — this is the exact #251 → #260 → #451 recurrence,
  already recorded as **intentionally unowned** for local/pre-merge
  prevention in
  `charness-artifacts/goals/2026-05-31-260-mutation-test-regression-on-main.md:326-337`;
  (2) the broader "assemble literal tuple/dict → render → emit" idiom
  recurs across ~20 sibling `skills/**/scripts/init_adapter.py` scripts
  (per `tests/test_adapter_shim_inprocess_coverage.py:31,55`) with the same
  thin-assertion shape, a follow-up sibling sweep, not this slice's scope;
  (3) a speculative, unverified sibling blind spot at
  `scripts/announcement_adapter_lib.py:125` (`elif kind == "path":`,
  exercised in-process by
  `tests/test_announcement_adapter_lib.py:188-191` with an identifier-safe
  literal) — not part of the reported #451 survivor set, not run through
  Cosmic Ray, so recorded as a valid-but-unconfirmed follow-up rather than
  acted on now.

## Structured Findings

- F1 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals/2026-05-31-260-mutation-test-regression-on-main.md:326-337 | action: document | note: scheduled mutation-score gate resamples a different file pool every run; local/pre-merge prevention is deliberately unowned, so a future recurrence in an unrelated file is expected, not a defect in this fix
- F2 | bin: valid-but-defer | evidence: moderate | ref: skills/public/announcement/scripts/init_adapter.py:29-46 | action: defer | note: ~20 sibling init_adapter.py scaffolds share the same thin-assertion "build items -> emit" idiom; broader sibling sweep is out of this slice
- F3 | bin: valid-but-defer | evidence: weak | ref: scripts/announcement_adapter_lib.py:125 | action: document | note: unverified in-process `==` comparison on an identifier-safe literal in a pre-existing, unrelated test; not part of #451's reported survivors, not confirmed via Cosmic Ray
- F4 | bin: over-worry | evidence: weak | ref: tests/quality_gates/test_quality_behavior_recommendation.py | action: defer | note: "test-writing theater" concern raised by counterweight; rejected — every new assertion maps to a real, previously-unchecked branch
- F5 | bin: bundle-anyway | evidence: weak | ref: tests/test_announcement_adapter_lib.py:88-105 | action: defer | note: `build_items` test asserts only 2 of ~14 literal fields; cheap to broaden but unnecessary since the scoped mutation re-run already shows 0 survivors

## Reviewer Tier Evidence

- Requested tier: high-leverage (angles) / high-leverage (counterweight).
- Requested spawn fields: session-model inheritance (Claude Code host; per
  repo's per-host subagent contract, Codex-only override fields
  `model=gpt-5.6-terra`/`reasoning_effort=medium` do not apply on this
  host).
- Host exposure state: host-defaulted
- Application state: host-confirmed: bounded-reviewer subagent spawned via
  the Agent tool with Read/Grep/Glob-only envelope for all four reviewers.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; reviewers were pointed at the
live git diff and source tree directly).

## Boundary Ownership

- Producer: n/a — test-only diff, no shared/generic/cross-surface
  production code touched (Weinberg angle explicitly scoped this
  `n/a`).
- Consumer: n/a.
- Owning surface: n/a.
- Verdict: single-surface

## Deliberately Not Doing

- Not broadening `build_items`'s test to assert every literal field (F5) —
  the scoped local mutation re-run (see below) already shows 0 survivors
  for this file without it.
- Not fixing or filing an issue for the `scripts/announcement_adapter_lib.py:125`
  possible blind spot (F3) — unverified against the actual mutation tool
  and outside #451's reported scope; a future mutation-score regression
  naming it would be the real trigger.
- Not designing an "owned" local/pre-merge mutation-score prevention track
  (F1) — the prior #260 goal artifact already decided this is out of scope
  for that slice; re-litigating it is out of scope here too.

## Verification Evidence

A scoped local Cosmic Ray session limited to exactly the two touched source
files (`skills/public/quality/scripts/recommend_behavior_test.py`,
`skills/public/announcement/scripts/init_adapter.py`), test-command narrowed
to the two touched test files, with the repo's own
`scripts/filter_cosmic_ray_mutants.py` applied: 0 surviving mutants out of 70
executed (18 filtered as trivial `__main__`-guard / `sys.path.insert` index
mutants, matching the repo's existing filter policy for those classes).
