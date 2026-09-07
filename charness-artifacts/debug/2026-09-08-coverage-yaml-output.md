# Debug Review: coverage-yaml-output
Date: 2026-09-08

## Problem

The retained coverage-ready-timing stdout begins `ok\nstatus: clean...`, but
historical bytes fail `yaml.safe_load`; downstream `_load_mapping` therefore
returns `None`. The question was whether current source still produces this
defect. No production repair was made.

## Correct Behavior

Given coverage output selected for a task, when the producer completes, the
consumer should receive one parseable YAML mapping. A malformed stream must
not be treated as a task or coverage receipt.

## Observed Facts

- Historical HEAD was `d8d05d57e312fa5206007256f0fc182ebc9c39a2`.
- Historical retained raw output is malformed YAML and breaks the real
  `scripts/task_run/task_run_changed_line.py` `_load_mapping` path.
- Current `gate.main` with retained selection, a stubbed successful producer,
  and the actual imported consumer emitted parseable YAML; adding the timer's
  exact `functools`/import wrapping did too.
- Historical direct consumer over retained coverage emitted parseable
  `ok: true...`. Current `_run_command` with child `printf 'ok\n'` emitted no
  outer stdout and retained the child bytes in `result.stdout`. Current and
  historical `recommendation`/`expand_targets` emitted no stdout.
- These controls do not reproduce the full historical producer environment;
  they do not disconfirm every producer defect. Current-source attribution is
  unproven, not repaired.
- The focused baseline `tests/quality_gates/test_release_changed_line_coverage.py`
  passed 37 tests in 2.33s on parent source `2b810b0a0e`; its producer stubs
  cannot establish whole historical full-path behavior.

## Reproduction

- Historical retained bytes fail `yaml.safe_load`; the same bytes cause the
  real downstream `_load_mapping` to return `None`. Scoped current and
  historical capture controls parse successfully, so a full producer replay
  was not established.

## Candidate Causes

- An environment-specific file-descriptor writer or producer-side capture
  path could have emitted the malformed historical bytes; this remains a
  hypothesis, not a located cause.
- Consumer parsing is not the demonstrated cause: direct historical consumer
  parsing of retained coverage succeeded.

## Hypothesis

- If the historical producer environment contains a writer/capture path absent
  from the controls, reproducing that environment should yield the malformed
  prefix; disconfirm with a full instrumented replay that validates captured
  output before parsing. No such replay or `strace` is warranted without a
  more precise target.

## Verification

- Still-candidate/unproven. Scoped controls were parseable, but they omit the
  full historical producer environment and therefore cannot locate or exclude
  the writer.

## Root Cause

No causal writer was established. The closed prior incident is an unproven
producer-output result, not an active specification handoff. The only stable
finding is that retained historical output is malformed while the tested
scoped paths are parseable.

## Invariant Proof

- Invariant: producer output handed to the final consumer must be one parseable
  YAML mapping.
- Producer Proof: historical retained bytes violate it; current scoped controls
  satisfy it, without full producer-environment coverage.
- Final-Consumer Proof: historical direct consumer parses retained coverage;
  changed-line receipt loading fails closed on unreadable output.
- Interface-Shape Sibling Scan: the Rust wrapper has static
  capture-then-YAML similarity only; no defect was observed and no action is
  justified.
- Non-Claims: no current-source attribution, full-path equivalence, task or
  coverage verdict, or production repair is claimed.

## Detection Gap

- The focused tests stub the producer and did not fire on the historical
  full-path output. No task/coverage verdict is trusted when stdout is
  malformed; downstream `_load_mapping` already fails closed. Future timing
  reuse should validate captured output before treating it as a receipt.

## Sibling Search

- Mental model: producer-only or scoped capture evidence is not end-to-end
  producer-environment proof; a consumer boundary that fails closed is an
  intentional safety seam.
- same layer: `scripts/task_run/task_run_changed_line.py::_load_mapping` and the
  changed-line receipt path | decision: intentional plain-text or non-rendering boundary |
  proof: unreadable output yields `None`, not a trusted verdict.
- abstraction up: Rust wrapper capture-then-YAML shape | decision:
  same class, diagnostic-only for this slice | proof: static similarity with no observed
  defect.
- specialization down: `scripts/mutation/release_changed_line_coverage.py::_run_command` | decision: intentional plain-text or non-rendering boundary | proof: child bytes captured in a scoped command control.
- mental-model siblings: the timing harness assumed process success implied parseable output | decision: same class, diagnostic-only for this slice | proof: retained malformed bytes; no shipped defect located.
- cross-file: `scripts/task_run/task_run_changed_line.py` is the final refusal boundary.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: the full historical producer environment
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

This resolved record authorizes no production repair. The required `impl` token
is inactive lifecycle metadata; the seam-index schema has no terminal `none`.
Validate captured output before
reusing timing as a receipt; if a future investigation gains a precise writer
target, use a full instrumented replay before assigning current-source cause.

## Evidence Disposition

- Report Identity: probe/2026-09-08-reading-coverage-cost.json:coverage-yaml-output#sha256:f90a9c4cb6603944b02e3ef6a4db7159b41941d8ec9b6ef51d9e1a5fec3e8890
- Reported Findings: 1
- Dispositioned Findings: YAML-1
- Missing Findings: none
- Evidence Digest: sha256:e8d14d37e310822dd8de7e89657896ebfbb8c55ae05d91186a9456b4220e1c2d
- Report Source: charness-artifacts/probe/2026-09-08-reading-coverage-cost.json
- Report Source SHA256: f90a9c4cb6603944b02e3ef6a4db7159b41941d8ec9b6ef51d9e1a5fec3e8890

## Adversarial Verification

- Finding: YAML-1 | source: charness-artifacts/probe/2026-09-08-reading-coverage-cost.json | expected: one parseable YAML mapping | stimulus: retained raw report bytes plus scoped current and historical capture controls | disposition: unproven | observed: historical retained bytes are malformed YAML; scoped controls are parseable and the causal writer is unlocated | proof: executable fixture | handoff: none | next move: none | receipt: none | receipt sha256: none
