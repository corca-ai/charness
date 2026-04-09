#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required for secretlint." >&2
  exit 1
fi

npm exec -- secretlint "**/*" --secretlintignore .secretlintignore
