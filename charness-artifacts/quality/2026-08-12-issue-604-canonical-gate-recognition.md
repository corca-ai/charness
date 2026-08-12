# Quality Review
Date: 2026-08-12
Title: Issue 604 canonical gate recognition

## Scope

Target boundary: #604's default CI/local parity recognition for Charness-owned
`run-quality.sh` invocation forms.

Ambient repo findings: consumer CI failures, release publication, and broader
canonical-gate taxonomy are not part of this local proof-surface repair.

## Surface Contract Review

- semantic coverage: `observed` — default tuple selection and CLI parity output are exercised.
- surface: CI/local gate parity inventory supplied to a consumer operator
- owner: quality's canonical-gate pattern tuple owns default command recognition
- projections: source library, inventory CLI output, maintainer reference, plugin export
- state scope: matching runner forms and a no-runner workflow with no opt-in refusal
- transitions: command recognized, last anchor selected, later required step classified, or unmatched job reported advisory
- proof boundary: isolated workflow fixtures and focused deterministic tests; no hosted workflow executes
- unexamined axes: arbitrary consumer command semantics and installed consumer configuration

## Current Gates

- `--require-empty-parity-issues` enforces only post-anchor parity findings.
- `--require-canonical-gate-match` remains the separate opt-in for repositories that require every runnable job to name a recognized gate.

## Runtime Signals

- runtime source: focused pytest receipt; timing capture is missing because this cheap parser path has no configured timing capture. <!-- reproduction-source -->
- runtime hot spots: none observed; broad quality was not required to prove the tuple behavior.
- coverage gate: parity inventory and documented-subcommand suites pass (67 tests).
- evaluator depth: deterministic-gates-only; Cautilus is not approved and would not improve command-pattern proof.

## Healthy

- Existing `npm`, `make`, and run-verify default recognition is unchanged.
- Repositories that do not use `run-quality.sh` are still advisory unless they opt into canonical-match refusal.

## Weak

- The default expansion newly judges consumer CI that previously escaped parity analysis; that is deliberate floor growth, not backward-compatible silence.

## Missing

- No evidence establishes whether any external consumer will receive a new finding.

## Deferred

- The next authorized release must include a note that direct and env-prefixed `run-quality.sh` CI forms can now produce parity findings.

## Advisory

- structural review result: evidence: the focused parity inventory and documented-subcommand suites pass 67 tests; fixtures cover every supported form and the no-runner control.
- prose review result: `references/adapter-gate-review.md` supports a narrow structural fact; the change recognizes only an exact owned command rather than promoting arbitrary prose into a hard rule.

## Delegated Review

- Delegated Review: executed — round 1 caught command-mention overmatching and round 2 caught dotted filename suffix overmatching; both were repaired. The capped round-2 repair is accepted-unreviewed and recorded in `charness-artifacts/critique/2026-08-12-issue-604-canonical-gate-critique.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not applicable; parser fixtures are cheap and bounded.

## Commands Run

- Focused parity inventory and documented-subcommand suites — 67 passed. <!-- reproduction-source -->
- Ruff and `git diff --check` passed for the initial changed source and tests.

## Recommended Next Quality Moves

- active canonical recognition — capability_needed=honest parity denominator; next_center=default tuple; transformation=recognize exact Charness runner forms without changing opt-in refusal flags; proof_boundary=CLI workflow fixtures; enforcement_posture=existing-gate-reuse.
- passive consumer migration — capability_needed=consumer-specific CI disposition; next_center=each consumer workflow; transformation=review new parity findings when updating; proof_boundary=consumer run; enforcement_posture=no-gate because Charness cannot infer consumer intent.

## History

- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
