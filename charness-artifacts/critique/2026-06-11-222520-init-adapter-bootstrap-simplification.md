# Critique: init adapter bootstrap simplification

Date: 2026-06-11
Scope: Slice 2 of `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`

## Decision Reviewed

Replace repeated `runpy.run_path` plus `SimpleNamespace` bootstrap loader bodies
in selected public skill `init_adapter.py` files with a shorter root-discovery
pattern:

- find the nearest ancestor containing `skill_runtime_bootstrap.py`;
- insert that ancestor into `sys.path`;
- import `skill_runtime_bootstrap` as the runtime helper;
- keep existing `load_repo_module_from_skill_script` behavior.

Changed source files:

- `skills/public/achieve/scripts/init_adapter.py`
- `skills/public/announcement/scripts/init_adapter.py`
- `skills/public/create-skill/scripts/init_adapter.py`
- `skills/public/find-skills/scripts/init_adapter.py`
- `skills/public/hitl/scripts/init_adapter.py`
- `skills/public/hotl/scripts/init_adapter.py`
- `skills/public/impl/scripts/init_adapter.py`
- `skills/public/narrative/scripts/init_adapter.py`
- `skills/public/quality/scripts/init_adapter.py`
- `skills/public/release/scripts/init_adapter.py`
- `skills/public/retro/scripts/init_adapter.py`
- `tests/quality_gates/test_hotl_adapter.py`
- generated `plugins/charness/skills/*/scripts/init_adapter.py` mirrors

## Expected Invariants

- Public skill `init_adapter.py` scripts still run from the source checkout.
- Exported plugin mirrors still carry `skill_runtime_bootstrap.py` and import it
  from the exported plugin root.
- A stranded package without an ancestor `skill_runtime_bootstrap.py` still
  fails visibly.
- The slice reduces real bootstrap boilerplate without hiding unresolved
  resolver or scaffold duplication.

## Executed Proof

- Focused pytest: `33 passed`.
- Smoke: all 11 changed `init_adapter.py` scripts wrote adapter scaffolds into a
  temporary repo.
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`.
- `python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py`.
- `python3 scripts/validate_skills.py --repo-root .`.
- `python3 scripts/validate_public_skill_validation.py --repo-root .`.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`.
- `python3 scripts/validate_packaging.py --repo-root .`.
- `python3 scripts/validate_packaging_committed.py --repo-root .`.
- Doc and hygiene gates from `check_changed_surfaces.py`.
- Broad pytest: `2803 passed, 4 skipped, 26 deselected`.
- `nose` broad scan: `526 families / 13164 dup_lines` before, `525 families /
  12773 dup_lines` after.
- `nose` resolver/scaffold-filtered `top 25`: `2924` duplicated lines before,
  `2278` after.

## Fresh-Eye Findings

Reviewer: subagent `Mendel`.

- Low: same-interpreter multi-root cache remains a blind spot. Normal import
  keys the bootstrap by `sys.modules["skill_runtime_bootstrap"]`, so a single
  long-lived Python process importing adapters from two different Charness roots
  could reuse the first bootstrap module. The reviewer did not consider this a
  blocker because normal CLI/plugin execution uses fresh processes and the
  runtime functions derive repo root from the caller path.

No blocker found.

## Counterweight

This is not a complete bootstrap commonization. A small repeated root-discovery
block remains because each public skill script must find the repo or plugin root
before it can import repo-owned helpers. Removing that last local block would
either require a globally installed dependency or reintroduce a larger inline
loader.

The residual cache risk does not block this slice, but it should be revisited if
Charness starts importing source and installed plugin adapters together in one
long-lived Python process.
