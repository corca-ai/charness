# Lane brief: test subprocess migration (#768, Goal Run #765)

Read `gh issue view 768` first (Owned scope "Tests", Acceptance, Non-claims:
"No change to what a test asserts"). Then read `tests/script_main.py`
(`load_script_module`, `run_loaded_script_main`), `tests/script_loader.py`,
`tests/script_closure.py`, `tests/quality_gates/inprocess_script_support.py`,
`scripts/boundary-bypass-exemptions.txt`, and the `boundary_contract` marker
in `pyproject.toml`. Read the retro lesson: a test proving a LOCAL layout fact
must assert what the module under test bound, never a global interpreter
property; never make a migrated test pass by filtering `sys.path`.

Outcome for YOUR slice: every test file in the scope below either runs the
repo script in-process (through the loaders above) or keeps its spawn because
the process boundary IS the claim, and every kept spawn carries
`@pytest.mark.boundary_contract(reason="...")` with a reason a reader can judge.

## Scope

__SCOPE__

Only these test files. Other lanes own the other test batches and the
production code concurrently; do not touch `scripts/**`, `skills/**`, any test
outside your list, `pyproject.toml`, or the shared helpers in `tests/*.py`
(if a helper is missing something, report it in the commit body instead). Do
not spawn descendant agents.

## Decision rule per file

Read the file's recorded reason first (`boundary-bypass-exemptions.txt`,
existing `boundary_contract` reasons, docstrings). KEEP a spawn only when one
of these is the claim, and name it in the marker reason:

- `__main__` dispatch smoke (the script must be runnable as a program);
- exact exit-code / stderr contract of the process;
- child-exit-on-parent-death or signal behaviour;
- env-scrubbed export self-sufficiency (a clean interpreter is the point);
- the target itself spawns git or another binary and the test observes that.

Everything else MIGRATES: call `main(argv)` through `run_loaded_script_main`
or the module's functions through `load_script_module`, capture stdout with
`capsys`, and assert the SAME things the test asserted before (output text,
exit code from the returned int, files written). Do not weaken or reword an
assertion; if an assertion cannot be expressed in-process, that is a KEEP with
that reason.

A migrated test must not import the script through `sys.path` manipulation or
pass only because of interpreter state; use the loaders.

## Verification before you stop

```
python3 -m pytest --collect-only -q <your files> | tail -1      # record the count BEFORE you start, and after; they must match
python3 -m ruff check <touched files>
python3 -m ruff format --check <touched files>
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target <each touched file>
python3 scripts/run_standing_pytest.py --repo-root .            # full lane; paste the summary line
```

Commit in ONE commit with subject
`tests: run <your batch label> repo scripts in-process, mark real boundaries (#768)`
and a body with: per-file disposition (migrated | kept: <reason>), the
collect-only count before/after, and the exact commands with verdicts. No
close keyword. Stop after the commit and report the hash.
