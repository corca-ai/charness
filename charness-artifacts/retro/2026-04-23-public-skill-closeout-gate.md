# Public Skill Closeout Gate

## Context

Unit of work: make the #62 Cautilus planning miss hard to repeat. The slice
changed `run_slice_closeout.py` and `plan_cautilus_proof.py` so public-skill
validation follow-ups cannot be silently buried when Cautilus regression proof
itself is not required.

## Evidence Summary

- User correction: #62 had pytest and slice closeout, but not explicit Cautilus
  dogfood/scenario review until challenged.
- Premortem angle review found two real blockers: `hitl-recommended` public
  skill changes could still pass, and invalid public-skill policy failed open.
- Counterweight review kept enforcement in `run_slice_closeout.py` instead of
  overloading the Cautilus planner as the blocking UI.
- `python3 scripts/run_slice_closeout.py --repo-root .` passed after the fix.

## Waste

The first fix only blocked `scenario_registry_review_required`, which protected
`evaluator-required` skills like `init-repo` but not other public-skill review
recommendations. That would have recreated the same "recommendation existed but
was not a stop gate" failure shape.

## Critical Decisions

- Block closeout whenever `skill_validation_recommendations` is non-empty
  unless `--ack-cautilus-skill-review` is passed.
- Fail closed when public-skill validation policy cannot be loaded or validated
  during Cautilus proof planning.
- Defer policy-only and dogfood-only slices as a separate decision; this slice
  protects public skill package changes.

## Expert Counterfactuals

- A workflow engineer would have made the closeout wrapper enforce visible
  recommendations, not just binary Cautilus proof requirements.
- A test maintainer would have added negative tests for `hitl-recommended` and
  invalid-policy branches before trusting the new evaluator-required test.

## Next Improvements

- `workflow`: after public-skill package edits, run slice closeout and expect
  explicit Cautilus skill-review acknowledgement before final verification.
- `capability`: consider a follow-up gate for policy-only or dogfood-only
  public-skill validation changes if those slices keep recurring.

## Persisted

yes
