#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if command -v gitleaks >/dev/null 2>&1; then
  exec gitleaks dir \
    --config "$REPO_ROOT/.gitleaks.toml" \
    --no-banner \
    --redact \
    "$REPO_ROOT"
fi

if command -v npm >/dev/null 2>&1; then
  exec npm exec --no-install -- secretlint "**/*" --secretlintignore .secretlintignore
fi

echo "secret scanning requires either gitleaks or repo-local secretlint via npm." >&2
exit 1
