# Critique: JS-Native Agent Runtime Mutation

Date: 2026-05-21
Target: mutation workflow/testability slice
Fresh-Eye Satisfaction: parent-delegated

## Change

Move the StrykerJS agent-runtime mutation slice off Python pytest and onto a
repo-native JavaScript test command. The Stryker command runner now executes
`npm run test:agent-runtime`, which uses Node's native test runner against
`tests/agent-runtime/*.test.mjs`.

## Findings

- Act Before Ship: prove Stryker can run the JS-native command from its temp
  sandbox, not only from the source checkout.
- Bundle Anyway: guard future `scripts/agent-runtime/*.mjs` additions so they
  cannot enter the mutation pool without being imported by the JS-native test.
- Over-Worry: do not add Jest, Vitest, or a new JS framework for this slice;
  Node's built-in test runner is enough for the deterministic module contracts.
- Valid but Defer: per-mutant affected-test selection for JavaScript remains
  outside the command-runner design. This slice keeps the surface small and
  budgeted instead of claiming coverage-derived precision.

## Applied Before Commit

- `stryker.config.mjs` command runner now calls `npm run test:agent-runtime`.
- `tests/agent-runtime/native.test.mjs` imports and behaviorally exercises all
  current `scripts/agent-runtime/*.mjs` modules.
- `tests/quality_gates/test_js_mutation_tooling.py` pins the command, excludes
  pytest, pins the mutation pool, and asserts the native test imports every
  mutated agent-runtime module.
- `.agents/surfaces.json` routes agent-runtime JS changes to the native test and
  JS mutation dry-run.
- `skills/public/quality/references/mutation-testing.md` and the checked-in
  plugin export document the JS-native command-runner posture.

## Proof

- `npm run test:agent-runtime`
- `npm run test:mutation:js:dry-run`
- `MUTATION_JS_TARGETS=scripts/agent-runtime/contract-versions.mjs MUTATION_JS_TIMEOUT_SECONDS=180 npm run test:mutation:js`
- `python3 scripts/check_js_mutation_score.py --repo-root .`
- `python3 -m pytest -q tests/quality_gates/test_js_mutation_tooling.py tests/quality_gates/test_surface_obligations.py::test_check_changed_surfaces_routes_agent_runtime_js_to_native_tests`
- `python3 scripts/validate_surfaces.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
