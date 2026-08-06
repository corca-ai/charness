# Issue #512 Metric Window Ordering Debug
Date: 2026-08-06

## Problem

`record_metric_window.py` inserts the `Host metric window:` line at the start of
`## Final Verification`. If an author has an exact-match section-fill operation
that expects the heading followed by its authored body, the helper's insertion
changes the input shape and the replacement silently does not apply.

## Correct Behavior

Given a goal artifact with an authored `## Final Verification` body, when the
metric helper records a valid window, the authored body remains a contiguous
block and the new line is appended within that section. A later exact-match
author fill must still match; the metric reader must still parse one window.

## Observed Facts

- #512 was read through the GitHub adapter with `comments_read: true`; it is
  OPEN and has no comments.
- `goal_metric_window_lib.py:117-126` previously constructed the new body as
  `line + existing_body`, so the helper prepended.
- The causal fresh-eye review found the aggregate refusal and soft-wrap claims
  already disconfirmed by current source/tests; the metric ordering concern
  remains source-supported but its historical ceal frequency is unproven.
- The repaired `test_record_metric_window.py` now proves insertion, idempotence,
  parsing, and an author's exact-match operation after helper insertion.

## Reproduction

The smallest local fixture used a `## Final Verification` heading followed by
`Author placeholder.` and then called the current helper. The output placed the
metric line before the authored text; the exact string
`## Final Verification\n\nAuthor placeholder.` was absent. This confirms the
ordering mechanism at the current HEAD without claiming the original ceal host
or a provider roundtrip.

## Candidate Causes

- The helper owns a section mutation but has no ordering invariant with the
  author's section-fill operation.
- The insertion policy prepends generated evidence instead of preserving the
  authored section as the stable prefix.
- Tests cover helper output and reader parsing but omit the reported producer /
  author sequence.

## Hypothesis

If the helper appends the metric line at the end of `## Final Verification`,
then an exact-match author fill performed after the helper remains applicable
while repeated calls still replace one line. Disconfirmer: a fixture must show
the authored block remains contiguous, the line remains inside Final
Verification, and the host probe still reports `parsed`.

## Verification

- confirmed — the pre-repair source reproduced the prepend/order failure
  mechanism; the repaired source appends and the regression fixture preserves
  the authored exact-match prefix.
- confirmed — focused tests pass, including one-window replacement and the host
  probe's `parsed` result after the repaired helper runs.
- Causal fresh-eye review: parent-delegated high-leverage review returned
  findings, and the boundary fingerprint verified clean with no drift.

## Root Cause

The metric writer and the author both mutate the same closeout section, but the
writer's prepend policy is not an append-only contract. This makes a helper
call change the exact authored shape that a later fill operation may match.

## Invariant Proof

- Invariant: generated metric evidence must not break the authored
  `Final Verification` body, and exactly one parseable window must reach the
  closeout reader.
- Producer Proof: `goal_metric_window_lib.record_metric_window` now preserves
  the authored body and appends one generated line; the regression observes the
  stable exact-match shape.
- Final-Consumer Proof: `host_log_probe_lib.parse_goal_metric_window` reads the
  repaired line and the focused end-to-end test observes `parsed`.
- Interface-Shape Sibling Scan: closeout evidence consumes the section through
  the goal artifact parser and the shared coordination grammar; no external
  mirror is changed by this local helper move.
- Non-Claims: no ceal host execution, installed plugin, adapter/provider
  roundtrip, live source, or remote CI behavior is proven by this diagnosis.

## Detection Gap

- The helper unit tests detect insertion and duplicate windows, but no test
  exercises an exact-match author fill after the helper call. The smallest
  detector is the reproduction fixture promoted to a regression test.

## Sibling Search

- Mental model: a generated evidence producer mutates an authored closeout
  section that a later consumer or author treats as stable text.
- same-layer: `goal_metric_window_lib.py` and `test_record_metric_window.py` |
  decision: same bug, fix now | proof: local source and fixture reproduction.
- cross-file: `goal_artifact_closeout_evidence.py` and
  `host_log_probe_lib.py` | decision: same class, diagnostic-only for this
  slice; preserve their reader contract | proof: static inspection.
- abstraction-up: lifecycle ordering guidance | decision: valid follow-up
  outside the slice; follow-up: #512-closeout-ordering-docs | proof: static
  inspection only.
- Proof levels stay separate: local payload proof only; no provider roundtrip.

## Seam Risk

- Interrupt ID: issue-512-metric-window-ordering
- Risk Class: contract-freeze-risk
- Seam: goal artifact authoring helper -> Final Verification reader
- Disproving Observation: append-only output still breaks exact author fill or
  causes the host metric probe to report a missing/ambiguous window.
- What Local Reasoning Cannot Prove: behavior in the originating ceal host,
  installed copies, adapters, or providers.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: none

## Prevention

Keep the writer append-only within `## Final Verification`, retain the
author-fill regression, and preserve the existing idempotent single-window and
parser tests. The public reference now states that exact-match filling is safe
before or after the helper. Defer broader lifecycle documentation until a
concrete cross-surface failure appears.
