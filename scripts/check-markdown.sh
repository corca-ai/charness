#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required for markdownlint-cli2." >&2
  exit 1
fi

mapfile -t markdown_files < <(
  git ls-files -- '*.md' \
    ':(exclude)skill-outputs/**' \
    ':(exclude)skills/support/specdown/**' \
    ':(exclude)plugins/charness/support/specdown/**' \
    ':(exclude).pytest_cache/**'
)

if [ "${#markdown_files[@]}" -eq 0 ]; then
  echo "No tracked markdown files to lint."
  exit 0
fi

npm exec -- markdownlint-cli2 --no-globs "${markdown_files[@]}"
