<!-- charness-work-item-key: backlog-637 -->
# Existing Work Item #637 — Artifact scaffold preflight

## Purpose and premise

Add exact flattened installed-layout positive and negative scaffold fixtures and
preflight output. Keep source-checkout and installed claims separate.

## Owned change and acceptance

The preflight names the flattened paths and refuses missing or ambiguous
scaffolds deterministically; source layout success cannot satisfy installed
layout proof.

## Accepted ownership boundary

This child owns the artifact-surface preflight's package-layout resolution. The
registry remains canonical at `skills/public/...`; a checked-in or exported
plugin resolves the corresponding flattened `skills/...` producer from the
dispatcher package, never from the consumer artifact root. Missing and
ambiguous producer candidates are deterministic failures.

The child does not own the separate retro-planner issue, marketplace or hosted
installation behavior, or any installed-host mutation.

## Verification and evidence boundary

- Implementation commit: `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f`
  (`fix(issue-637): resolve exported artifact scaffold paths`); canonical
  source and checked-in plugin mirror are byte-identical.
- Clean proof worktree: branch
  `proof/issue-637-artifact-preflight-20260827` at the named target commit;
  path scope is `scripts/check_artifact_surface_preflight.py`,
  `plugins/charness/scripts/check_artifact_surface_preflight.py`, and
  `tests/quality_gates/test_check_artifact_surface_preflight.py`. It started
  and ended with empty `git status --porcelain`; cache, pycache, and coverage
  paths were outside the worktree.
- Exact standing target: `python3 scripts/run_standing_pytest.py --repo-root .
  --mode read-only --pytest-target
  tests/quality_gates/test_check_artifact_surface_preflight.py` — `62 passed`.
- Export-only consumer fixture: flattened positive stub rendering passed;
  missing flattened producer and simultaneous canonical/flattened producers
  both returned code `1` and named their candidate paths.
- Focused compile, Ruff, and source/mirror parity checks passed.

Changed-line proof is intentionally not a blocking gate for this implementation;
the proof surface was verified through its focused target and export fixture.
No installed-host mutation, remote CI, release, push, tag, or fresh-eye review
is claimed.
