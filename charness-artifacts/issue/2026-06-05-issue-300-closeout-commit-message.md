Normalize setup host docs only path

Close #300.

Classification: feature.
Issue closeout carrier: direct-commit.
Issue: #300 Make setup host-docs-only normalization explicit.
JTBD: operators who ask for a narrow AGENTS.md/host-docs setup path need the
same deterministic AGENTS.md plus CLAUDE.md symlink policy as full setup,
without hand-writing a partial approximation first.
Boundary: preserve the existing setup agent-docs policy; add a safer narrow
execution path and documentation, not a new host instruction policy.
Resolution brief: feature-class issue with no open product decisions; implement
the smallest host-docs-only helper that dry-runs by default, writes only with
`--execute`, and blocks on real CLAUDE.md content that needs a user merge
decision.
Implementation: Added `normalize_host_docs.py` under the setup skill and
`scripts/setup_host_docs_lib.py`. The helper writes a compact canonical
`AGENTS.md` template plus `CLAUDE.md -> AGENTS.md` when both are missing, creates
only the symlink when AGENTS.md already exists, and blocks instead of merging a
real CLAUDE.md file.
Prevention: setup docs now route narrow "host docs only" / "AGENTS.md only"
requests through the helper so the deterministic symlink policy is not lost.
Tests: `pytest -q tests/quality_gates/test_setup_normalize_host_docs.py
tests/quality_gates/test_setup_render_skill_routing.py
tests/quality_gates/test_setup_inspect_policy.py::test_setup_inspect_repo_flags_targeted_missing_surface
tests/quality_gates/test_achieve_before_activation.py
tests/quality_gates/test_release_only_sentinel_inventory.py` passed.
Critique: charness-artifacts/critique/2026-06-05-issue-300-host-docs-normalization.md
