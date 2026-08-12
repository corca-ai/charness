# Issue 595 Runtime Advisory Contract Debug
Date: 2026-08-12

## Problem

`latest_spikes` and runtime-visibility findings were reported without a local,
explicit explanation of why they do not change the runtime-budget exit code.

## Correct Behavior

A latest-only wall-clock spike must remain visible as an advisory, with its
non-failing reason stated at the consumer output; runtime-visibility gaps must
state that their quality-summary reader, rather than this command's verdict,
owns the follow-up.

## Observed Facts

- The live `local-linux-x86_64-36cpu` report has one spike: `pytest-release`
  latest 108044ms over a 105000ms bar, while its recent median is 90895ms.
- The same report has no visibility findings, 27 configured budgets, no missing
  samples, and no enforced violations.
- `render_runtime_summary.py` already carries visibility findings into the
  quality summary; `check_runtime_budget.py` summaries retain both fields.
- D54 records that these are contended wall-clock samples and that the median
  is the deliberately enforced basis.

## Reproduction

- Seed one command with latest 30000ms, median 15000ms, and a 22000ms budget;
  the command returns 0 and reports `latest-spike`.

## Candidate Causes

- A single-sample observation was rendered with no advisory rationale.
- Weak configuration findings looked structurally indistinguishable from an
  ignored verdict input.
- The prior issue did not measure whether a live spike existed.

## Hypothesis

- Repeating the median-based advisory rationale at human output and documenting
  the visibility reader in every structured output will make the non-failing paths intentional;
  disconfirmer: the seeded spike loses visibility or changes the exit code.

## Verification

- `check_runtime_budget.py --repo-root . --detail` confirmed the measured live
  spike, zero violations, and no visibility findings.
- Focused runtime-budget tests exercise the seeded spike's output and exit code,
  plus the structured advisory contracts for spike and visibility findings.

## Root Cause

The gate intentionally uses recent median for its irreversible verdict, but the
latest-only and visibility observations did not state their distinct advisory
contracts across every output mode.

## Invariant Proof

- Invariant: a one-off contended wall-clock sample cannot silently become a
  green enforced result; it is visible and labeled advisory, while a median
  regression remains a failure.
- Producer Proof: `evaluate()` emits the latest-spike record and visibility data.
- Final-Consumer Proof: the budget command prints the latest advisory and the
  runtime summary renders visibility findings with their recommended action.
- Interface-Shape Sibling Scan: `budget_slack_findings` is already an explicitly
  documented advisory; this slice matches that pattern without changing its rule.
- Non-Claims: this does not prove another machine's contention characteristics
  or change #546's missing-sample policy.

## Detection Gap

- runtime-budget human output | a latest-only spike had no stated advisory
  rationale | assertion of its output contract and zero exit.

## Sibling Search

- Mental model: an observable that does not decide a gate needs a named reader
  and a reason for its advisory severity.
- same layer: slack advisory | decision: existing explicit contract, align now | proof: static comparison.
- cross-file: runtime summary visibility renderer | decision: documented existing
  final consumer | proof: source and focused renderer tests.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: runtime signal to budget verdict and quality-summary review output.
- Disproving Observation: seeded spike becomes absent or nonzero after the change.
- What Local Reasoning Cannot Prove: whether another host should use a different budget.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: advisory-versus-verdict distinction and consumer evidence.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

When a gate reports a non-verdict observation, state the reason at its nearest
consumer and test that the observation remains visible without weakening the
actual verdict basis.
