fix: preserve authored goal closeout bodies

Closes #512

JTBD: Make complete-flip closeout deterministic when the metric helper and the
author both write the `## Final Verification` section.

Boundary: The resolution owns the portable metric-window writer, its public
contract, generated plugin mirror, and regression proof. It does not claim
Ceal/provider/install behavior, remote CI, serial refusal aggregation, or
soft-wrapped routing.

Resolution brief: Keep authored Final Verification content as a stable prefix
and append the generated Host metric window after it. This preserves exact-match
author fills in either ordering while retaining one-line replacement and
idempotence.

Implementation: Updated `skills/public/achieve/scripts/goal_metric_window_lib.py`
and its generated plugin mirror, clarified `goal-artifact.md` in both surfaces,
and added the helper-then-exact-match regression to
`tests/quality_gates/test_record_metric_window.py`.

Root cause: The helper previously prepended generated evidence into the same
section an author treats as exact-matchable text, changing the authored shape
and allowing a replacement to silently no-op.

Debug artifact: `charness-artifacts/debug/2026-08-06-issue-512-metric-window-ordering-debug.md`

Siblings: Serial refusal aggregation and soft-wrapped routing were inspected and
are already covered by current source/tests; decision: do not bundle; proof:
causal source review and existing targeted tests. Global metric-line matching is
a diagnostic-only follow-up, not a blocker without a concrete misplaced-line
case.

Prevention: Append-only section mutation, an exact-match author-fill regression,
existing idempotence/replacement tests, probe parsing coverage, and an explicit
public ordering contract in source/plugin parity.

Critique #512: charness-artifacts/critique/2026-08-06-issue-512-metric-window-ordering-code-critique.md
Boundary #512: single-surface — producer `record_metric_window` owns the
portable artifact mutation; the plugin copy is a generated mirror and the probe
is the consumer.
Behavior #512: local focused pytest (`tests/quality_gates/test_record_metric_window.py`,
14 passed) exercised the helper-then-exact-match author-fill sequence and parsed
the resulting metric window through the host probe; this is distinct from the
commit carrier and GitHub state readback.

Fresh-Eye Satisfaction: parent-delegated; three named critique angles and a
separate counterweight returned findings, with clean reviewer-boundary
fingerprints and findings-received delivery.
AI-provenance: Agent-authored direct-commit carrier; implementation, focused
tests, source/plugin sync, debug artifact, critique, and closeout evidence were
reviewed and recorded in the listed artifacts.
