# Quality Review
Date: 2026-06-27

## Scope

Target boundary: `create-cli` public skill, reviewed as the pilot target for the
capability-first / generative-sequence quality-move contract.

Ambient repo findings: interrupted v0.56.7 release WIP remains dirty and is a
non-claim for this target-skill pilot.

## Current Gates

- `plan_quality_run.py --target-skill create-cli --json` resolves
  [create-cli SKILL](../../skills/public/create-cli/SKILL.md) and emits a
  capability-centered structural packet.
- `inventory_skill_ergonomics.py` with the create-cli skill path reports
  `zero_heuristic_findings`; prose review remains required.
- `suggest_public_skill_dogfood.py --skill-id create-cli --json` provides one
  consumer prompt for routing and review, not an automatic pass.

## Runtime Signals

- runtime source: timing capture is missing for this dated pilot artifact; no
  runtime numbers are claimed.
- runtime hot spots: none claimed.
- coverage gate: focused quality tests passed for the contract migration before
  this artifact was written.
- evaluator depth: deterministic-gates-only; no Cautilus run because this is a
  local target-skill quality pilot.

## Healthy

- `create-cli` already centers operator contract, command-surface shape,
  lifecycle mutation rules, structured output, and distribution contract before
  implementation details.
- The skill ergonomics summary found no heuristic pressure across core length,
  mode/option pressure, prose ritual, path ambiguity, host-surface references,
  or reference discoverability.

## Weak

- Before this pilot, `create-cli` step 6 said "Add the right gates" after the
  already-good operator-contract and command-surface sequence. That was
  legitimate for CLI delivery boundaries, but under the new quality-move lens it
  could be over-read as gate-first advice unless the capability and proof
  boundary were named first.

## Missing

- Missing consumer-side pilot proof: the dogfood suggestion names the right
  first prompt, but no fresh reviewer has yet judged whether the new move-card
  vocabulary improves `create-cli` use.

## Deferred

- Defer `create-skill`, `ideation`, and `spec` hooks until this pilot receives a
  critique result. The vocabulary is not ready for broad rollout from this
  artifact alone.

## Advisory

- structural review result: use the shared generative-sequence lens because the
  weak spot is sequencing-shaped: `create-cli` should choose the command-surface
  capability and proof boundary before talking about gate families.
- prose review result: no heuristic findings from `inventory_skill_ergonomics`,
  but the phrase "Add the right gates" should stay tied to CLI delivery proof,
  not become a generic quality outcome.
- packet answer: capability_needed=`create-cli` users choose repo-owned command
  surfaces from operator intent before gate families;
  sequencing_applicability=order matters because gate selection depends on the
  operator contract, command surface, mutation rules, and distribution contract;
  current_centers=operator contract, intent-first grammar, lifecycle mutation
  rules, and quality-gates reference; next_center=proof seam before gate family;
  transformation=changed step 6 to "Add the right gates from the command
  capability seam already named above"; proof_boundary=focused tests plus
  reviewer judgment that the hook changes the `create-cli` decision surface;
  enforcement_posture=advisory.

## Delegated Review

- Delegated Review: not_applicable — this pilot records the first target-skill
  move card; fresh-eye critique is planned before hooks spread to adjacent
  skills.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable for this local skill-surface pilot.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill create-cli --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/create-cli/SKILL.md --summary`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-cli --json`
- `python3 -m pytest -q tests/test_quality_scaffold.py tests/test_quality_artifact_report_all.py tests/test_quality_artifact.py tests/quality_gates/test_quality_run_planner.py tests/quality_gates/test_quality_handoff_inventory.py tests/quality_gates/test_quality_skill_docs.py`
- `python3 -m ruff check scripts/validate_quality_artifact.py scripts/inventory_quality_handoff.py scripts/validate_quality_closeout_contract.py skills/public/quality/scripts/scaffold_quality_artifact.py skills/public/quality/scripts/plan_quality_run.py tests/test_quality_scaffold.py tests/test_quality_artifact_report_all.py tests/test_quality_artifact.py tests/quality_gates/test_quality_run_planner.py tests/quality_gates/test_quality_handoff_inventory.py tests/quality_gates/test_quality_skill_docs.py`

## Recommended Next Quality Moves

- active move_type=interface-narrowing; capability_needed=`create-cli` users choose a repo-owned command surface from operator intent before gate families; current_centers=operator contract, intent-first grammar, lifecycle rules; next_center=proof boundary before gates; transformation=step 6 now requires gates to come from the command capability seam already named above; proof_boundary=focused tests plus pilot critique; enforcement_posture=advisory.
- passive move_type=defer-watch; capability_needed=adjacent skills reuse the vocabulary consistently; current_centers=shared reference plus quality packet; next_center=post-pilot thin hooks; transformation=defer `ideation`/`spec`/`create-skill` hooks until critique, because broad rollout before critique may spread paperwork instead of judgment; proof_boundary=pilot critique result; enforcement_posture=no-gate because this is not yet actionable.

## History

- [prior skill quality review](./history/2026-06-25-critique-skill-quality-review.md)
