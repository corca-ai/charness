# Debug Review: staged owner universe
Date: 2026-09-06

## Problem

Committing only evidence Python copies and an impl instruction failed with "refusing empty matched universe for named --paths ... nothing was validated" in the cheap-owner pre-commit hook.

## Correct Behavior

Given staged files outside the length owner's universe, do not invoke that owner. Mixed sets still validate the in-universe source. Explicit direct empty selections must continue to refuse.

## Observed Facts

The hook selects every .py suffix; check_code_lengths.select_targets intersects those paths with its adapter-resolved universe. Evidence copies are intentionally outside that universe. The initial five-path commit failed; unstaging only the two evidence copies removed that failure. The later release-receipt refusal is a separate correct boundary, admitted by the documented local Slice-reopen contract.

## Reproduction

Stage charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-baseline-catalog.py without a source .py change and run scripts/hooks/check_staged_cheap_owners.py. The final hook refuses despite having no applicable length-owned input. Captured tool output supplies exact symptom; local owning source resolves it, so no public-web diagnosis is useful.

## Candidate Causes

- Invalid Python content: disconfirmed; refusal occurs during universe selection, before measurement.
- Missing measurement binary: disconfirmed; no tokei command is reached for empty selection.
- Caller universe wider than callee: confirmed by suffix-only hook filter and callee intersection.

## Hypothesis

Using the owner's existing select_targets before dispatch removes artifact-only invocations and preserves source-file checks. Disconfirmer: unstaging only the evidence copies removed the original refusal before repair; mixed source/evidence and custom-adapter cases then test whether the correction skips too much.

## Verification

Confirmed: cheap-owner suite 12 passed and dependent staged-plan suite 40 passed. The actual hook command on both evidence copies now exits 0. The custom-universe fixture initially used unsupported inline YAML and correctly refused the invalid adapter; block-list syntax passed. The source-child failure assertion uses a mocked nonzero child and proves propagation, not tokei itself. Configured independent review goal798-final-owner-review passed with no findings; report: charness-artifacts/critique/workers/goal798-final-owner-review/worker-report.yaml. Its non-claims leave consumer A/B and release proof to the parent Goal.

## Root Cause

Empty-universe refusal → hook passed only evidence copies → hook selected by suffix → owner intentionally excludes artifact trees → caller duplicated applicability with a weaker rule. Existing tests covered in-universe Python and unrelated Markdown, not out-of-universe Python.
Pattern Ladder: observed hook refusal (live commit); local suffix selection (source); interface sibling callee select_targets already correct (source); pattern of patterns is caller re-deriving ownership instead of consuming its selector; structural prevention is mixed/outside/custom-universe hook coverage. A true source file falsifies indiscriminate skipping.

## Invariant Proof

- Invariant: dispatch only nonempty owner-selected input, preserving the owner's actual failure result.
- Producer Proof: consume the existing selector; no copied patterns.
- Final-Consumer Proof: artifact-only actual hook exit 0; mixed/custom selector checks and mocked source-failure propagation in the 12-test suite.
- Interface-Shape Sibling Scan: staged_commit_gate_plan Python compile accepts all Python and does not use this universe; docs length invocation validates the full docs corpus, not an empty scoped subset.
- Non-Claims: no removal of length checks, adapter validation, or direct empty-selection refusal.

## Detection Gap

Hook tests only valid source Python and unrelated README | suffix coincidence hid mismatch | artifact-only and mixed-set fixtures expose it.

## Sibling Search

- Mental model: any file sharing an extension belongs to the same owner.
- same layer: docs/schema/debug selectors | decision: not the same bug | proof: static scan, these invoke whole-corpus owners.
- specialization down: custom adapter Python universe | decision: same bug, fix now | proof: focused case planned.
- abstraction up: direct length CLI | decision: diagnostic-only | proof: source; preserve empty refusal.
- cross-file: scripts/staged_commit_gate_plan.py compile selection | decision: not the same bug | proof: compile intentionally accepts arbitrary Python.
- mental-model: implementation evidence source copies | decision: same bug, fix now | proof: live refusal.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: local pre-commit owner applicability
- Disproving Observation: none from external host
- What Local Reasoning Cannot Prove: hosted release
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/friction-reduction.md

## Prevention

Reuse the owner selector and retain negative source failure propagation proof. Independent critique accepted this boundary; Goal 798 integrated and release verification remain separate. No gate policy is widened or weakened.
