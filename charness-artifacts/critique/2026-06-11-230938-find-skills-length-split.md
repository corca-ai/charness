# Critique: find-skills length split

Date: 2026-06-11
Scope: Slice 4 of `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`

## Decision Reviewed

Split worktree workflow recommendation logic and summary-output rendering out of
the find-skills inventory modules so the public skill no longer sits in the
Python length warn band.

Changed source files include:

- `skills/public/find-skills/scripts/list_capabilities.py`
- `skills/public/find-skills/scripts/list_capabilities_lib.py`
- `skills/public/find-skills/scripts/workflow_recommendations.py`
- `skills/public/find-skills/scripts/list_capabilities_summary.py`
- generated `plugins/charness/skills/find-skills/scripts/*` mirrors

## Expected Invariants

- `--recommend-for-task` still returns the same worktree create and cleanup
  workflow recommendations.
- Cleanup-shaped worktree tasks still suppress the create workflow route.
- `--summary` output shape is unchanged, including conditional
  `recommendation_interpretation` when a ranking was produced.
- Plugin-installed `find-skills` still carries and loads the new local helper
  files.
- No new import cycle exists; `list_capabilities.py` depends on leaf helpers.

## Executed Proof

- Focused find-skills pytest: `40 passed`.
- Targeted `ruff check` and `python3 -m py_compile`.
- `python3 scripts/check_python_lengths.py --repo-root . --paths ...` reported
  no warning for the four source/helper files and plugin mirrors.
- Full `check_python_lengths.py --require-git-file-listing`: warn-band count
  moved from `10` files to `8`; the two find-skills files left the warning list.
- `python3 scripts/validate_packaging.py --repo-root .`.
- `python3 scripts/validate_packaging_committed.py --repo-root .`.
- `python3 scripts/validate_skills.py --repo-root .`.
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`.
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`.
- `python3 scripts/validate_public_skill_validation.py --repo-root .`.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`.
- `python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing`.
- `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`.
- Broad pytest: `2803 passed, 4 skipped, 26 deselected`.

## Fresh-Eye Findings

Reviewer: subagent `Nash`.

- No blocker found.
- Reviewer smoke-probed live CLI behavior for create-worktree, cleanup-worktree,
  validation-shaped recommendation, plugin-mirror execution, `--summary` with
  recommendations, and `--summary` without recommendations.
- Low residual: the new helper files were untracked during review and must be
  included in the final commit for both source and plugin mirror trees.

## Counterweight

This split does not chase clone metrics directly. It removes a near-term quality
gate pressure: `list_capabilities.py` and `list_capabilities_lib.py` were both in
the Python length warn band, and the extracted responsibilities are cohesive
leaf helpers. The tradeoff is two more local modules, but both are single-purpose
and loaded through the existing public-skill local module mechanism.
