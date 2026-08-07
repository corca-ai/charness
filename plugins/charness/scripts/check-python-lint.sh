#!/usr/bin/env bash
# The single home for the repo's ruff invocation.
#
# It exists because the path list used to live in four places and three of them were
# stale. The local gate gained `skills/shared/scripts` on 2026-07-10 (`3c01f8ad`); the
# CI copy in `.github/workflows/quality-core.yml` was retyped by hand and never followed,
# so ten tracked shared-contract scripts -- `run_plan_envelope.py`, `validate_skills.py`,
# `reviewer_boundary_state.py` among them -- were invisible to the exact workflow whose
# stated job is to catch a direct push that bypasses the local hooks.
#
# That workflow declares `# charness:gate-policy local-gate-subset-mirror` on the claim
# that every step "verbatim re-runs a repo-owned validator the canonical local gate
# already enforces". A retyped command line cannot keep that claim: sameness of
# invocation is not checkable while the invocation is a string someone typed twice. A
# single entrypoint is what makes the claim true by construction rather than by review.
#
# So: change the path list HERE and nowhere else. Callers invoke this script by name.
#
# Not runnable from the plugin export. The exported copy self-locates to
# `plugins/charness/`, which has no `charness/`, `tests/`, or `skills/shared/scripts`, so
# it would die on absent paths. That is true of the exported `run-quality.sh` too and is
# not a regression -- noted because the header above calls this the single home for the
# invocation, and the export is a tree where it cannot run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Hard failure, not the `check-shell.sh` skip. ruff is a pinned, installed dependency
# (`integrations/tools/ruff.json` records the lint phase cannot honestly complete
# without it), so a silent skip here would report a clean lint that never ran -- which
# is the same false-green shape this script was created to close.
if ! command -v ruff >/dev/null 2>&1; then
  echo "ruff unavailable; the Python lint gate cannot report a verdict." >&2
  echo "Install it (see integrations/tools/ruff.json) and re-run." >&2
  exit 1
fi

ruff check \
  charness \
  scripts \
  tests \
  skills/public/*/scripts \
  skills/support/*/scripts \
  skills/shared/scripts
