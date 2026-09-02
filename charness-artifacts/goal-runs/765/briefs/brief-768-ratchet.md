# Lane brief: retire the boundary-bypass ratchet (#768, Goal Run #765)

Read `gh issue view 768` (Tests paragraph, last sentence: delete
`scripts/boundary-bypass-baseline.json`, `scripts/boundary-bypass-exemptions.txt`,
and the ratchet gate, because the `boundary_contract` marker now carries the
adjudication). Read `skills/public/quality/references/boundary-bypass-ratchet.md`
and `scripts/check_boundary_bypass_ratchet.py` to learn what the ratchet
guarded, then `scripts/check_subprocess_form.py` (the production-side
replacement) and the `boundary_contract` marker in `pyproject.toml` (the
test-side replacement).

Outcome: the ratchet gate, its baseline, its exemptions file, and its
library are gone; every reference to them is removed or repointed; the
inventory that MEASURES test process boundaries may stay only if something
still consumes it (say which). Nothing that still catches a real failure mode
is deleted without naming its replacement.

## Scope

You may edit or delete: `scripts/check_boundary_bypass_ratchet.py`,
`scripts/boundary_bypass_ratchet_lib.py`, `scripts/boundary-bypass-baseline.json`,
`scripts/boundary-bypass-exemptions.txt`, `scripts/inventory_boundary_bypass.py`,
`scripts/inventory_boundary_bypass_lib.py`, `scripts/check_staged_test_boundaries.py`,
`scripts/staged_commit_gate_plan.py`, `scripts/subprocess_only_coverage_advisory.py`,
`scripts/validate_quality_artifact.py`, `scripts/waiver_file_lines.py`,
`scripts/run-quality.sh`, `.githooks/pre-commit`, `.agents/quality-adapter.yaml`,
`.agents/surfaces.json`, `docs/deferred-decisions.md`, `docs/validator-timing-layers.md`,
`native/repograph/fixtures/carriers/expected/quality_label_universe.yaml`,
`skills/public/quality/references/boundary-bypass-payload.example.json`,
`skills/public/quality/references/boundary-bypass-ratchet.md`,
`skills/public/quality/references/catalog.yaml`,
`skills/public/quality/references/consumer-validator-catalog.yaml`,
`skills/public/quality/references/index.md`,
`skills/public/quality/references/inventory-dispatch.md`,
`skills/public/quality/references/testability-and-selection.md`,
`skills/public/quality/scripts/dup_ratchet_lib.py`,
`skills/public/quality/scripts/validate_boundary_bypass_payload.py`,
and the tests that name the ratchet: `tests/test_boundary_bypass_ratchet.py`,
`tests/test_boundary_bypass_inventory.py`,
`tests/quality_gates/test_boundary_bypass_payload_validator.py`,
`tests/quality_gates/test_staged_commit_gate_plan.py`,
`tests/quality_gates/test_subprocess_only_coverage_advisory.py`,
`tests/quality_gates/test_test_production_ratio.py`,
`tests/quality_gates/inprocess_script_support.py`, `tests/quality_gates/support.py`,
`tests/coverage_debt/test_batch3.py`, `tests/coverage_debt/test_batch5.py`,
`tests/coverage_debt/test_batch6.py`, and any other test whose only reference is
a fixture path (path-only edits).
Do not touch `plugins/**` (generated). Do not spawn descendant agents.

## Rules

1. Delete the gate, library, baseline, and exemptions with `git rm`. For each,
   write in the commit body the failure mode it caught and the replacement that
   now catches it (production: `check_subprocess_form.py`; tests: the
   `boundary_contract` marker plus the in-process loaders).
2. `inventory_boundary_bypass*.py` is a measurement, not a gate. Keep it only
   if `validate_quality_artifact.py`, `subprocess_only_coverage_advisory.py`,
   the quality skill's `inventory-dispatch.md`, or `.agents/surfaces.json`
   still consume its payload after the ratchet is gone; otherwise delete it
   with the same failure-mode line. Do not leave a producer with no consumer.
3. Remove the `check-boundary-bypass-ratchet` queue line from `run-quality.sh`,
   its `.githooks/pre-commit` and `staged_commit_gate_plan.py` entries, its
   `validator-timing-layers.md` row (add a one-line note that it was retired by
   #768 and what replaced it), its catalog entries, and its surfaces entry.
   Add `check-subprocess-form` to `run-quality.sh` right after
   `check-python-runtime-inheritance` (`python3 scripts/check_subprocess_form.py --repo-root "$REPO_ROOT" --require-git-file-listing`),
   to the runner fixture list in `tests/quality_gates/support.py` beside the
   other gate labels, and to `docs/validator-timing-layers.md` as a new row.
4. Tests that tested the ratchet itself are deleted with it. Tests that used
   the ratchet's payload as fixture data get a path-only edit or the fixture
   inlined; their assertions do not change.
5. Acceptance greps for the issue (run and paste):
   `grep -rln 'sys.executable\|"python3"' tests` versus
   `grep -rln boundary_contract tests`: report the two sets and their difference.

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/check_unreferenced_scripts.py --repo-root . --strict
python3 scripts/run_standing_pytest.py --repo-root .      # paste the summary line
./scripts/run-quality.sh
./scripts/check-docs.sh
```

Commit in ONE commit with subject
`quality: retire the boundary-bypass ratchet; the marker and the form gate carry the adjudication (#768)`
and a body with the per-file failure-mode lines, the acceptance grep sets, and
the exact commands with verdicts. No close keyword. Stop after the commit and
report the hash.
