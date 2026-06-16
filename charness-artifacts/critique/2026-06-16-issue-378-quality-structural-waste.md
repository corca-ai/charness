# Critique: #378 quality structural waste advisory

Status: complete
Fresh-Eye Satisfaction: parent-delegated
Target: code critique
Issue: #378

## Reviewer Tier Evidence

- requested tier: default
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: spawn tool accepted reviewer agent ids
  `019ecdf5-823f-7a41-ac8d-c5b54e9dadd0`,
  `019ecdf5-97bb-7ea3-acf9-5d0373004a47`,
  `019ecdf5-ae23-7210-bec7-009317f6d74c`, and
  `019ecdf9-491f-7460-bbda-90eeae9a7559`; reviewer-tier application details
  are host-hidden.

## Change

Add a `quality` advisory inventory for two slow-gate waste patterns:
duplicate broad pytest discovery/collection and broad AST source scanners that
lack a visible cheap prefilter.

Out of scope: blocking gates, measured runtime attribution, full dataflow
analysis, or GitHub issue closeout.

## Angles

- False-positive/noise and advisory-honesty risk.
- Integration, packaging, mirror, and validator coverage risk.
- Issue acceptance fit and operator next-action usefulness.
- Counterweight pass after fixes.

## Act Before Ship

- Duplicate pytest collection was initially overclaimed as duplicate proof even
  when no canonical runner was visible. Fixed by splitting
  `pytest_collect_only_duplicate` from
  `pytest_collect_only_broad_collection`, downgrading the aggregate finding to
  `broad_collection_review` when no canonical runner/target-list owner is
  visible, and adding a no-canonical regression test.
- The new 4-field `INTERPRETATION` declaration was not registered in
  `.agents/inference-interpretation-surfaces.json`. Fixed by registering the
  `structural-waste` inference surface and updating the live registry test.
- New public/plugin scripts and focused tests must be staged with the commit.

## Bundle Anyway

- The broad-scanner prefilter heuristic is intentionally token based. Keep it
  advisory and improve only after real artifact samples show noise or misses.
- The live registry test now asserts the `structural-waste` surface id directly.

## Over-Worry

- Not covering every parser or language is acceptable for the first slice; #378
  asks for cheap command/script/token evidence.
- The current repo's live output is a single broad-scanner advisory candidate,
  and the recommendation explicitly allows recording why full parsing is the
  correctness boundary.

## Valid But Defer

- Broader discovery roots beyond `scripts`, `skills/public`, and
  `skills/support` can wait for downstream samples.
- Runtime correlation can be added later; this slice gives operator-visible
  structural next actions without claiming wall-clock proof.

## Proof

- `python3 scripts/validate_cautilus_proof.py --repo-root .` -> pass; closeout
  reported `next_action: none` for live Cautilus execution and kept the
  reviewed dogfood case as the explicit `quality` scenario review.
- `python3 -m pytest -q tests/quality_gates/test_structural_waste_inventory.py
  tests/quality_gates/test_inference_interpretation_meta_validator.py
  tests/quality_gates/test_quality_skill_docs.py
  tests/quality_gates/test_inventory_consumption.py` -> 56 passed.
- `python3 scripts/validate_inference_interpretation.py --repo-root .
  --require-git-file-listing` -> 10 inference-layer surfaces valid.
- `ruff check skills/public/quality/scripts/structural_waste_lib.py
  skills/public/quality/scripts/inventory_structural_waste.py
  tests/quality_gates/test_structural_waste_inventory.py
  tests/quality_gates/test_inference_interpretation_meta_validator.py` -> pass.

## Non-Claims

- This critique does not close #378.
- The inventory is advisory and does not prove runtime savings.
- The broad-scanner heuristic is not a full dataflow analyzer.
