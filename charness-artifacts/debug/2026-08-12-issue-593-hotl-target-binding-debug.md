# Issue #593 HOTL Target Binding Debug
Date: 2026-08-12

## Problem

The HOTL disposition floor judged every syntactically matching `HOTL #N:` line
in a closeout body, including quoted discussion about issues this carrier was
not closing, causing false refusal before the GitHub write.

## Correct Behavior

Given carrier targets, when a HOTL entry names another issue, then it is inert;
matching targets remain subject to the typed-status floor and bare `HOTL:` is
valid shorthand only for one target.

## Observed Facts

- #593 is open with no comments; its recorded failure is a quoted `HOTL #77:`
  blocking a close of #800.
- Behavioral verdict already accepts the carrier number list and filters target
  references; HOTL did not.
- `verify-closeout` and `close-with-comment` each already own invoked numbers.

## Reproduction

Run the helper or either carrier with `- HOTL #77: not verified` while closing
only `#800`; before this repair the floor reported an undispositioned entry for
#77.

## Candidate Causes

- The shared HOTL function omitted a `numbers` parameter when it was extracted.
- Existing tests proved status vocabulary but not target-bound carrier behavior.
- The manual carrier's direct mutation path reused the target-free helper call.

## Hypothesis

- Confirmed: thread the carrier numbers into the HOTL owner and bind targeted
  lines like behavioral verdicts; disconfirmer: an untyped `HOTL #77:` still
  blocks a close of only `#800`, or an untyped matching `HOTL #800:` passes.

## Verification

- `python3 -m pytest tests/quality_gates/test_issue_closeout_rung1_floors.py
  tests/quality_gates/test_issue_close_comment_floor.py -q` — 34 passed.
- Helper, actual bundled `verify-closeout`, and actual manual close-comment
  floor regressions cover unrelated, matching, and shorthand target shapes.
- Critique added the direct carrier handoff and combined-target counterexamples;
  the same focused suite then passed 35 tests.

## Root Cause

The HOTL parser had no caller-owned target identity, unlike its behavioral
verdict sibling. The carrier knew the numbers but did not pass them across the
floor boundary.

## Invariant Proof

- Invariant: a disposition floor judges only the closeout issues its carrier names.
- Producer Proof: both verifier and close-comment carrier pass their invoked numbers.
- Final-Consumer Proof: bundle and manual-floor regressions prove target binding.
- Interface-Shape Sibling Scan: plugin projections match source; behavioral verdict
  already uses the same target-intersection boundary.
- Non-Claims: no GitHub close, hosted readback, or provider mutation occurred.

## Detection Gap

- HOTL floor | parser-only tests lacked carrier target binding | add bundle and manual-carrier regressions.

## Sibling Search

- Mental model: a shared parser can judge text without the caller identity that
  gives its target syntax meaning.
- same layer: behavioral verdict target parsing | decision: retain its
  intersection rule | proof: it already receives `numbers` from verify-closeout.
- cross-file: plugin issue scripts | decision: synchronize source | proof: mirror
  drift gate passed for all three changed projections.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: carrier target identity to HOTL disposition parser.
- Disproving Observation: unrelated target still blocks or matching target becomes inert.
- What Local Reasoning Cannot Prove: live GitHub comment rendering.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: target-bound irreversible closeout floor.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Shared closeout parsers with per-issue syntax must receive target identity from
their carriers, with a bundled and a direct-mutation regression.
