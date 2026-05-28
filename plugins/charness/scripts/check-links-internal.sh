#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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
