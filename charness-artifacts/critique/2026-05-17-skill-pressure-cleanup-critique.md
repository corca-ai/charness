# Skill Pressure Cleanup Critique

- Date: 2026-05-17
- Target: public skill pressure cleanup and skill ergonomics gate enforcement
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: n/a (current git diff review)

## Change

Clean up pressure signals across the public skill surface, keep schema and
taxonomy vocabulary honest, and turn Charness' own skill ergonomics checks from
advisory-only warning into configured enforcement for low-noise rules.

## Findings

### Act Before Ship

- `gather` briefly hid the real adapter key by changing
  `gather_provider.<source>.mode` to a generic route phrase. Restored the exact
  key and changed the pressure inventory to ignore inline code spans so schema
  literals do not count as avoidable user-facing branching.
- Restored canonical `access modes` wording where it names integration
  taxonomy rather than casual choice.

### Bundle Anyway

- Treating `## References` as pressure-exempt is honest for current skill
  packages because the section is a link inventory, not workflow prose.
- Charness now enables `long_core`, `mode_option_pressure_terms`,
  `progressive_disclosure_risk`, `code_fence_without_helper_script`, and
  `portable_helper_path_ambiguity` in `.agents/quality-adapter.yaml`, while
  default adapters still leave the noisy policy opt-in.
- Focused tests prove the newly supported gate rules fail when their matching
  heuristic appears, and the current repo has zero skill ergonomics findings.

### Over-Worry

- Most wording replacements preserve intent: `mode maze` to `routing maze`,
  `mode shifts` to `state shifts`, `Report Mode` to `Generated Reports`, and
  `mode choice` to `taxonomy choice`.
- Plugin export and find-skills artifacts were regenerated after the source
  skill changes.

### Valid But Defer

- A future rule can inspect whether `## References` stays mostly link inventory
  instead of becoming hidden workflow prose.
- `code_fence_without_helper_script` overlaps a package validator smell; the
  overlap is acceptable for now because one is package validity and one is
  repo-configured pressure policy.

## Scenario Review

`run_slice_closeout.py` required public-skill scenario review because this slice
changed multiple public skill cores. The reviewed dogfood scaffolds for
`quality`, `gather`, `create-skill`, and `spec` still route to the same skills
with the same expected artifacts or adapter-free behavior:

- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id gather --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-skill --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id spec --json`

Decision: no maintained Cautilus scenario-registry edit is needed. The changes
preserve routing contracts and mainly reduce structural pressure plus enforce
local quality policy. The Cautilus planner reported `run_mode: ask`,
`next_action: none`, and `scenario_registry_review_required: true`; deterministic
validators and this scenario review own closeout without a live evaluator run.

## Proof

- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`: zero heuristics across 22 skills; max core is `release` at 160.
- `python3 skills/public/quality/scripts/validate_skill_ergonomics.py --repo-root .`: passed with all five configured rules.
- `pytest -q tests/quality_gates/test_skill_ergonomics_gate.py tests/quality_gates/test_quality_skill_ergonomics.py`: 21 passed.
- `./scripts/run-quality.sh`: 60 passed, 0 failed, total 87.6s.

## Next Move

Run slice closeout with `--ack-cautilus-skill-review`, then commit the source
skill edits, quality gate enforcement, synced plugin export, refreshed
find-skills/quality artifacts, tests, and this critique artifact together.
