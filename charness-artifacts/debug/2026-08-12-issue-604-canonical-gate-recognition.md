# Issue #604 Canonical Gate Recognition Debug
Date: 2026-08-12

## Problem

The CI/local parity defaults recognize `bash scripts/run-quality.sh` but not
the `./scripts/run-quality.sh` spelling that Charness scaffolds and documents.
An unrecognized job has no canonical anchor, so its later quality steps evade
the parity-issue bucket.

## Correct Behavior

Default recognition identifies the Charness-owned runner when CI invokes it as
`bash scripts/run-quality.sh`, `bash ./scripts/run-quality.sh`, or
`./scripts/run-quality.sh` behind an optional environment prefix. It does not
require repositories to ship or use that runner.

## Observed Facts

- GitHub #604 records the three missed spellings and the red-to-green masking
  direction; it has no comments.
- The default tuple has only `\\bbash\\s+scripts/run-quality\\.sh\\b`.
- `--require-canonical-gate-match` is separately opt-in; ordinary reports only
  place unmatched jobs in `jobs_without_canonical_gate`.
- The user selected default expansion only as recognition, not as a new
  requirement that every consumer use `run-quality.sh`.

## Reproduction

- A workflow with `./scripts/run-quality.sh --read-only` followed by a required
  command has no canonical anchor under the current default tuple.
- A workflow with no matching runner continues to report an advisory unmatched
  job and exits zero unless the caller explicitly supplies
  `--require-canonical-gate-match`.

## Candidate Causes

- The default regex requires `bash` and omits the leading `./` form.
- Default-pattern tests cover only `npm run verify` fixtures.
- The report's advisory unmatched bucket can be mistaken for a requirement.

## Hypothesis

- Confirmed: extending only the exact run-quality alternatives will anchor the
  shipped invocation forms without changing unmatched-job exit behavior;
  disconfirmer: test an unrelated no-runner workflow before and after the edit.

## Verification

- `python3 -m pytest tests/quality_gates/test_inventory_ci_local_gate_parity.py tests/quality_gates/test_documented_subcommands.py -q` — 67 passed.
- The CLI fixture anchors every shipped runner spelling and reports the following
  required step as a parity issue.
- The no-runner fixture exits zero even with `--require-empty-parity-issues`;
  only `--require-canonical-gate-match` changes that advisory state into a refusal.
- Fresh-eye round 1 found direct-path matching could anchor an `echo`, test,
  assignment, or comment mention. The repair confines default matches to shell
  command positions and adds end-to-end non-invocation refusal controls.
- Fresh-eye round 2 found `.sh.bak` crossed a word boundary. The repair accepts
  only a shell-token delimiter after the exact runner name and adds `.bak` and
  `.shx` controls; this capped round-2 repair is accepted-unreviewed.

## Root Cause

The tuple encoded one shell spelling rather than the portable command shapes
that Charness itself produces. Its tests did not exercise the tuple directly.
The first repair also treated path mentions as invocations until fresh-eye review
showed the command-position boundary was necessary; its `\\b` suffix also
accepted dotted filename extensions until round 2 restricted token termination.

## Invariant Proof

- Invariant: recognizing a command does not require its use; unmatched jobs stay advisory unless an opt-in refusal flag is present.
- Producer Proof: command-position alternatives recognize exact shell-prefixed and direct runner command words without changing opt-in refusal flags.
- Final-Consumer Proof: isolated workflow fixtures expose post-run required commands as parity issues, while echo/test/assignment/comment and `.bak`/`.shx` mentions remain unmatched and refuse only with the opt-in flag.
- Interface-Shape Sibling Scan: the no-runner control preserves `jobs_without_canonical_gate`; the maintainer reference now states the non-requirement and release-note obligation.
- Non-Claims: no consumer CI, hosted workflow, release, or issue closure has run.

## Detection Gap

- Default-pattern suite | no test exercised runner alternatives, command-position semantics, or filename termination | added exact positive forms, non-invocation counterexamples, and an unrelated no-runner control.

## Sibling Search

- Mental model: default recognition is confused with a universal enforcement requirement.
- same layer: `--require-canonical-gate-match` remains the explicit enforcement switch | decision: preserved | proof: the no-runner CLI control stays green under parity-issue-only enforcement.
- cross-file: maintainer-local enforcement reference and plugin export | decision: synchronized the recognition/non-requirement contract | proof: packaging validation passed and the plugin CLI executed its current workflow inventory.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: default regex selection to CI workflow parity verdict
- Disproving Observation: a no-runner workflow becomes a hard failure with no opt-in refusal flag.
- What Local Reasoning Cannot Prove: existing consumer CI outcomes after the shipped default changes.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: #604 changes a shipped proof-surface default.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Keep behavior-level tests for every supported runner invocation, non-invocation
counterexample, and non-requirement control, not merely regex text assertions.
The floor expansion must be called out in the next release notes rather than
retroactively claiming that prior consumers were covered.
