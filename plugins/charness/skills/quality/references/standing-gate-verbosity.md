# Standing Gate Verbosity

When a repo already has a standing local gate such as `pre-push`, `verify`, or
`lefthook pre-push`, `quality` should treat verbosity shape as an operability
concern rather than as harmless style.

The default gate should answer three questions quickly:

- which phase just ran
- how long it took
- what failed first

Quiet defaults and failure detail are complements, not opposites. A good gate
stays compact on green, then becomes loud enough to act on when a seam fails.

Use `<repo-root>/scripts/inventory_standing_gate_verbosity.py` when a repo keeps a standing
hook, hook runner, or verify chain.

## Inventory Axes

Review these six axes and classify each as `healthy`, `weak`, `missing`, or
`not_applicable` when the repo genuinely does not use that shape:

1. **Test-runner reporter**
   - `node --test` should pin
     `--test-reporter=dot --test-reporter-destination=stdout`
   - `pytest` should usually run with `-q`
   - `jest` / `vitest` should usually prefer a dot reporter in the standing gate
   - `go test -v` is usually a smell in the default gate
   - `cargo test -- --nocapture` is usually a smell in the default gate
2. **Orchestrator output mode**
   - prefer a thin orchestrator that delegates `pre-push` to a repo-owned
     runner (for example `<repo-root>/scripts/run-pre-push.sh`,
     `<repo-root>/scripts/run-pre-push.mjs`, or
     `<repo-root>/scripts/run-quality.sh`). The runner owns
     quiet-default success output, failure-path log replay, per-phase elapsed
     reporting, and a single verbose-on-demand env seam — shapes that outlive
     any one orchestrator's UI quirks.
   - grouped output configured on the orchestrator itself
     (`lefthook output:` / `skip_output:`) is an acceptable secondary local
     fix when the orchestrator still fans out commands directly under
     `parallel: true`. Treat it as a fallback, not as the design target.
   - `lefthook` with `parallel: true` should not leave success logs to raw
     interleaving by default.
3. **Per-gate chatter**
   - noisy tools such as `pylint`, `coverage report`, or `specdown` should use
     their quietest honest defaults in the standing gate
   - verbose troubleshooting output should move behind an env flag or sibling
     verbose script
4. **Phase-level signal**
   - success output should identify the phase and elapsed time
   - failure output should reveal the seam without forcing an immediate rerun
   - runtime-budget output should also show top-N recent hot spots, including
     unbudgeted phases, so a green budget gate still answers what dominated
     the last run
   - test-runner phases that depend on optional parallelism should print or
     otherwise prove the active mode; a silent serial fallback is an
     operability defect even when tests pass
5. **Escape hatch**
   - keep verbose-on-demand cheap with `VERBOSE=1`, `CI=1`, or a sibling
     `*:verbose` script
6. **Failure detail**
   - quiet success output is healthy only when quiet failure output is still
     actionable
   - a failing executable-spec or test phase should name the failing
     unit/spec/case and include a short `actual`, error, or diff snippet
     without forcing the operator to manually rediscover the failing case
   - a one-time failure replay or captured-output print is acceptable; always
     verbose standing logs are not required

## Slow Test Triage

When the user says the test gate feels slow, do not stop at the orchestrator's
total wall time. Confirm whether the intended parallel runner is active, run
the test runner's native duration report, and separate duplicated proof from
slow-but-necessary behavior coverage.

For pytest-shaped repos, that usually means checking `pytest-xdist` readiness,
serial fallback output, and `pytest --durations` on the standing target set.
Full integration or coverage traces should move to on-demand or a separate
standing phase when a cheaper unit test can preserve the output contract.

Runtime budgets should be profile-aware when samples come from materially
different machines or runners. When the operator has not selected
`CHARNESS_RUNTIME_PROFILE`, create a cheap human-readable machine profile
label with the OS, architecture, and CPU count, such as
`local-linux-x86_64-8cpu`. Avoid slow hardware probing; if profile creation
would block the review, skip it and report the limitation. A single global
threshold is acceptable only when the repo intentionally measures one stable
runner class.

For broad quality or init-repo reviews, run bounded delegated exploration when
the host supports it before finalizing slow-gate advice. Useful lenses are:
fixture economics, parallel critical path, duplicated proof, adapter/runtime
budget policy, and operator signal. Report whether delegated review was
executed or blocked instead of silently replacing it with a same-agent pass.
When the review is executed, name the concrete lens ids in the artifact, for
example `fixture-economics`, `parallel-critical-path`, and
`duplicated-proof`; when blocked, cite the concrete host or tool signal.

## Guardrails

Treat these as prompts for bounded inventory, not as a reason to force one
orchestrator or one test stack onto every repo.

- Do not mark a repo `missing` just because it does not use a particular test
  runner.
- Do not require full observability stacks or permanent verbose logs.
- Do not hide failure diagnostics in the name of compact output.
- Do not call a second implementation or parallel hook healthy if its output
  shape makes the failing seam hard to identify.
