AI-provenance: agent-drafted via charness issue resolve; posted as manual fallback closeout after the direct-commit auto-close carrier closed the issue but lacked the enforced closeout ledger shape.

Manual fallback reason: auto-close-failed-after-remote-verification

JTBD: The scheduled mutation-test issue should stop recurring because the JS mutation slice stays within its configured workload budget and uses the same deterministic seed in selection and execution.

Root cause: `scripts/run_js_mutation.py` omitted `scripts/agent-runtime/build-skill-execution-observation.mjs` from the JS mutant-weight table and treated missing weights as zero-cost; `.github/workflows/mutation-tests.yml` also computed `MUTATION_SAMPLE_SEED` for `Select mutation sample` but did not pass it into `Run mutation`.

Debug artifact: `charness-artifacts/debug/2026-06-25-issue-400-js-mutation-weight-gap.md`

Siblings: decision: bundled the same positive-weight guard, indexed lookup, checked-in workflow seed handoff, quality template seed handoff, and focused tests; deferred broad survivor-killing for `build-skill-execution-observation.mjs` as outside this scheduler-regression slice. proof: `tests/quality_gates/test_js_mutation_tooling.py`, `tests/quality_gates/test_quality_mutation_testing.py`, `MUTATION_SAMPLE_SEED='28100660350:236774f484978a60564b013afe79053c69ad986f..074498316feb84afedf9ca217da9a5ac71cae114' npm run test:mutation:js`, and `python3 scripts/check_js_mutation_score.py --repo-root .`.

Prevention: Full-mode JS mutation selection now refuses missing or non-positive mutant weights, uses indexed weight lookup after the table guard, tests exact weight-table coverage, and requires both the checked-in workflow and reusable template to pass the scheduled sample seed into the mutation run.

Behavior: verified through local deterministic runner evidence distinct from GitHub closed state: the issue seed JS mutation run exited 0 and `python3 scripts/check_js_mutation_score.py --repo-root .` reported StrykerJS above threshold.

Critique: charness-artifacts/critique/2026-06-25-issue-400-js-mutation-resolution.md
