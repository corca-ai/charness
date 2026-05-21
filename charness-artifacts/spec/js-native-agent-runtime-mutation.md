# JS-Native Agent Runtime Mutation

## Problem

The current StrykerJS slice mutates `scripts/agent-runtime/*.mjs` but kills
mutants by running `python3 -m pytest -q tests/test_cautilus_scenarios.py`.
That works because the Python tests shell out to Node, but it keeps JS mutation
testability coupled to Python wrapper behavior and makes the mutation command
harder to reason about.

## Current Slice

Move the StrykerJS command runner to a repo-owned JS-native test command while
keeping the existing Python tests as cross-language integration smokes.

## Fixed Decisions

- Add a `node:test` surface under `tests/agent-runtime/` that directly imports
  and exercises the agent-runtime ESM modules.
- Add `npm run test:agent-runtime` as the stable JS-native test command.
- Update `stryker.config.mjs` to run `npm run test:agent-runtime`, not pytest.
- Keep Python tests that execute the CLI runner; they prove Python workflow
  integration, not the Stryker kill command.

## Probe Questions

- Whether direct module tests expose missing exports or import-time side
  effects that were hidden by the Python wrapper.
- Whether the new command still gives useful Stryker feedback within the
  existing JS mutation budget.

## Deferred Decisions

- Whether to split `run-local-eval-test.mjs` into smaller modules. This slice
  may add tests around the current exports, but should not refactor runtime code
  unless direct JS tests reveal a necessary seam.

## Non-Goals

- Do not remove Python integration tests.
- Do not change Cautilus adapter behavior or live evaluator proof.
- Do not widen JS mutation beyond `scripts/agent-runtime/*.mjs`.

## Success Criteria

- StrykerJS no longer invokes pytest for the JS mutation slice.
- The JS-native test command directly imports all six files in
  `scripts/agent-runtime/`.
- The JS-native test command covers representative positive and negative
  behavior, not only import smoke.
- Existing mutation wrapper tests assert the new command so this does not drift
  back to pytest silently.

## Acceptance Checks

- `npm run test:agent-runtime`
- `npm run test:mutation:js:dry-run`
- `python3 -m pytest -q tests/quality_gates/test_js_mutation_tooling.py`
- Surface closeout commands reported by
  `python3 scripts/check_changed_surfaces.py --repo-root .`

## Critique

Pre-implementation fresh-eye review `019e4902-6003-7ae3-990d-b64051fc9fc9`
accepted the direction with four act-before-ship requirements: Stryker must not
invoke pytest; JS tests must avoid captured absolute checkout paths because
Stryker runs against a temp copy; parity must cover the existing fixture,
concept assertion, Codex argument/auth, home isolation, and entry-file
normalization behavior instead of import smoke only; and contract constants
need direct assertions.

The implementation follows those constraints with `tests/agent-runtime` using
repo-relative ESM imports, `npm run test:agent-runtime` as the Stryker command,
and a surface obligation that routes agent-runtime JS changes to the native
test command and JS mutation dry-run.

## Canonical Artifact

This file owns the slice contract until implementation lands.

## First Implementation Slice

Create the JS-native test command, point Stryker at it, update tests and docs,
then run focused JS, mutation dry-run, and affected Python quality tests.
