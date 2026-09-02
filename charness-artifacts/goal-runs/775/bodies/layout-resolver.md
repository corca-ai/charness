<!-- charness-work-item-key: layout-resolver -->

## Objective

One resolver beside `scripts/core/repo_layout.py` answers "where does repo script X live" for the flat and packaged layouts, and the three independent lookups are gone.

## Owned scope

- Add the resolver (flat name in, path out; packaged subdirectory search; missing script is a typed miss, never a silent fallback).
- Fold and delete: `scripts/core/scaffold_artifact_lib.py::_repo_script` (glob), `tests/quality_gates/seeding_support.py::_packaged_script` and `_seed_path` (rglob), `skills/public/quality/scripts/public_spec_adapter_policy.py::load_repo_script_module` (glob). `scripts/core` ships with the export, so the skill imports the resolver; the native `export-safe` gate forbids only `skills.public` imports.
- `scripts/staged_commit_gate_plan_helpers.py::present_gate` is not a layout search (it chooses `tools/` versus `scripts/` for a relative path); it calls the resolver for the existence check and is otherwise unchanged.
- A form check refusing any `glob`/`rglob` search for a script name under `scripts/` outside the resolver module.
- Tests: flat layout, packaged layout, missing script, seeded duplicate lookup refused.

## Acceptance

- The form check passes on the tree and refuses a seeded `rglob` lookup.
- Gates `check-export-safe-imports` and `check-export-self-sufficiency` green; the exported quality skill still resolves its repo scripts.
- Standing lane green with the skip list read.

## Focused verification

Resolver tests, the export-safety gates, `run_standing_pytest.py`.

## Dependencies

awiki-phase-echo (order only).

## Non-claims

No file moves; no rename sweep tool.
