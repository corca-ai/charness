#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.githooks"

if [[ ! -d "$HOOKS_DIR" ]]; then
  echo "Missing hook directory: $HOOKS_DIR" >&2
  exit 1
fi

git -C "$REPO_ROOT" config core.hooksPath "$HOOKS_DIR"
echo "Configured core.hooksPath -> $HOOKS_DIR"
echo "Installed hooks:"
find "$HOOKS_DIR" -maxdepth 1 -type f | sort
