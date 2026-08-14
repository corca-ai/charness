#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. scripts/check-markdown.sh carries the canonical statement of this
# rule and the reasoning; this is the same guard with this gate's own consequence.
#
# Measured from the generated mirror BEFORE this guard: exit 0, "97 Total / 78 OK / 0 Errors".
# A clean green over the wrong tree. Two things go wrong at once there: the
# `:(exclude)plugins/**` pathspec below is cwd-relative, so from `plugins/charness` it excludes
# NOTHING and the gate lints the mirror it is supposed to skip; and `--root-dir` then resolves
# every repo-relative link against the package root instead of the git root. Note this gate was
# predicted to "fail loud" from the mirror and does not -- it passes. Issue #618.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
else
  git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_toplevel" && "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
    {
      echo "check-links-internal: refusing to run from an exported copy."
      echo "  script root:  $REPO_ROOT"
      echo "  git toplevel: $git_toplevel"
      echo "This gate excludes plugins/** with a cwd-relative pathspec and resolves"
      echo "repo-relative links against its root, so a package root that is not the git root"
      echo "reports a clean pass over the mirror it should have skipped (issue #618)."
      echo "Run scripts/check-links-internal.sh from the charness source checkout, or set"
      echo "CHARNESS_REPO_ROOT to that checkout."
    } >&2
    exit 1
  fi
fi
cd "$REPO_ROOT"

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
trap 'rm -rf "$listing_dir"' EXIT
tracked_markdown_list="$listing_dir/tracked-markdown.txt"
run_git_listing_to_file tracked-markdown "$tracked_markdown_list" \
  git ls-files -- '*.md' \
  ':(exclude)charness-artifacts/**' \
  ':(exclude).charness/**' \
  ':(exclude).cautilus/**' \
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
