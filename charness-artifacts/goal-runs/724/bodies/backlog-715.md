<!-- charness-work-item-key: backlog-715 -->
# Existing Work Item #715 — Installed implementation identity

## Purpose and premise

Require implementation-skill admission to resolve and report the installed and
source implementation identities before worker selection. Source-only green is
not installed adoption.

## Owned change and acceptance

Prove stale-installed refusal and matching-installed acceptance with explicit
paths, hashes, and version identity. A worker cannot silently select a stale
installed skill after a source repair.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_skill_surface_preflight.py`, then changed-line proof. This child does not mutate the installed host.
