# Lane brief: repair test seams after the subprocess_guard migration (#768, Goal Run #765)

Context: six lanes moved every production spawn in `scripts/` and `skills/` to
`scripts/subprocess_guard.py` (`run_process` for short probes,
`run_monitored_phase` for long phases) and migrated most tests in-process. The
integrated tree now has failing tests in the files listed below. Read
`scripts/subprocess_guard.py` (docstring and both signatures), `tests/script_main.py`,
`tests/quality_gates/inprocess_script_support.py`, and the `boundary_contract`
marker in `pyproject.toml` before touching anything.

Outcome for YOUR slice: every listed test file is green under
`python3 scripts/run_standing_pytest.py --repo-root . --pytest-target <file>`,
asserts the SAME facts it asserted before, and spawns repo Python only where the
process boundary is the claim, marked `@pytest.mark.boundary_contract(reason=...)`.

## Scope

__SCOPE__

Only these test files. Do not edit `scripts/**`, `skills/**`, `pyproject.toml`,
or shared helpers in `tests/*.py`; if a helper or a production module needs a
change, report the exact file, line, and reason in the commit body and leave
that test red. Do not spawn descendant agents.

## Seam rules

1. `monkeypatch.setattr(module.subprocess, "run", fake)` and friends: the module
   no longer imports `subprocess`; it binds `run_process` (and sometimes
   `run_monitored_phase`) from the guard at import. Patch `module.run_process`
   (or `module.run_monitored_phase`). Prefer patching the module attribute over
   `scripts.subprocess_guard.run_process` so the test names the seam it owns.
2. A fake must accept the guard signature: `run_process(command, *, cwd, env=None,
   timeout_seconds=..., shell=False, executable=None)` returning
   `subprocess.CompletedProcess[str]` with TEXT stdout/stderr (never bytes);
   `run_monitored_phase(command, *, cwd, phase, timeout_seconds, display=None,
   heartbeat_seconds=..., env=None, shell=False, executable=None, stream=None,
   capture=True)` returning a `PhaseOutcome` (read the dataclass in the guard).
   Use `**kwargs` in fakes so a caller's keyword does not break the test.
3. The guard never raises `CalledProcessError` or `TimeoutExpired`; it returns
   the code (timeout is `TIMEOUT_EXIT_CODE` with a stderr marker). A test that
   asserted an exception now asserts the same failure through the returned
   result or the caller's own refusal; the FACT asserted (this input fails, with
   this message) stays the same.
4. A test that asserts the argv contained `"python3"` for a spawn that is now
   an in-process import: the behaviour under test moved; assert the in-process
   effect (the called function, the emitted output) instead. Say so in the
   commit body per test.
5. Leftover migration files (those in the scope that still spawn repo Python
   without a marker): apply the migration rule: keep a spawn only for
   `__main__` dispatch smoke, exact exit/stderr contract, child-exit-on-parent
   death, env-scrubbed export self-sufficiency, or a target that spawns git or
   another binary itself; mark it; migrate the rest through the loaders.
6. Never make a test pass by filtering `sys.path` or weakening an assertion.

## Verification before you stop

```
CHARNESS_ALLOW_BARE_PYTEST=1 python3 -m pytest --collect-only -q <your files> | tail -1   # before and after; must match
python3 -m ruff check <touched files>; python3 -m ruff format --check <touched files>
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target <each touched file>
python3 scripts/run_standing_pytest.py --repo-root .     # paste the summary line
```

Commit in ONE commit with subject
`tests: repair <batch label> seams for the subprocess_guard migration (#768)`
and a body listing per file: repaired | migrated | kept: <reason> | left red: <file:line reason>.
No close keyword. Stop after the commit and report the hash.
