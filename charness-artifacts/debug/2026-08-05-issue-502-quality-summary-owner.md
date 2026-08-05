# Issue #502 Quality Summary Owner Debug
Date: 2026-08-05

## Problem

The quality gate's terminal summary has a runtime renderer, but its contract is
still repeated as hand-written prose in many tests. A format change therefore
looks like assertion sanding instead of a change to one owned interface.

## Correct Behavior

Given a quality receipt, when the runner prints its final line, one renderer
owns the semantic fields and tests prove those fields through a small contract
surface. A reader retaining only the final line must still get the verdict and
the actionable failing or unproven subjects.

## Observed Facts

- `scripts/run-quality.sh:509-558` collects counts, adverse subjects, recovery
  paths, and unproven subjects, then delegates rendering to
  `scripts/proof_receipt.py:209-224`.
- The issue's reported 17 assertions are not the current full match count:
  `rg -n 'Quality summary:|passed, .*failed|FAILED:' tests/quality_gates`
  returns 36 matching lines across five files, including comments and the
  renderer tests. Exact summary-shape assertions remain spread across runner,
  aggregate, gate-summary, and receipt tests.
- A structured receipt already exists: `scripts/proof_receipt.py:30-68`
  serializes `status`, `effective_exit_code`, measured scope, adverse subjects,
  recoveries, and unproven subjects.

## Reproduction

- Run `rg -n -C 3 'Quality summary:|passed, .*failed|FAILED:' tests/quality_gates`
  and inspect the repeated exact prose. A focused runner change requires edits
  in several test modules even though `render_quality_summary` is the producer.
- The existing tail-shaped behavior probe is
  `tests/quality_gates/test_gate_summary_names_failures.py:33-73`; it proves
  the delivered line but does not make the structured receipt the shared test
  contract.

## Candidate Causes

- The renderer was centralized for runtime output, but test consumers retained
  exact strings from earlier runner-owned formatting.
- No test helper or field-level assertion boundary distinguishes semantic
  receipt fields from intentionally user-facing final-line formatting.
- The JSON receipt is opt-in and not required by the runner's default test
  harness, so tests naturally keep parsing stdout prose.

## Hypothesis

- If runner tests assert parsed receipt fields and reserve one delivery test for
  the exact final line, then a renderer format change will have one intentional
  presentation assertion instead of many copied strings. Disconfirmer: inventory
  all summary assertions and run the focused suite after the smallest helper
  migration; repeated exact-shape consumers outside the delivery contract would
  falsify the claim.

## Verification

- Confirmed: the causal reviewer independently identified the same producer/test
  ownership gap; the quality reviewer found no blocker; and the focused suite
  passed 71 tests after runner consumers migrated to the receipt helper.

## Root Cause

The semantic producer and the test contract have different owners: production
rendering is centralized, while tests still encode the historical prose at
multiple call sites. The five-whys chain is therefore a contract-boundary gap,
not evidence that the renderer itself currently emits the wrong verdict.

## Invariant Proof

- Invariant: the receipt fields selected by the runner must reach the final
  stdout summary without semantic loss, while tests may pin presentation only at
  the delivery boundary.
- Producer Proof: `run-quality.sh:509-558` constructs the receipt arguments and
  `proof_receipt.py:209-224` renders them.
- Final-Consumer Proof: `test_gate_summary_names_failures.py:61-73` reads the
  actual final `Quality summary:` line, including failure name and recovery path.
- Interface-Shape Sibling Scan: the same receipt module renders closeout
  verdicts (`proof_receipt.py:227-242`), and `run_slice_closeout.py` consumes its
  structured result; this slice must not conflate quality prose with closeout.
- Non-Claims: no claim about every external CI log consumer, installed plugin,
  or provider-specific truncation behavior is proven locally.

## Detection Gap

- Existing pytest and summary probes fired when a prose string changed, but
  their failure mode required hand-editing many copies and could not identify
  which assertions were semantic versus presentation. Smallest detector:
  centralize field assertions and retain one explicit final-line delivery test.

## Sibling Search

- Mental model: output prose is treated as the interface even when a structured
  receipt already owns the semantics.
- same layer: `tests/quality_gates/test_quality_runner.py` and
  `test_quality_runner_runtime_aggregate.py` | decision: same class, inspect
  now | proof: static scan plus local test fixtures.
- abstraction up: `scripts/proof_receipt.py` closeout renderer | decision:
  intentional separate surface | proof: source and focused tests.
- cross-file: `tests/quality_gates/test_gate_summary_names_failures.py` | decision:
  same class, fix or preserve as the one delivery-boundary proof | proof: local
  subprocess payload.

## Seam Risk

- Interrupt ID: issue-502-quality-summary-owner
- Risk Class: none
- Seam: runner receipt arguments -> proof renderer -> truncated stdout reader
- Disproving Observation: none yet
- What Local Reasoning Cannot Prove: external log viewers preserve and expose
  the final line as assumed.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Make the structured receipt the default test seam, keep one explicit final-line
delivery assertion for truncation/operability, and document the boundary so
future format changes update the owner rather than copied consumer prose.
