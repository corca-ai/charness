# Goal Run `backlog-722` ownership-shaped setup plan

## Scope

- Work item: `backlog-722` / issue `#722`
- Contract source: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md`
- Owned producers: `scripts/setup_operating_surface_lib.py`, `scripts/setup_agent_docs_lib.py`, and `scripts/setup_inspect_quality_lib.py`, with byte-identical plugin mirrors
- Owned test fixture: `tests/quality_gates/test_setup_operating_surface_plan.py`

## Implemented contract

The setup/quality boundary now emits a deterministic, plan-only ownership
map. Each surface and move includes `surface`, `owner`, `source`, `consumer`,
`action`, and `confidence`, while retaining lexical shape and deeper-owner
candidate evidence. `medium` confidence is reserved for readable structure;
path-only or empty input leaves the owner unset, reports `confidence: none`,
and refuses ownership assignment with the stable reason that readable
structure is required and path existence alone is insufficient.

The implementation lives in a cohesive dedicated producer rather than
inflating the already-saturated agent-docs reader. Both source and plugin
producer/consumer mirrors compare byte-identically. No content mutation or
approval is performed by inspection.

## Executed verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_setup_inspect_policy.py` — `44 passed`.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_setup_inspect_policy.py --pytest-target tests/quality_gates/test_setup_operating_surface_plan.py` — `47 passed`.
- Source/plugin `cmp`, `py_compile`, `ruff`, Python length validation, and `git diff --check` passed.
- Isolated proof commit `e250565f9`: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, 3/3 changed mutation-pool files analyzed, `blocking: []`, and `unmapped_changed_pool_files: []`.
- The overloaded classification mutant was caught by the ownership fixture and restored.

## Boundary and non-claims

This is local deterministic verification only. It does not claim semantic
ownership approval, documentation movement, installation, hosted behavior,
release, tag, push, or issue closure. The user-authorized path omits forced
fresh-eye, handoff, and micro-slice rituals; no fresh-eye result is claimed.
Issue `#722` remains open.
