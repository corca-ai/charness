#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. The rule and its one implementation live in
# scripts/exported-copy-guard.sh; this gate resolves its shell population from the
# adapter-owned `shell_sources` universe at the verified repository root.
#
# The previous cwd-relative `find` silently narrowed an exported run to the mirrored
# package tree. The shared resolver makes the population explicit and lets a declared
# empty adapter family refuse while an undeclared empty family reports a no-op.
GATE_NAME="check-shell"
GATE_CONSEQUENCE="This gate resolves shell files from the adapter-owned shell_sources universe, so
the package root cannot silently replace the verified repository root."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-shell: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "shellcheck unavailable; skipping shell lint." >&2
  exit 0
fi

listing_dir="$(mktemp -d)"
# `|| true` so a failed removal cannot restate this gate's verdict: `set -e` is in
# force inside an EXIT trap, so an aborting `rm` replaces the pending status with its
# own. Measured on run-quality.sh, where it turned a correct exit 2 into a 1.
trap 'rm -rf "$listing_dir" || true' EXIT
listing_path="$listing_dir/shell-files.txt"
listing_stderr_path="$listing_dir/shell-files.stderr"
universe_script="scripts/quality_universes_lib.py"
if [[ ! -f "$universe_script" ]]; then
  universe_script="$CHARNESS_GATE_DIR/quality_universes_lib.py"
fi

if python3 "$universe_script" \
  --repo-root "$REPO_ROOT" \
  --key shell_sources \
  --gate-label check-shell \
  --format lines >"$listing_path" 2>"$listing_stderr_path"; then
  :
else
  rc=$?
  echo "check-shell: shell universe resolution failed." >&2
  echo "command: python3 '$universe_script' --repo-root '$REPO_ROOT' --key shell_sources --gate-label check-shell --format lines" >&2
  printf 'exit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$listing_path" >&2
  echo "STDERR:" >&2
  cat "$listing_stderr_path" >&2
  exit 1
fi
mapfile -t sh_files <"$listing_path"

if [ "${#sh_files[@]}" -eq 0 ]; then
  echo "WARN: check-shell: discovered empty shell_sources universe; nothing was checked."
  exit 0
fi

shellcheck -x "${sh_files[@]}"
