# Debug Review: advisory presence is not confirmed inaccuracy
Date: 2026-09-06

## Problem

The published release renderer labels every advisory finding `SHIPPED KNOWN-INACCURATE`, including a finding that only says supporting evidence was not available. This changes the finding's meaning at the final reader boundary.

## Correct Behavior

Given an opaque advisory finding, the release record preserves its text, order and nongating disposition without inferring a demonstrated error. Confirmed errors must remain equally visible, and an empty list must say none recorded.

## Observed Facts

The pre-repair `_scope_lines` header uses `defect(s)` and `SHIPPED KNOWN-INACCURATE` based solely on nonempty `advisory_findings`. The schema carries strings or dictionaries, not an epistemic type. The final `claims_review_lines` composition includes that header. Independent investigation identified the category error before implementation.

## Reproduction

`charness-artifacts/probe/2026-09-06-advisory-render-comparison.json` captures the same evidence-limit and confirmed-error records passed through actual final renderers: canonical exported v8.4.3 versus integrated repair. Both baseline cases receive the categorical inaccuracy label; candidate retains each supplied finding under neutral nongating wording.

## Candidate Causes

- The reviewer already declared an error: disconfirmed by an evidence-limit-only input with no such declaration.
- The schema classifies advisory findings as defects: disconfirmed by opaque list/string/dictionary carrier semantics.
- The final renderer infers error from nonempty advisory scope: confirmed by paired final-consumer output.

## Hypothesis

A neutral aggregate header, with unchanged per-finding rendering, removes the invented classification without concealing actual errors. Disconfirmer: the confirmed-error case must still appear unchanged and as visibly as the evidence-limit case.

## Verification

Confirmed: release scope/publication-boundary tests passed (56), including evidence-limit, confirmed-error, mixed, empty, legacy strings/dictionaries, order and flattening. Integrated changed-line coverage covered all mapped changed lines. Independent code/contracts review passed in `charness-artifacts/critique/workers/goal798-code-contracts/worker-report.yaml`; it explicitly dispositioned concern about hiding confirmed defects.

## Root Cause

Advisory record overstates truth → header promotes every item to a defect → presence controls the branch, not a typed finding meaning → prior visibility fix preserved waived narrative-error wording → the regression test pinned that label rather than varying epistemic meaning. Missing invariant: transport may preserve but must not strengthen supplied evidence.

Pattern Ladder: observed final record (paired executable output; refute with evidence-only input); local `_scope_lines` aggregation (same bug, fix now); interface sibling `claims_review_lines` composition (same bug, fix now; actual final output); broader schema/rendering boundary (static scan only; no new classification schema justified). General claims about every release signal remain unproven.

## Invariant Proof

- Invariant: when a claims review supplies advisory text, the final release record preserves it without synthesizing a stronger truth verdict.
- Producer Proof: paired inputs in the comparison receipt deliberately differ in epistemic meaning.
- Final-Consumer Proof: actual `claims_review_lines` outputs and its standing regression cases.
- Interface-Shape Sibling Scan: `_scope_lines`, `claims_review_lines`, scope validation and resume publication transport.
- Non-Claims: no correction to historical published records, new schema taxonomy, or public release success.

## Detection Gap

- Old publication test | protected visibility by pinning the categorical label | vary evidence-limit, true-error and mixed inputs at final rendering.
- Scope/schema validator | correctly checks carrier shape, not truth | retain its boundary; avoid teaching it to classify free text.
- Existing flattening cases | protect record rendering integrity | preserve strings/dictionaries and ordering cases.

## Sibling Search

- Mental model: a transport container's presence is treated as a semantic truth judgment.
- same layer: final advisory header | decision: same bug, fix now | proof: executable final-render comparison.
- specialization down: legacy strings and dictionaries | decision: same bug, fix now | proof: standing tests; no shape migration.
- abstraction up: scope schema | decision: same class, diagnostic-only for this slice | proof: static scan | no action needed: it owns renderability, not epistemic classification.
- mental-model: resume publication transports `advisory_findings` | decision: same class, diagnostic-only for this slice | proof: static scan; existing transport preserves items.
- cross-file: `claims_review_scope.py`, `publish_release_resume_publish.py`, and final renderer.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: claims payload→published record wording
- Disproving Observation: local paired output is sufficient for this renderer repair
- What Local Reasoning Cannot Prove: public release visibility
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/evidence-meaning.md

## Prevention

Use neutral aggregate wording and keep the supplied findings visible. The existing final-render tests now vary meaning rather than pinning an unjustified epistemic upgrade. Parent owns final release readback and Work Item #800 closure; this record closes the local diagnosis/repair only.
