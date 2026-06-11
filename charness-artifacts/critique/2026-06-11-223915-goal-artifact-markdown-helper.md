# Critique: goal artifact markdown helper

Date: 2026-06-11
Scope: Slice 3 of `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`

## Decision Reviewed

Extract repeated achieve goal-artifact fenced-code masking logic into
`skills/public/achieve/scripts/goal_artifact_markdown.py`, while preserving each
consumer module's private `_mask_fences` surface as an alias.

Changed source files include:

- `skills/public/achieve/scripts/goal_artifact_markdown.py`
- `skills/public/achieve/scripts/goal_artifact_lib.py`
- `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
- `skills/public/achieve/scripts/goal_artifact_disposition_grammar.py`
- `skills/public/achieve/scripts/goal_artifact_coordination_floors.py`
- `skills/public/achieve/scripts/goal_artifact_timebox.py`
- `skills/public/achieve/scripts/goal_artifact_phase_routing.py`
- `skills/public/achieve/scripts/goal_artifact_closeout_delegation.py`
- `skills/public/achieve/scripts/goal_artifact_discussion.py`
- `skills/public/achieve/scripts/goal_artifact_early_close_report.py`
- generated `plugins/charness/skills/achieve/scripts/goal_artifact_*.py` mirrors

## Expected Invariants

- Balanced backtick and tilde fenced blocks are blanked while preserving length
  and newline offsets.
- Unbalanced fences fail open by returning the original text.
- Existing tests and callers that reference `module._mask_fences` still work.
- Plugin mirrors carry the new helper alongside the consumers.

## Executed Proof

- Focused pytest: `191 passed`.
- Targeted `ruff check` and `python3 -m py_compile`.
- Full public/support skill script `py_compile`.
- `python3 scripts/validate_packaging.py --repo-root .`.
- `python3 scripts/validate_packaging_committed.py --repo-root .`.
- `python3 scripts/validate_skills.py --repo-root .`.
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`.
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`.
- `python3 scripts/validate_public_skill_validation.py --repo-root .`.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`.
- `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`.
- Broad pytest: `2803 passed, 4 skipped, 26 deselected`.
- `nose` broad scan after previous slice: `525 families / 12773 dup_lines`;
  after this slice: `526 families / 12590 dup_lines`.
- `nose` resolver/scaffold-filtered `top 40`: `3033` duplicated lines before,
  `2943` after.

## Fresh-Eye Findings

Reviewer: subagent `Dirac`.

- Low: commit-inclusion risk because the new source and plugin helper files were
  untracked during review. This is a process risk, not a code blocker; the
  helper files must be staged with the consumers before commit.
- Low: same-interpreter public/plugin cache risk remains because sibling imports
  use the bare module name `goal_artifact_markdown`. The reviewer judged the
  current risk low because the helper is pure, path-insensitive, and source /
  plugin copies are identical.

No blocker found.

## Counterweight

This is a real structural simplification: the duplicated parsing algorithm now
has one owner, and private `_mask_fences` surfaces remain stable for tests and
callers. It does trade a small sibling-import pattern into several modules, but
that pattern is shorter and less semantically risky than maintaining divergent
copies of markdown fence masking.
