# Cautilus Dogfood
Date: 2026-05-02

## Trigger

- slice: HITL adaptive decision queue for report-mode review packets.
- issue: `hitl` should not mechanically present chunks in source order when
  one early decision can set a rule, reprioritize remaining cards, or make the
  current queue stale enough that fixing and restarting is better.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while widening the `hitl` public
  contract with adaptive decision ordering, structured queue effects, and
  display-only restart recommendations.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/report-mode.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --paths skills/public/hitl/SKILL.md skills/public/hitl/references/report-mode.md scripts/hitl_report_mode_lib.py skills/public/hitl/scripts/bootstrap_review.py --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260502T123000000Z-hitl-adaptive-decision-queue`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id hitl --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- run artifact:
  `.cautilus/runs/20260502T123000000Z-hitl-adaptive-decision-queue/`
- summary:
  `.cautilus/runs/20260502T123000000Z-hitl-adaptive-decision-queue/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked
- routing: 5/5 expected routes matched; bootstrap helper remained
  `find-skills`.

## Scenario Review

- Representative scenario: adding adaptive HITL queue guidance should not make
  generic implementation, spec, or validation prompts route directly to HITL.
- Expected behavior: startup discovery still routes through `find-skills`;
  implementation-shaped work remains `impl`; concept-to-contract work remains
  `spec`; validation-shaped review remains `quality` before HITL/manual review.
- Observed behavior: the maintained routing fixture completed successfully
  after the HITL adaptive queue guidance changed.
- HITL dogfood decision: update `docs/public-skill-dogfood.json` for `hitl` to
  freeze stable adaptive IDs, deterministic priority ordering, structured
  review-input effects, display-only restart recommendations, and superseded
  items staying unreviewed.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  deterministic report-mode tests prove the adaptive queue behavior directly,
  and the existing routing fixture covers the preserve-goal prompt surface
  slice.

## Outcome

- recommendation: `accept-now`
- The prompt-surface changes preserve current Cautilus routing behavior.
- The adaptive queue behavior is backed by deterministic helper tests and
  checked-in dogfood evidence instead of requiring a new maintained Cautilus
  scenario.

## Follow-ups

- Add a dedicated semantic Cautilus scenario only if later `hitl` changes alter
  routing for bounded human-review requests rather than adding deterministic
  report packet behavior.
