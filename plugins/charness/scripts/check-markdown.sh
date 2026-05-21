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

  echo "check-markdown: git file listing failed ($context)" >&2
  printf 'command:' >&2
  printf ' %q' "$@" >&2
  printf '\nexit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$output_path" >&2
  echo "STDERR:" >&2
  cat "$stderr_path" >&2
  return 1
}

if command -v markdownlint-cli2 >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(markdownlint-cli2)
elif command -v npm >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(npm exec -- markdownlint-cli2)
else
  echo "markdownlint-cli2 or npm is required for markdown linting." >&2
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
  ':(exclude).pytest_cache/**'
mapfile -t tracked_markdown_files <"$tracked_markdown_list"

markdown_files=()
for path in "${tracked_markdown_files[@]}"; do
  if [[ -f "$path" ]]; then
    markdown_files+=("$path")
  fi
done

if [ "${#markdown_files[@]}" -eq 0 ]; then
  echo "No tracked markdown files to lint."
  exit 0
fi

python3 "$REPO_ROOT/scripts/check_markdown_inline_code.py" --repo-root "$REPO_ROOT"
"${MARKDOWNLINT_CMD[@]}" --no-globs "${markdown_files[@]}"
