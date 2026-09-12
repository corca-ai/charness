#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. scripts/exported-copy-guard.sh carries the rule, the reasoning and
# the one implementation; what follows is this gate's own consequence.
#
# Measured from the generated mirror BEFORE this guard: exit 0, "97 Total / 78 OK / 0 Errors".
# A clean green over the wrong tree. Two things go wrong at once there: the
# `:(exclude)plugins/**` pathspec below is cwd-relative, so from `plugins/charness` it excludes
# NOTHING and the gate lints the mirror it is supposed to skip; and `--root-dir` then resolves
# every repo-relative link against the package root instead of the git root. Note this gate was
# predicted to "fail loud" from the mirror and does not -- it passes. Issue #618.
GATE_NAME="check-links-internal"
GATE_CONSEQUENCE="This gate excludes plugins/** with a cwd-relative pathspec and resolves
repo-relative links against its root, so a package root that is not the git root
reports a clean pass over the mirror it should have skipped."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-links-internal: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

run_git_listing_to_file() {
  local context="$1"
  local output_path="$2"
  shift 2
  local stderr_path rc

  stderr_path="${output_path}.stderr"
  if "$@" >"$output_path" 2>"$stderr_path"; then
    return 0
  else
    rc=$?
  fi

  echo "check-links-internal: git file listing failed ($context)" >&2
  printf 'command:' >&2
  printf ' %q' "$@" >&2
  printf '\nexit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$output_path" >&2
  echo "STDERR:" >&2
  cat "$stderr_path" >&2
  return 1
}

if ! command -v lychee >/dev/null 2>&1; then
  cat >&2 <<'EOF'
lychee is required for link checking. Install one of:
  - cargo install lychee
  - download from https://github.com/lycheeverse/lychee/releases
EOF
  exit 1
fi

listing_dir="$(mktemp -d)"
# `|| true` so a failed removal cannot restate this gate's verdict: `set -e` is in
# force inside an EXIT trap, so an aborting `rm` replaces the pending status with its
# own. Measured on run-quality.sh, where it turned a correct exit 2 into a 1.
trap 'rm -rf "$listing_dir" || true' EXIT
tracked_markdown_list="$listing_dir/tracked-markdown.txt"
run_git_listing_to_file tracked-markdown "$tracked_markdown_list" \
  git ls-files -- '*.md' \
  ':(exclude)charness-artifacts/**' \
  ':(exclude).charness/**' \
  ':(exclude).pytest_cache/**' \
  ':(exclude)evals/fixtures/**' \
  ':(exclude)tests/fixtures/**' \
  ':(exclude)plugins/**'
mapfile -t tracked_markdown_files <"$tracked_markdown_list"

markdown_files=()
for path in "${tracked_markdown_files[@]}"; do
  if [[ -f "$path" ]]; then
    markdown_files+=("$path")
  fi
done

if [[ "${#markdown_files[@]}" -eq 0 ]]; then
  echo "No markdown files to check."
  exit 0
fi

lychee \
  --offline \
  --no-progress \
  --include-fragments \
  --root-dir "$REPO_ROOT" \
  "${markdown_files[@]}"
