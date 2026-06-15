# Issue 373 Producer-Before-Validator Debug
Date: 2026-06-15

## Problem

Issue #373 reported that artifact-producing skill bootstrap instructions can run validators before the scaffold or template producer. The visible regression is `skills/public/achieve/SKILL.md`, where `check_goal_artifact.py` was shown before `upsert_goal.py`.

## Correct Behavior

Template-producing helpers run before validators or readiness checks. Validators are post-scaffold gates: they verify an existing, shaped artifact and must not be documented as the discovery or scaffold mechanism.

## Observed Facts

- `skills/public/achieve/SKILL.md` listed `check_goal_artifact.py` before `upsert_goal.py` in the `## Bootstrap` command block.
- `skills/public/achieve/references/goal-artifact.md` already showed the correct order: `upsert_goal.py` before `check_goal_artifact.py`.
- `tests/quality_gates/test_goal_artifact_producers.py` proved the produced goal shape but did not inspect bootstrap command order.
- Sibling bootstraps for debug, quality, ideation, critique, handoff, retro, and hitl did not show a validator command before a producer command in their startup examples.

## Reproduction

Read `skills/public/achieve/SKILL.md` and inspect the `## Bootstrap` fenced shell block. The validator command appears before the producer command, so an operator following the bootstrap literally can validate an artifact that has not been scaffolded yet.

## Candidate Causes

- The bootstrap block mixed discovery, scaffold, and validation commands without an invariant that producers must precede validators.
- Existing producer tests verified artifact shape after helper execution, not the public operator instructions that tell agents how to start.
- Achieve uses `check_goal_artifact.py` both as a final gate and as a helpful inspection tool, which made it easy to accidentally promote the validator into the scaffold position.
- The sibling skill scaffolds expose validator commands through helper payloads, but no repo-level test scanned skill bootstrap examples for producer/validator ordering.

## Hypothesis

Reversing the achieve bootstrap order and adding a table-driven bootstrap-order test for all known public artifact producer/validator pairs will catch this issue and the likely sibling regression class.

## Verification

- `pytest -q tests/quality_gates/test_artifact_producer_order.py tests/quality_gates/test_goal_artifact_producers.py` passed.
- `python3 scripts/validate_debug_artifact.py --repo-root . --report-all` passed.
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --check` passed.
- `python3 scripts/validate_skills.py --repo-root .` passed.
- `python3 scripts/validate_packaging.py --repo-root .` and `python3 scripts/validate_packaging_committed.py --repo-root .` passed after plugin mirror sync.

## Root Cause

The repo lacked a deterministic guard on public skill bootstrap examples. Validator commands were treated as harmless inspection commands even when placed before the command that creates the artifact they validate.

## Invariant Proof

- Invariant: When a public skill bootstrap names both a template producer and its artifact validator, the producer command appears first.
- Producer proof: `tests/quality_gates/test_artifact_producer_order.py` scans known public artifact surfaces, including same-script mode pairs such as `hitl` sync versus `--check`, and fails when a validator appears before its producer.
- Consumer proof: `skills/public/achieve/SKILL.md` now documents `upsert_goal.py` as the producer and `check_goal_artifact.py` as a post-scaffold gate.

## Detection Gap

The prior tests covered goal artifact shape but not the public command sequence an operator would follow. The new gate closes that specific instruction-surface gap.

## Sibling Search

Checked public skill bootstrap sections for achieve, debug, quality, ideation, critique, handoff, retro, and hitl. Only achieve had a producer/validator inversion in the startup block. Fresh-eye recurrence critique caught that `hitl` needed executable coverage despite using the same script for produce and check modes; the ordering test now includes that same-script mode pair.

## Seam Risk

- Interrupt ID: producer-before-validator-373
- Risk Class: none
- Seam: public skill bootstrap instructions for artifact-producing workflows
- Disproving Observation: a bootstrap command block that names a validator before the producer is sufficient to disprove the intended operator sequence
- What Local Reasoning Cannot Prove: that every future artifact-producing skill will be added to the table without review; closeout relies on the changed-surface and skill validation gates to keep new public skills visible
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

Continue implementation. The fix is narrow, deterministic, and directly tied to the reported regression. Run the required critique and closeout before committing.

## Prevention

Keep producer/validator ordering as an executable quality gate rather than a prose-only convention. Add new artifact-producing public skills to `PRODUCER_VALIDATOR_PAIRS` when they introduce a scaffold helper plus validator/readiness check.

## Related Prior Incidents

None found for this exact ordering bug during the sibling search.
