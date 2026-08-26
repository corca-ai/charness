# Goal Run `backlog-546` runtime-budget intent follow-up

## Scope

- Work item: `backlog-546` / issue `#546`
- Contract source: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md`
- Ownership: quality adapter declaration plus the runtime-budget universe gate

## Implemented contract

`runtime_budget_intent` is now an adapter-owned companion to runtime budgets. It
classifies each budgeted label exactly once as one of:

- `always`: scheduled by the default runner path;
- `conditional`: scheduled only under a named trigger; or
- `external`: not locally enforceable, with the owning boundary named.

The gate checks the exact union of every top-level and profile budget block. A
conditional declaration produces a machine-readable
`execution_proven: false` non-claim; it does not pretend that the trigger ran or
that the label's budget fired. Missing intent remains a migration warning for
older consumers, while a present but incomplete or extra declaration is invalid.

## Executed verification

- `python3 -m pytest -q tests/quality_gates/test_runtime_budget_universe.py tests/quality_gates/test_adapter_lib_yaml.py` — `53 passed`.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` — `11439 passed in 104.36s`.
- `python3 scripts/check_runtime_budget_universe.py --repo-root .` — exit `0`; `status: configured`, `checked: 35`, `universe_size: 109`, `unknown_labels: []`, `missing_labels: []`, `extra_labels: []`, `errors: []`, and `9` explicit conditional non-claims.
- `python3 scripts/validate_adapters.py --repo-root .` — `16` resolvers and `16` YAML files validated, `0` unreconciled keys.
- `python3 scripts/check_export_safe_imports.py --repo-root . --require-git-file-listing` — `862` files validated.
- `python3 scripts/check_plugin_import_smoke.py --repo-root .` — every plugin Python file imported successfully.
- `python3 scripts/check_export_self_sufficiency.py --repo-root .` — `status: pass`.
- `python3 scripts/check_plugin_dir_references.py --repo-root .` — pass.
- Source/plugin parity for the changed validator, helper, universe gate, and adapter library — pass.
- Isolated changed-line proof, using parent `f4572226798eaf41902980ffc9894350694733f3` and proof commit `a053a0e1e7bb5995d816a2a887065aea4177e440`, ran `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, `ok: true`, `4/4` changed mutation-pool files analyzed, `blocking: []`, `unmapped_changed_pool_files: []`.
- Required targeted mutant proof: temporarily changing `check_runtime_budget_universe.py:159` from `errors.append(` to `errors.clear(` made `test_gate_rejects_an_intent_label_without_a_budget` fail with a `None` payload; the line was restored and the focused suite passed.

## Boundary and remaining gap

This is local deterministic proof. The scheduler itself was not changed. The
selected-profile advisory still reports `8` profile-scoped unreachable labels,
and the cosmic-ray config still has one expensive command without a queue label;
those are preserved as explicit advisories, not silently promoted to claims.
Consumer repositories still need their own runner-universe reader and a
consumer-defined conditional-label schema. No conditional trigger execution,
hosted enforcement, installed-host behavior, issue closure, push, release, tag,
or fresh-eye review is claimed. The user-authorized implementation path also
omits forced fresh-eye, handoff, and micro-slice rituals.

The repository-wide Python-length gate remains non-green on six pre-existing
files outside this change (`premise_preflight_lib.py`, `setup_agent_docs_lib.py`,
`check_dup_ratchet.py`, `quality_declaration_lifecycle.py`,
`test_quality_run_planner.py`, and `test_setup_inspect_policy.py`); the new
`adapter_validators.py` length issue was removed by the helper split and the
changed files pass their scoped length hooks.

Issue `#546` remains open because the consumer/trigger-execution boundary is
still unproven.
