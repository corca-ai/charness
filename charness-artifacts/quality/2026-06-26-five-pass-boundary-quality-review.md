# Quality Review
Date: 2026-06-26

## Scope

Target boundary: follow-up quality slice covering web-fetch route split,
gather terminal taxonomy, import-safe script tests, boundary-bypass reduction,
and mutation coverage refresh.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, existing
intentional CLI smokes, and the larger nested-CLI backlog are not fully fixed
here.

## Current Gates

- Focused pytest passed 165 tests across web-fetch routing, gather terminal
  source resolution, gather planning, docs/misc quality, find-skills loader
  conversions, and public URL support.
- Slice closeout passed deterministic validators, boundary-bypass ratchet,
  broad read-only pytest, and mutation coverage producer.
- Public `gather` dogfood validation passed after recording the terminal
  taxonomy review and scenario-registry decision.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: closeout broad read-only pytest completed in 60.0s; fast
  focused pytest suites completed in 0.59s, 3.30s, and 10.24s.
- coverage gate: `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage` passed and wrote mutation coverage artifacts.
- evaluator depth: deterministic gates only; `plan_cautilus_proof.py` returned
  `next_action: none`, so no Cautilus run was allowed or needed; gather
  scenario-registry review stayed on deterministic plan/route tests.

## Healthy

- `route_public_fetch.py` is now a smaller facade; route tables, host matching,
  GitHub adapter mode resolution, and gather-adapter discovery live in
  `route_public_fetch_routes.py`.
- `tests/script_loader.py` removes duplicated dataclass-safe script import
  helpers from find-skills and docs/misc tests.
- `tests/quality_gates/test_docs_and_misc.py` reduced one boundary-bypass key
  while retaining `current_release.py` CLI wiring through direct `main()`
  invocation with patched argv and captured stdout.
- X/Twitter source resolution now emits `terminal_category`; gather plans
  advertise the categories and durable records render them.
- Effective boundary-bypass key count improved from 117 to 116 for this slice.

## Weak

- `tests/quality_gates/test_docs_and_misc.py` still has an advisory subprocess
  smoke for `synthesize_operator_acceptance.py`; fresh-eye did not review that
  older boundary in this slice.
- Changed-line mutation self-check must be rerun after commit because
  uncommitted mutation-pool changes are outside the `origin/main..HEAD` range.
- `tests/quality_gates/test_docs_and_misc.py` remains a large mixed quality
  test file, although this slice extracted shared script loading.

## Missing

- Missing before this slice: terminal source-resolution taxonomy had no
  category field, gather plan did not advertise the category contract, and
  repeated test-local script loaders made import-safe conversions noisier.

## Deferred

- Tokenizer-specific prompt measurement remains deferred; this slice targets
  script execution fanout, source-resolution clarity, and mutation proof.

## Advisory

- structural review result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` reports ok with 116
  effective candidate keys and no new candidate keys.
- prose review result: `testability-and-selection.md` supports keeping thin
  real-boundary smokes while moving ordinary behavior assertions below the
  boundary; `current_release.py` now follows that rule without subprocess.
- public-skill review result: `suggest_public_skill_dogfood.py --skill-id
  gather --json` was inspected, `docs/public-skill-dogfood.json` records the
  terminal taxonomy update, and `evals/cautilus/scenarios.json` remains mapped
  to `gather-adapter-bootstrap`.
- fresh-eye result: artifact:
  `charness-artifacts/critique/2026-06-26-web-fetch-gather-quality-slice.md`
  records two findings that were fixed before closeout.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f034f-5e94-74f0-a201-587e6d39978b` found one medium CLI-boundary gap and
  one low gather-plan contract gap; both were fixed before closeout.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass ratchet, shared loader
  extraction, focused pytest, broad read-only pytest, and mutation coverage.

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id gather --json`
- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock --produce-mutation-coverage --mutation-coverage-extra-pytest-target tests/test_web_fetch_route_and_classify.py --mutation-coverage-extra-pytest-target tests/test_twitter_exact_source.py --mutation-coverage-extra-pytest-target tests/test_gather_plan.py --mutation-coverage-extra-pytest-target tests/quality_gates/test_docs_and_misc.py --ack-cautilus-skill-review`
- `python3 scripts/run_slice_closeout.py --repo-root . --base origin/main --verification-lock --produce-mutation-coverage --mutation-coverage-extra-pytest-target tests/test_web_fetch_route_and_classify.py --mutation-coverage-extra-pytest-target tests/test_twitter_exact_source.py --mutation-coverage-extra-pytest-target tests/test_gather_plan.py --mutation-coverage-extra-pytest-target tests/quality_gates/test_docs_and_misc.py --ack-cautilus-skill-review`
- `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha origin/main --reuse-coverage`

## Recommended Next Gates

- active none — post-commit changed-line mutation coverage passed for the
  changed mutation-pool files.
- passive convert the existing `synthesize_operator_acceptance.py` subprocess because
  only after proving it has another operator-facing CLI boundary; fresh-eye
  already caught one over-conversion in this class.
- passive keep `route_public_fetch_routes.py` below the warn band because it
  now owns the concentrated web-fetch route table and may keep accumulating
  route-specific behavior.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
