# Debug Review
Date: 2026-08-12

## Problem

The final verification lock reported two retro lesson-selection preview failures, but the live source-checkout preview and its focused tests then passed. The report had read a retained failure log rather than a freshly attributable failure from the current lock.

## Correct Behavior

Given a newly persisted retro, when the repository validates its lesson-selection preview, then the checked-in index must be byte-equivalent to `scripts/build_retro_lesson_selection_index.py` from this repository.

## Observed Facts

- A retained `pytest.log` contained two `test_lesson_selection_preview` failures after 8,640 passes.
- `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed stable-preview-seed --json` passed against the same worktree afterwards.
- `python3 -m pytest tests/test_lesson_selection_preview.py -q` passed (6 passed) afterwards.
- A freshly run standing suite then reached a different, attributable failure: the live inventory-consumption floor probe still pinned the pre-goal quality corpus (134 artifacts) while the goal added four quality artifacts (138).

## Reproduction

- Run `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed stable-preview-seed --json` and `python3 -m pytest tests/test_lesson_selection_preview.py -q` from the current worktree; both pass, so the reported index failure is not reproducible.

## Candidate Causes

- A retained failure log was associated with the current lock despite not being refreshed by that run.
- Installed plugin helper used an older lesson-index implementation.
- The new retro's fields exercised a schema difference between installed and source-repo builders.

## Hypothesis

- The current source-checkout index was stale; disconfirmer: run the current preview and focused consumer tests without rewriting the index.

## Verification

- result: disproved — the current preview and its focused tests pass without rewriting the index. The retained failure log is not evidence of a current source/index mismatch.

## Root Cause

No current lesson-index defect was established. The initial diagnosis relied on an old failure log, so it cannot support a claim about installed-helper/source-checkout incompatibility. The actionable defect was instead the stale live inventory-floor measurement after this goal added four quality artifacts; both live measurement probes were refreshed from the repository scripts.

## Invariant Proof

- Invariant: a live corpus measurement must agree with the checked-in quality corpus it describes.
- Producer Proof: `measure_inventory_consumption_floor.py` and `measure_inventory_marker_rule.py` re-derived both probe payloads from the current repository.
- Final-Consumer Proof: `test_a_declaration_is_not_its_own_corroboration.py` and `test_inventory_marker_rule_measurement.py` passed (59 passed).
- Interface-Shape Sibling Scan: both shallow and recursive marker variants were refreshed; no validator threshold or consumer-field contract changed.
- Non-Claims: this does not prove the retained log's original run was healthy or establish compatibility across installed plugin revisions.

## Detection Gap

- final lock reporting | retained failure output was not attributable to the current run | record only fresh process output with an explicit exit status.

## Sibling Search

- Mental model: a retained failure log is evidence of a past failure, not of the current tree.
- same layer: shallow and recursive quality-corpus probes | decision: refresh both now | proof: current measurement output and 59 focused tests.
- no cross-file sibling: validator thresholds and consumer declarations were unchanged, so this is measurement synchronization rather than a rule edit.

## Seam Risk

- Interrupt ID: retained-failure-log-attribution
- Risk Class: none
- Seam: final-lock receipt to per-check failure log
- Disproving Observation: a fresh same-command process reproduces the cited failure
- What Local Reasoning Cannot Prove: the provenance of the prior retained failure
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Treat retained failure logs as diagnostic context only. Final lock claims must bind to fresh command output and an explicit exit status; synchronize a live measurement whenever the corpus it measures changes.
