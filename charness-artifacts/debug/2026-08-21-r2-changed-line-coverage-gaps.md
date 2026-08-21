# Debug Review
Date: 2026-08-21

## Problem

The required changed-line producer first returned `blocked` after the contract
wording repair. Three changed source files had five lines that the focused test
population never executed, so the mutation gate could not establish proof.

## Correct Behavior

Every changed branch in a verdict-producing or evidence-producing surface must
have a direct producer/consumer counterexample test before the changed-line
gate is allowed to render clean. The test command must also use an inventoried
path; a guessed nonexistent test path must be treated as a command-surface
failure, not as a harmless empty run.

## Observed Facts

- The explicit-base proof reported `status: blocked`, standing pytest passed,
  and `analyzed_changed_pool_files: 6`.
- Blocking targets were `scripts/critique_adapter_lib.py:189,190,192`,
  `scripts/critique_packet_lib.py:274`, and
  `scripts/release_issue_ledger_evidence.py:242`.
- The uncovered lines are the non-mapping runner refusal, unknown runner-field
  refusal, non-mapping reviewer-runner rendering fallback, and missing
  post-lock release-content evidence refusal.
- The first related verification invocation used the nonexistent path
  `tests/test_reviewer_delivery_integration.py`; `rg --files tests` showed the
  shipped path is `tests/quality_gates/test_reviewer_delivery_integration.py`.
- A parallel source search also guessed `skills/retro`; the checkout owns
  `skills/public/retro`, while `skills/retro` is the flattened installed-layout
  form. That search emitted an `rg` path error and its partial output was not
  used as evidence.
- A gate-discovery query also named absent `.pre-commit-config.yaml`; this repo
  owns its staged gate plan under `scripts/` and hooks rather than that config.
  The missing file error was treated as a failed lookup, not as evidence that
  no gate exists.
- The goal validator was first called with unsupported `--path`; its own help
  exposed the owning spelling `--goal-path`, after which the goal validated
  active with fresh HEAD. Unsupported flags are recorded with wrong paths as
  the same call-boundary failure class.
- The missing tests were added at the existing adapter, packet, and release
  ledger consumer boundaries; focused suites then passed `45` and `26` tests.

## Reproduction

Before the test repair:

`python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha 825b2a4198ae1342a843ccd20f57be7f4e1e0213 --refuse-unestablished`

returned `status: blocked` with the five exact path:line targets above.

## Candidate Causes

- Coverage-scope cause: the default-worker migration added new malformed-input
  and fallback arms without adding direct counterexample tests.
- Consumer-shape cause: tests covered happy/default runner values but not the
  refusal and renderer fallback that decide whether malformed packets stay
  visible.
- Invocation cause: an operator guessed a test path instead of asking the repo
  for the installed path inventory, producing `no tests ran`.

## Hypothesis

The changed-line block is a real missing-invariant gap, not a selector bug: each
targeted line should become executed once its input class is constructed at its
own public or consumer boundary. Disconfirmer: run the focused tests and repeat
the same explicit-base changed-line producer; if any target remains unexecuted,
the mapping or test boundary is still incomplete.

## Verification

- Confirmed: the target lines map to distinct malformed-input/fallback classes
  in the source diff, and existing tests had no matching input assertions.
- Confirmed: adapter refusal, packet renderer fallback, and post-lock carrier
  absence tests now exercise all five targets.
- Confirmed after repair: the same explicit-base producer returned `status:
  clean`, `consumer_returncode: 0`, and `blocking: []`; standing pytest passed.

## Root Cause

The default-runner change was integrated as a semantic feature and its happy
path was tested, but the changed-line proof population was not designed from
the new input partition. The structural gap was treating adapter validation,
packet rendering, and release-ledger evidence as separate test concerns rather
than one producer-to-verdict contract whose malformed classes must be measured.

## Invariant Proof

- Invariant: a changed-line verdict is valid only when every changed pool line
  is executed by the focused producer and its final consumer remains fail-closed.
- Producer Proof: the explicit-base changed-line command named the exact
  blocking path:line targets and the focused tests were added against them.
- Final-Consumer Proof: the changed-line consumer refuses a verdict when any
  mapped line is uncovered; standing pytest alone cannot discharge this floor.
- Interface-Shape Sibling Scan: adapter validation, packet rendering, and
  release-ledger evidence all convert malformed input into operator verdicts.
- Non-Claims: this receipt does not prove fresh-eye approval, external host
  behavior, release publication, or issue closure.

## Detection Gap

- Changed-line gate: it fired correctly, but only after integration; the missing
  tests were the gap. Smallest fix: add one counterexample per blocking target
  and rerun the same explicit-base producer.
- Focused suites: happy-path tests existed but did not enumerate malformed
  runner/evidence classes. Smallest fix: assert the exact refusal/fallback at
  the final consumer boundary.
- Operator command surface: a guessed path produced no tests. Smallest fix:
  inventory with `rg --files` before composing test commands and record a
  nonzero/no-tests result as a command failure.

## Sibling Search

- Mental model: a proof surface can be green while a newly added input class is
  never presented to its consumer.
- same layer: `tests/quality_gates/test_reviewer_tier_policy.py` and
  `tests/test_critique_prepare_packet.py` | decision: same bug, fix now |
  proof: focused tests exercise adapter/packet malformed classes.
- abstraction up: `tests/quality_gates/test_release_issue_ledger.py` |
  decision: same bug, fix now | proof: post-lock missing-carrier counterexample.
- cross-file: `scripts/check_skill_contracts.py` and
  `scripts/validate_critique_artifacts.py` | decision: same class,
  diagnostic-only for this slice | proof: static changed-pool scan; their
  changed lines are not among the blocking targets.

## Seam Risk

- Interrupt ID: r2-changed-line-coverage-gaps-2026-08-21
- Risk Class: none
- Seam: changed source branch -> focused test population -> mutation/changed-line verdict
- Disproving Observation: repeat the explicit-base producer after the tests;
  all six changed files are mapped and no blocking target remains.
- What Local Reasoning Cannot Prove: provider-hosted execution or external
  release behavior.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

For every proof-surface change, derive the input partition from the changed
branches before broad quality runs: default, malformed, missing, and fallback
consumer shapes. Run the explicit-base changed-line producer before standing
or release lanes. For command paths, resolve with `rg --files` or the owning
planner instead of guessing; a wrong path is a failed boundary that must be
recorded and corrected.

Additional command-boundary smells: the semantic review fan-out exposed the
same class above the test selector:

- The first worker fan-out used a provider-invalid JSON Schema (`const` without
  a declared string type). All three attempts were recorded as non-delivery;
  adding the type and validating the schema before retry fixed the provider
  boundary.
- Delivery inspection first guessed `begin` and `findings-received` CLI
  subcommands; `reviewer_delivery.py --help` showed the owning names are
  `start`, `transition`, and `findings`.
- A ledger readback first guessed three `/tmp/*delivery.json` names instead of
  inventorying the actual `*-ledger.json` paths.
- `findings` was first called with unsupported `--signal`; the CLI help showed
  that findings has no signal field.
- Round persistence first supplied a new window id against an old snapshot;
  the snapshot-id mismatch was correctly refused, then a repo-root snapshot
  was created for the actual round record.

These were not harmless operator typos. Each guessed path, flag, or schema
shape could have produced a false “nothing returned” or a falsely unbound
review. The prevention is one inventory/help/schema smoke step before fan-out,
then typed receipts and actual CLI state transitions after delivery.

Follow-up proof found three uncovered worker-delivery refusals in
`scripts/critique_reviewer_evidence.py`. Standing pytest passed, but the
changed-line gate correctly blocked. Direct artifact-boundary counterexamples
were added; rerun the exact-base proof to verify them.
