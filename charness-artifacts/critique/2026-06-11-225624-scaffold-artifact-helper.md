# Critique: scaffold artifact helper

Date: 2026-06-11
Scope: Slice 3 of `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`

## Decision Reviewed

Extract repeated scaffold validator lookup, JSON/template CLI emission, and
debug/quality current-pointer payload handling into
`scripts/scaffold_artifact_lib.py`, while keeping each public skill scaffold's
template and adapter-specific payload choices local.

Changed source files include:

- `scripts/scaffold_artifact_lib.py`
- `skills/public/critique/scripts/scaffold_critique_artifact.py`
- `skills/public/debug/scripts/scaffold_debug_artifact.py`
- `skills/public/handoff/scripts/scaffold_handoff_artifact.py`
- `skills/public/ideation/scripts/scaffold_ideation_artifact.py`
- `skills/public/quality/scripts/scaffold_quality_artifact.py`
- `skills/public/retro/scripts/scaffold_retro_artifact.py`
- generated `plugins/charness/scripts/scaffold_artifact_lib.py`
- generated `plugins/charness/skills/*/scripts/scaffold_*_artifact.py` mirrors
- `tests/test_scaffold_inprocess_coverage.py`
- `tests/quality_gates/test_scaffold_changed_line_coverage.py`

## Expected Invariants

- Repo-local validators still win over installed-plugin validators when a
  consumer repo owns `scripts/<validator>.py`.
- Installed-like plugin scaffolds still cite bundled validators when the
  consumer repo has no local validator.
- Debug and quality `latest.md` current-pointer behavior still distinguishes
  plain paths, relative symlink targets, and absolute symlink targets.
- Scaffold `main()` still supports both rendered-template stdout and JSON
  payload output.
- In-process coverage still records each scaffold and the shared validator
  fallback branch.

## Executed Proof

- Focused scaffold pytest: `38 passed`, including
  `tests/quality_gates/test_scaffold_changed_line_coverage.py`.
- Targeted `ruff check` and `python3 -m py_compile`.
- Full public/support/plugin script `py_compile`.
- `python3 scripts/validate_packaging.py --repo-root .`.
- `python3 scripts/validate_packaging_committed.py --repo-root .`.
- `python3 scripts/validate_skills.py --repo-root .`.
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`.
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`.
- `python3 scripts/validate_public_skill_validation.py --repo-root .`.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`.
- `python3 scripts/check_changed_surfaces.py --repo-root .` and all listed
  verify commands for the changed surfaces.
- Broad pytest: `2803 passed, 4 skipped, 26 deselected`.
- `nose` broad scan after Slice 2: `526 families / 12590 dup_lines`; after this
  slice: `525 families / 12577 dup_lines`.

## Fresh-Eye Findings

Reviewer: subagent `Newton`.

- No blocker found.
- Low residual: the in-process monkeypatch test exercises helper lookup through
  mutated `module.__file__`, repo-local fallback, and missing-validator raise;
  installed-plugin fallback is covered separately by exported scaffold tests.
- Low residual: standalone copying of a single scaffold without the root/plugin
  `scripts/scaffold_artifact_lib.py` would fail, especially for ideation. This
  is outside the current full-source and plugin-installed packaging contract.
- Low residual: same-process mixed-version imports could reuse a cached
  `scripts.scaffold_artifact_lib`; normal CLI/plugin subprocess execution avoids
  this, and the repo already uses the same `scripts.*` import pattern elsewhere.

## Counterweight

This is a modest but real structural simplification: shared validator lookup and
CLI output no longer live in six copies, while the skill-specific authoring
surface remains local and readable. The helper adds a new root script dependency
for scaffolds, but that dependency is mirrored into `plugins/charness/scripts/`
and exercised by installed-like plugin tests.
