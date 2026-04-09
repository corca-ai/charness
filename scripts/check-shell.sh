#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "shellcheck unavailable; skipping shell lint." >&2
  exit 0
fi

mapfile -t sh_files < <(find scripts -maxdepth 1 -type f -name '*.sh' | sort)
if [ "${#sh_files[@]}" -eq 0 ]; then
  exit 0
fi

shellcheck -x "${sh_files[@]}"
