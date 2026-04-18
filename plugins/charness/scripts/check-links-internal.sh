#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v lychee >/dev/null 2>&1; then
  cat >&2 <<'EOF'
lychee is required for link checking. Install one of:
  - cargo install lychee
  - brew install lychee
  - download from https://github.com/lycheeverse/lychee/releases
EOF
  exit 1
fi

mapfile -t markdown_files < <(
  git ls-files -- '*.md' \
    ':(exclude)charness-artifacts/**' \
    ':(exclude).charness/**' \
    ':(exclude)skills/support/specdown/**' \
    ':(exclude)plugins/charness/support/specdown/**' \
    ':(exclude).pytest_cache/**' \
    ':(exclude)evals/fixtures/**' \
    ':(exclude)plugins/**'
)

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
