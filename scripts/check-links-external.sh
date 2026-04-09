#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v lychee >/dev/null 2>&1; then
  echo "lychee unavailable; skipping external link checks." >&2
  exit 0
fi

lychee --offline --no-progress --include-fragments .
