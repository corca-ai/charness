#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. The rule and its one implementation live in
# scripts/exported-copy-guard.sh; this gate's own measured consequence is below.
#
# This copy's failure was worse than #618's because it was GREEN. The whole population comes
# from `find` against the cwd, so the mirrored copy at `plugins/charness/scripts/` found no
# top-level `*.sh` (no `init.sh` there), found the ten mirrored `scripts/*.sh`, and skipped both
# the `tests/` and `.githooks/` branches because neither directory exists in the mirror. It then
# linted ten files and exited 0 while never seeing `init.sh`, `tests/**/*.sh`, or `.githooks/*`.
# A silent scope shrink under a passing verdict is strictly worse than a red one: nothing looks
# wrong. `REPO_ROOT_VERIFIED` below exists so the empty-population exit can tell "we know this
# root and discovery came back empty" (a broken discovery list) from "we could not confirm the
# root" (the pre-existing, deliberately tolerant behavior).
GATE_NAME="check-shell"
GATE_CONSEQUENCE="This gate discovers shell files by walking its own root, so a package root that is
not the git root lints a narrower tree and still exits 0."
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

collect_shell_files() {
  find . -maxdepth 1 -type f -name '*.sh' || return "$?"
  find scripts -maxdepth 1 -type f -name '*.sh' || return "$?"
  if [[ -d tools ]]; then
    find tools -maxdepth 1 -type f -name '*.sh' || return "$?"
  fi
  if [[ -d tests ]]; then
    find tests -type f -name '*.sh' || return "$?"
  fi
  if [[ -d .githooks ]]; then
    find .githooks -maxdepth 1 -type f || return "$?"
  fi
}

if collect_shell_files 2>"$listing_stderr_path" | sort >"$listing_path"; then
  mapfile -t sh_files <"$listing_path"
else
  rc=$?
  echo "check-shell: shell file discovery failed." >&2
  echo "command: { find . -maxdepth 1 -type f -name '*.sh'; find scripts -maxdepth 1 -type f -name '*.sh'; find tools -maxdepth 1 -type f -name '*.sh' when tools/ is present; find tests -type f -name '*.sh' when present; find .githooks -maxdepth 1 -type f when present; } | sort" >&2
  printf 'exit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$listing_path" >&2
  echo "STDERR:" >&2
  cat "$listing_stderr_path" >&2
  exit 1
fi

if [ "${#sh_files[@]}" -eq 0 ]; then
  # An empty population is only honestly green when the root is unconfirmed -- a tree that may
  # simply have no shell files, which is why `shellcheck` is not invoked with zero arguments.
  # From a root we KNOW (git toplevel, or an operator-asserted CHARNESS_REPO_ROOT) an empty
  # result cannot mean "no shell files": this script is itself `scripts/check-shell.sh`, so the
  # discovery list found nothing where it must find at least itself. Reporting 0 there would be
  # the same false green the root guard above was added to close.
  # VERIFIED means git compared and agreed; ASSERTED means the operator named the root.
  # Both are "a root we know"; only one of them is a comparison, and reading just the
  # first left an unpacked non-git export at a named root back on the tolerant exit 0.
  if [ "$REPO_ROOT_VERIFIED" -eq 1 ] || [ "${REPO_ROOT_ASSERTED:-0}" -eq 1 ]; then
    echo "check-shell: no shell files discovered under $REPO_ROOT." >&2
    echo "The discovery list cannot see this script itself; it is wrong, not the tree." >&2
    exit 1
  fi
  exit 0
fi

shellcheck -x "${sh_files[@]}"
