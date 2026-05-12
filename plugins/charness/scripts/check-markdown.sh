#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if command -v markdownlint-cli2 >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(markdownlint-cli2)
elif command -v npm >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(npm exec -- markdownlint-cli2)
else
  echo "markdownlint-cli2 or npm is required for markdown linting." >&2
  exit 1
fi

mapfile -t tracked_markdown_files < <(
  git ls-files -- '*.md' \
    ':(exclude)charness-artifacts/**' \
    ':(exclude).charness/**' \
    ':(exclude).cautilus/**' \
    ':(exclude).pytest_cache/**'
)

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
