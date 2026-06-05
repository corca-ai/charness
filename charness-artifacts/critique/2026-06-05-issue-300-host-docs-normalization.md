# Critique: Issue 300 host-docs normalization

Fresh-Eye Satisfaction: parent-delegated

## Change

Add a narrow setup host-docs-only normalization path for issue #300. The change
adds `normalize_host_docs.py` and `setup_host_docs_lib.py`, documents the path
in setup, and updates `achieve` closeout reporting guidance.

## Findings

### Act Before Ship

- Generic setup bootstrap initially invoked `normalize_host_docs.py --execute`,
  which would mutate `AGENTS.md` / `CLAUDE.md` before setup mode detection or a
  narrow host-docs-only path was chosen. This was fixed by making bootstrap
  dry-run and reserving `--execute` for the explicit narrow mutation path.

### Bundle Anyway

- The active goal artifact lagged behind the implementation and closeout draft.
  This was fixed by updating slice status and slice logs before closeout.

### Valid But Defer

- None after the existing-symlink deterministic case was covered by a focused
  test.

### Over-Worry

- Broad pytest is not needed for this pre-lock slice. The changed behavior is
  covered by focused setup/achieve/#299 tests and closeout rehearsal will run
  with `--skip-broad-pytest`.

## Evidence

- Reviewer: Carson (`019e953e-efad-7423-874b-6b79e3ab5ce9`), read-only bounded
  fresh-eye review.
- Touched source: `scripts/setup_host_docs_lib.py`,
  `skills/public/setup/scripts/normalize_host_docs.py`,
  `skills/public/setup/SKILL.md`,
  `skills/public/setup/references/agent-docs-policy.md`,
  `skills/public/achieve/references/lifecycle.md`.
- Focused proof after applying findings:
  `pytest -q tests/quality_gates/test_setup_normalize_host_docs.py
  tests/quality_gates/test_setup_render_skill_routing.py
  tests/quality_gates/test_setup_inspect_policy.py::test_setup_inspect_repo_flags_targeted_missing_surface
  tests/quality_gates/test_achieve_before_activation.py
  tests/quality_gates/test_release_only_sentinel_inventory.py` passed.
