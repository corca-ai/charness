<!-- charness-work-item-key: subprocess-retroactive-removal -->

## Objective

Leave one spawn primitive in production code and no repo Python re-spawning repo Python; leave subprocess in tests only where the process boundary is the claim.

## Owned scope

Production (`scripts/`, `skills/`, `native/`): replace the 19 self-invocations of this repo's Python with `runtime_bootstrap.import_repo_module` (the two `-m pytest`, the `-m coverage`, and the `python -c` clean-interpreter probe stay as spawns); remove the 7 hardcoded `"python3"`; route the remaining ~105 external-binary spawns (git, cargo, gh, rg, cosmic-ray) and the 9 config-driven `shell=True` sites through `scripts/subprocess_guard.py`; add a form check that refuses a `subprocess.` call outside the guard.

Tests: for each of the 193 files that spawn `python3` on a repo script, read its recorded reason first (`scripts/boundary-bypass-exemptions.txt`, `boundary_contract` reasons, docstrings). Keep one spawn where the boundary is the claim: `__main__` dispatch smoke, exact exit/stderr contract, child-exit-on-parent-death, env-scrubbed export self-sufficiency, targets that spawn git themselves. Migrate the rest to `tests/script_loader.py`, `script_main.py`, `script_closure.py`. Mark every kept spawn `boundary_contract(reason=...)`. Then delete `scripts/boundary-bypass-baseline.json`, `scripts/boundary-bypass-exemptions.txt`, and the ratchet gate, because the marker now carries the adjudication.

## Acceptance

- AST count of `subprocess.` call sites outside `subprocess_guard.py` in production is zero; a seeded bypass is refused.
- `grep -rln 'sys.executable\|"python3"' tests` equals the set of files carrying `boundary_contract`.
- `pytest --collect-only` count unchanged; per-file pass parity; no migrated test needs `sys.path` filtering to pass.

## Focused verification

Standing pytest lane before and after, with per-file runtime compared.

## Dependencies

gate-scope-repair.

## Non-claims

No replacement of git porcelain with a library. No change to what a test asserts.
