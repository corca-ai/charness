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
# Not runnable from the plugin export, and now it SAYS so. The exported copy self-locates
# to `plugins/charness/`, which has no `charness/`, `tests/`, or `skills/shared/scripts`,
# so it dies on absent paths -- loud, but naming missing directories rather than the
# reason they are missing. This comment claimed the condition was "noted"; noting it in a
# comment is not telling the operator, and the same was true of `run-quality.sh` and
# `self-validate-install-update.sh`. All three now share the guard the other five carry.
set -euo pipefail

GATE_NAME="check-python-lint"
GATE_CONSEQUENCE="This gate lints a fixed path list rooted at its own root, and the export has no
charness/, tests/ or skills/shared/scripts, so from a package root that is not the git
root it reports absent directories instead of the reason they are absent."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-python-lint: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=0
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

# Runtime/cache isolation is owned by the same shell primitive as the hooks and
# quality runner. Ruff is only one consumer of that environment.
# shellcheck source=.githooks/runtime-env.sh
source "$REPO_ROOT/.githooks/runtime-env.sh"

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
  tools \
  tests \
  skills/public/*/scripts \
  skills/support/*/scripts \
  skills/shared/scripts
