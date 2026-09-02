#!/usr/bin/env bash
set -euo pipefail

GATE_NAME="self-validate-install-update"
GATE_CONSEQUENCE="This gate runs repo-owned pytest targets rooted at its own root, and the export ships
no tests/, so from a package root that is not the git root it reports missing test files
instead of the reason they are missing."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "self-validate-install-update: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=0
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

python3 scripts/gates_support/run_standing_pytest.py \
  --repo-root "$REPO_ROOT" \
  --mode read-only \
  --include-release-only \
  --pytest-target tests/charness_cli/test_managed_install.py \
  --pytest-target tests/charness_cli/test_codex_cache_refresh.py \
  --pytest-target tests/charness_cli/test_update_propagation.py
