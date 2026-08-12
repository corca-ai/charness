# Debug Review
Date: 2026-08-12

## Problem

The final verification lock's standing pytest suite failed because the retro lesson-selection index written while persisting this goal's retro did not match the current repository generator.

## Correct Behavior

Given a newly persisted retro, when the repository validates its lesson-selection preview, then the checked-in index must be byte-equivalent to `scripts/build_retro_lesson_selection_index.py` from this repository.

## Observed Facts

- Standing pytest failed two `test_lesson_selection_preview` tests after 8,640 passes.
- The failure named `charness-artifacts/retro/lesson-selection-index.json` and prescribed the repository-root builder.
- Persistence was invoked through the installed plugin skill path; that helper refreshed the index, while the current repository owns the verifier and builder.

## Reproduction

- Run the installed retro persistence helper against this repository, then run `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed stable-preview-seed --json`; the index mismatch raises `ValueError`.

## Candidate Causes

- Installed plugin helper used an older lesson-index implementation.
- The new retro's fields exercised a schema difference between installed and source-repo builders.
- The index changed because of a nondeterministic timestamp or ordering defect.

## Hypothesis

- The installed helper's refresh used a different generator than this checkout; disconfirmer: re-run the repository-root builder and check whether the preview and focused tests pass without editing retro content.

## Verification

- result: confirmed — the repository-root builder regenerates the index, and the focused preview tests are the final consumer check; no retro prose or source generator repair is required.

## Root Cause

An installed/exported retro persistence helper refreshed a repository-owned generated index with a generator version that differs from this checkout. The plugin helper is safe for its own installed contract, but its generated index is not interchangeable with the source checkout's current verifier.

## Invariant Proof

- Invariant: generated lesson-selection index is produced by the same repository code that validates and consumes it.
- Producer Proof: `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write` refreshes the index.
- Final-Consumer Proof: `tests/test_lesson_selection_preview.py` exercises the repository preview reader.
- Interface-Shape Sibling Scan: persistence-generated state is the only affected seam in this closeout; source/plugin code projections were not changed.
- Non-Claims: this does not prove every installed plugin version can safely regenerate a source checkout's derived artifacts.

## Detection Gap

- final broad pytest | installed helper refreshed a source-owned index without a provenance check | rerun the source builder before the lock and retain this diagnosis.

## Sibling Search

- Mental model: a compatible skill interface does not imply compatible generated-artifact schema.
- same layer: retro persistence and index builder | decision: same waste, fix now | proof: source-builder regeneration plus preview tests.
- no cross-file sibling: the existing consumer check caught the mismatch before a commit or publish.

## Seam Risk

- Interrupt ID: generated-artifact-provenance
- Risk Class: none
- Seam: installed plugin helper to source-checkout generated artifact
- Disproving Observation: source builder leaves the index mismatch unchanged
- What Local Reasoning Cannot Prove: compatibility of every installed plugin revision with every checkout
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Run the repository-root index builder after goal-aware retro persistence when the final validator belongs to the source checkout, then let the preview tests certify the producer-to-consumer pair.
