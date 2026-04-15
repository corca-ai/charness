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

Use `scripts/inventory_standing_gate_verbosity.py` when a repo keeps a standing
hook, hook runner, or verify chain.

## Inventory Axes

Review these five axes and classify each as `healthy`, `weak`, `missing`, or
`not_applicable` when the repo genuinely does not use that shape:

1. **Test-runner reporter**
   - `node --test` should pin
     `--test-reporter=dot --test-reporter-destination=stdout`
   - `pytest` should usually run with `-q`
   - `jest` / `vitest` should usually prefer a dot reporter in the standing gate
   - `go test -v` is usually a smell in the default gate
   - `cargo test -- --nocapture` is usually a smell in the default gate
2. **Orchestrator output mode**
   - grouped output matters most when an orchestrator fans out commands in
     parallel
   - `lefthook` with `parallel: true` should not leave success logs to raw
     interleaving by default
3. **Per-gate chatter**
   - noisy tools such as `pylint`, `coverage report`, or `specdown` should use
     their quietest honest defaults in the standing gate
   - verbose troubleshooting output should move behind an env flag or sibling
     verbose script
4. **Phase-level signal**
   - success output should identify the phase and elapsed time
   - failure output should reveal the seam without forcing an immediate rerun
5. **Escape hatch**
   - keep verbose-on-demand cheap with `VERBOSE=1`, `CI=1`, or a sibling
     `*:verbose` script

## Guardrails

Treat these as prompts for bounded inventory, not as a reason to force one
orchestrator or one test stack onto every repo.

- Do not mark a repo `missing` just because it does not use a particular test
  runner.
- Do not require full observability stacks or permanent verbose logs.
- Do not hide failure diagnostics in the name of compact output.
- Do not call a second implementation or parallel hook healthy if its output
  shape makes the failing seam hard to identify.
