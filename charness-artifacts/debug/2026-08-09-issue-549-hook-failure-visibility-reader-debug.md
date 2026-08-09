# Hook Failure Visibility Reader Debug
Date: 2026-08-09

## Problem

The exported `setup` guidance defines how a consumer Lefthook command should
keep a failure actionable, but no executable setup surface reads the consumer's
actual `lefthook.yml`. A repo can therefore receive the contract while omitting
`fail_text` or advertising a log its command never writes, and setup reports no
corresponding fact.

## Correct Behavior

When setup inspects a repo with `pre-commit` or `pre-push` Lefthook commands, its
structured output names each command and every mechanically observable contract
gap. A statically well-shaped command is not reported as passing: final message
ordering, log provisioning, and an intentional failing-hook run remain explicit
live-verification requirements.

## Observed Facts

- `scripts/run-quality.sh` persists its own failing phase logs and names the
  failing label in the final summary line.
- `skills/public/setup/references/hook-failure-visibility.md` exports the consumer
  contract and `setup/SKILL.md` routes a detected Lefthook config to it.
- `scripts/setup_adapter_inspect_lib.py` detects only the manager's presence for
  worktree-adapter advice.
- `tests/quality_gates/test_setup_hook_failure_guidance.py` checks prose and
  mirroring only; it never presents an actual consumer hook command to a reader.

## Reproduction

Create a repo with `lefthook.yml` containing a `pre-push.commands.quality.run`
entry but no `fail_text`, then run
`python3 skills/public/setup/scripts/inspect_repo.py --repo-root <repo>`. Before
this repair, the payload contains no command-level failure-visibility finding.

## Candidate Causes

- The failure-log mechanism was expected to apply automatically to every
  consumer command — disconfirmed: it is owned by `run-quality.sh` only.
- The exported reference was expected to be executable policy — disconfirmed:
  it is prose and explicitly refuses to rewrite consumer configuration.
- Setup detection stopped at hook-manager presence and never reconciled the
  detected configuration with the exported contract — confirmed.

## Hypothesis

If the existing setup inspector parses the two supported Lefthook config paths
and reconciles each `pre-commit`/`pre-push` command's `fail_text`, next-action,
output filter, and advertised-log redirect, then concrete omissions become
actionable in the normal setup bootstrap. A well-shaped static result must still
say live verification is required. Disconfirmer: a missing or mismatched field
produces no exact command finding, or a well-shaped fixture produces `pass` or
`clean`.

## Verification

- Focused setup inspection tests pass over missing fields, invalid YAML,
  mismatched and temporary logs, output pipelines, fd-redirection order, and
  valid static controls.
- Compound commands and pipelines now stop at
  `manual-reconciliation-required`; quoted and commented operator text does not
  become a shell verdict.
- Both the source and exported-plugin `inspect_repo.py` entrypoints carry the
  reader verdict for broken and statically well-shaped consumer fixtures.
- The real bootstrap payload names `pre-push.commands.quality` and
  `fail-text-missing`; a well-shaped fixture remains
  `live-verification-required` rather than pass or clean.

## Root Cause

The mechanism, consumer contract, and setup detection were implemented as three
independent layers. The detector classified the hook manager only to recommend a
worktree adapter, so no producer ever supplied command-level facts to the setup
inspector and no final consumer could render the contract gaps.

## Invariant Proof

- Invariant: setup that detects a supported consumer hook configuration reports
  its mechanically observable failure-visibility gaps without claiming the
  hook's live failure behavior was observed.
- Producer Proof: real YAML fixtures exercise exact field gaps and shell
  redirection order in the reader.
- Final-Consumer Proof: source and plugin `inspect_repo.py` subprocess fixtures
  expose the reader's `action-required` and `live-verification-required` states.
- Interface-Shape Sibling Scan: Husky and simple-git-hooks use different
  configuration shapes and remain explicitly outside this Lefthook reader.
- Non-Claims: no static reader can prove final terminal ordering, directory
  provisioning, or the result of an intentional failing hook.

## Detection Gap

- setup hook-manager detection | manager presence only | reconcile supported
  command fields into the normal inspection payload.
- exported reference tests | prose existence only | add real configuration
  fixtures with deliberate contract failures.

## Sibling Search

- same layer: `setup_adapter_inspect_lib._detect_hook_manager` | decision: keep
  its worktree-adapter purpose; add a separate failure-visibility producer.
- abstraction up: `setup_inspect_lib.build_setup_inspection_payload` | decision:
  expose the producer's structured facts in the default setup inspection.
- specialization down: `hook-failure-visibility.md` | decision: document the
  reader and its live non-claims.
- adjacent managers: Husky/simple-git-hooks | decision: out of scope because the
  exported contract is Lefthook-specific.

## Seam Risk

- Interrupt ID: issue-549-hook-failure-visibility-reader
- Risk Class: operator-visible-recovery
- Seam: consumer Lefthook config -> setup inspection -> operator live check.
- Disproving Observation: a broken fixture is named exactly while a well-shaped
  fixture still requires live verification.
- What Local Reasoning Cannot Prove: the consumer's installed Lefthook terminal
  ordering and filesystem behavior.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md

## Prevention

Make command-level visibility a structured field of the setup inspector, keep
static gaps distinct from live proof, and pin both with real consumer config
fixtures.
