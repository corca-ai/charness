# Quality Gates

A repo-owned CLI should usually have:

- parser smoke tests for representative commands
- version probe tests for `version` and any supported top-level `--version`
  alias
- `--help` smoke for stable public subcommands
- no-side-effect `--help` probes for mutating subcommands such as `apply`,
  `init`, `install`, `update`, `reset`, and `delete`
- option-looking positional rejection probes such as `--help` or
  `--not-an-instance` when a mutating command requires a positional argument
- dry-run or plan probes for lifecycle mutations, or an explicit waiver when
  preview is not meaningful
- side-effect watch fixtures for filesystem writes, service/unit materialization,
  subprocess runners, and persisted manifests
- JSON-shape tests when agents consume the output
- JSON-shape tests for command discovery output when wrappers or agents probe
  the command registry
- redaction tests for external-capability CLIs that exercise stdout, JSON
  payloads, bridge logs, and debug logs without exposing raw tokens, raw request bodies, or full external identifiers
- file-mutation tests for install/update/reset commands
- validation for any persisted lock or manifest schema
- command-docs drift checks that compare no-side-effect `--help` output with
  first-touch install, update, doctor, reset, or uninstall docs
- cheap syntax smoke such as `py_compile` for Python entrypoints

Language baselines still apply to CLI repos:

- Python CLI: `ruff check` with `C90` enabled, plus one honest type checker
  (`mypy` or `pyright`)
- JavaScript/TypeScript CLI: `eslint` with a standing `complexity` rule, plus
  `tsc --noEmit` when TypeScript is present

## Lint Gate Before Slice-Complete

A created CLI inherits the same push-time-rejection cost shape any `impl` slice
carries: tests pass locally, the commit lands, and the push-time hook rejects
on lint. Run the repo's standing lint gate against the new CLI source before
declaring the slice complete instead of waiting for the hook.

Do not invent a parallel rule here. The detection and closeout shape are owned
by `impl`:

- survey the gate with `skills/public/impl/scripts/survey_verification.py`
  (`lint_gate.detected` / `lint_gate.command`)
- record the result in the `Lint Gate` closeout field whose states
  (`ran-pass`, `ran-fail-fixed`, `ran-fail-deferred`, `not-detected`,
  `skipped <reason>`) are defined in
  `skills/public/impl/references/verification-ladder.md` "Lint Gate Closeout
  Shape"

The discipline is disclosure-before-commit, not a new hard gate; the repo's
own pre-push/pre-commit hook still owns hard-block enforcement.

When the CLI owns lifecycle state, test both:

- happy path
- degraded or manual path

Quality review should ask:

- do stable public subcommands expose a no-side-effect `--help` contract
- do mutating commands reject option-looking positional values before touching
  local or host-visible state
- do lifecycle mutations expose dry-run/plan behavior, or is the waiver
  concrete enough to review
- does the CLI keep a stable answer for `version`, `--version`, and `-v`
  instead of letting those drift by parser accident
- is machine-readable command discovery distinct from help text when agents or
  wrappers need to probe the surface
- if a worker CLI touches an external system, are preflight status, host-only
  executor boundaries, operation scopes, and audit-safe fields explicit
- is binary health distinct from repo or install readiness
- if local plugin or skill discoverability matters, does it have its own
  readiness probe
- does `doctor` stay read-only
- does `update` report drift honestly
- does the CLI keep one source of truth for installed state
- can a later agent tell what changed without re-running everything
- are stable command names, options, and lifecycle invariants protected by a
  repo-local command-docs contract instead of recurring manual review

Command-docs drift gates should stay narrow. Check command existence, stable
option anchors, and crisp invariants such as "doctor is read-only" or
"delete-checkout requires an explicit flag." Leave broad documentation style,
progressive disclosure, and naming judgment to human or agent review.

## Release and Verification-Hook Safety

Two operator-trust failure modes appear repeatedly in repo-owned CLIs that
ship release pipelines, pre-push hooks, or broad verification commands. Both
deserve standing gates separate from parser smoke:

- **Stale generated-artifact failures must print the exact repair command.**
  A check that says "release notes are stale" or "manifest does not match
  source" without naming the script or command to run again is a trust hazard:
  the operator (or agent) has to grep the repo to find the producer. The
  failure message should always include the literal command to regenerate the
  artifact, ideally copy-pasteable, alongside the stale-state explanation.
  Test that the failure path emits the producer command, not only the
  diagnostic.
- **Broad verification hooks must not mutate the caller's worktree, index, or
  `HEAD`.** Pre-push, pre-release, or aggregate `verify` commands that run
  the full test/lint/generate fan-out can easily touch tracked files,
  regenerate artifacts in place, or move `HEAD` while the operator is mid-push.
  That looks like silent corruption from the operator's side. Guard the
  surface: prefer a read-only mode for hooks (`run-quality.sh --read-only`,
  `verify --no-write`, or a disposable checkout / git worktree for any
  generating step). Ship a fixture that asserts the broad verification
  command leaves `git status` clean and `HEAD` unchanged when it succeeds.

For release-publishing commands that need to write, publish from a disposable
checkout and target explicit refspecs such as `HEAD:main`; then verify the
remote branch and tag SHA before reporting success. Update or version
commands should not report an available update after they just installed
that same version — record the resolved version in the runtime state the
update check consults, not only in install logs.
