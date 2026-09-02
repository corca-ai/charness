# Lane brief: production subprocess retroactive removal (#768, Goal Run #765)

Read `gh issue view 768` first (Objective, Owned scope "Production", Acceptance,
Non-claims). Then read `scripts/subprocess_guard.py` in full: `run_process`
(short probe, quiet) and `run_monitored_phase` (long phase, streamed
lifecycle, `capture=False` when the child already streams) are the only two
spawn shapes this repo allows, and the module docstring explains why. Read
`runtime_bootstrap.py` (`import_repo_module`) and
`skill_runtime_bootstrap.py` (`load_repo_module_from_skill_script`) for the
in-process idiom.

Outcome for YOUR slice: inside the scope below, no production file calls
`subprocess.*` directly (every spawn goes through `subprocess_guard`), no
repo Python re-spawns repo Python when an in-process import does the same
work, and no spawn hardcodes the string `"python3"`.

## Scope

__SCOPE__

Only these paths. Other lanes own the other production directories and the
tests concurrently; do not touch `tests/**`, `scripts/subprocess_guard.py`,
`scripts/run-quality.sh`, or anything outside your scope, and do not spawn
descendant agents. If a change in your scope breaks a test, fix the CALLER in
your scope, not the test; if the test itself must change, report the test path
and the reason in the commit body instead and leave it red for the parent.

## Rules

1. **Self-invocation → import.** A spawn of this repo's own Python script
   (`[sys.executable, "<repo script>.py", ...]` or `["python3", "scripts/x.py", ...]`)
   becomes an in-process call through `import_repo_module` /
   `load_repo_module_from_skill_script` and the module's `main(argv)` or
   library function. Keep as spawns only: `-m pytest`, `-m coverage`, and the
   `python -c` clean-interpreter probe (their process boundary IS the claim);
   route those through the guard with `sys.executable`.
2. **Plan strings are not spawns.** A file that RENDERS a command line for a
   shell script or a hook (for example gate-plan tuples consumed by
   `run-quality.sh`) is producing text, not spawning; leave the rendered
   `python3` token alone when the consumer is a shell, and say so in the commit
   body for each such file.
3. **External binaries → guard.** `git`, `gh`, `cargo`, `rg`, `cosmic-ray`,
   `npx`, `awiki`, `lychee`, and similar go through `run_process` (short) or
   `run_monitored_phase` (long or streaming). Preserve the caller's timeout,
   cwd, env, and capture semantics; the guard returns a timeout as a RESULT,
   so remove any `try/except TimeoutExpired` the guard now makes dead, and keep
   the caller's refusal policy identical.
4. **`shell=True` sites** (config-driven command strings) pass `shell=True`
   to the guard; do not rewrite them into argv lists (that changes what the
   adapter authors wrote).
5. **No behaviour change.** Same exit codes, same stdout/stderr contract, same
   refusal messages. A caller that captured output still gets it; a caller that
   streamed still streams (`capture=False`).
6. Keep `import subprocess` only where a type annotation
   (`subprocess.CompletedProcess`) needs it; no `subprocess.run/Popen/check_*`
   call may remain in your scope. Verify with:
   `grep -rn "subprocess\.\(run\|Popen\|check_output\|check_call\|call\)(" <your scope>`
   → zero lines.

## Verification before you stop

```
python3 -m ruff check <touched files>
python3 -m ruff format --check <touched files>
python3 scripts/run_standing_pytest.py --repo-root .   # full lane; paste the summary line
./scripts/run-quality.sh
```

Commit in ONE commit with subject
`subprocess: route <your scope label> spawns through subprocess_guard (#768)`
and a body with: per-file disposition (import | guard-short | guard-long |
plan-string-left | kept-spawn-with-reason), the grep result, and the exact
commands with verdicts. No close keyword. Stop after the commit and report the
hash and any test you left red with its reason.
