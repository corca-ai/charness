# Cautilus Dogfood
Date: 2026-05-02

## Trigger

- slice: GitHub issue #91 HITL report mode for decision-queue review packets.
- issue: `hitl` needed a small report mode that makes human decisions primary,
  keeps suggested actions display-only, drops untouched `unreviewed` cards, and
  explains generated tables before showing raw structure.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while widening the `hitl` public
  contract with decision-first report packet rendering.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/report-mode.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --paths skills/public/hitl/SKILL.md skills/public/hitl/references/report-mode.md skills/public/hitl/scripts/render_report.py scripts/hitl_report_mode_lib.py --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260502T000000000Z-hitl-report-mode`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id hitl --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- run artifact: `.cautilus/runs/20260502T000000000Z-hitl-report-mode/`
- summary:
  `.cautilus/runs/20260502T000000000Z-hitl-report-mode/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked
- routing: 5/5 expected routes matched; bootstrap helper remained
  `find-skills`.

## Scenario Review

- Representative scenario: adding `hitl` report mode should not make generic
  validation or implementation prompts route directly to HITL.
- Expected behavior: startup discovery still routes through `find-skills`, and
  validation-shaped review remains `quality` before HITL/manual review.
- Observed behavior: the maintained routing fixture completed successfully
  after the HITL report-mode guidance changed.
- HITL dogfood decision: update `docs/public-skill-dogfood.json` for `hitl` to
  freeze the decision-first packet renderer, display-only suggested decisions,
  and plain-language table interpretation as reviewed consumer contract.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  deterministic report-mode tests prove issue #91 behavior directly, and the
  existing routing fixture covers the preserve-goal prompt surface slice.

## Outcome

- recommendation: `accept-now`
- The prompt-surface changes preserve current Cautilus routing behavior.
- The HITL report mode is backed by deterministic helper tests and checked-in
  dogfood evidence instead of requiring a new maintained Cautilus scenario.

## Follow-ups

- Add a dedicated semantic Cautilus scenario only if later `hitl` changes alter
  routing for bounded human-review requests rather than adding deterministic
  report packet behavior.
