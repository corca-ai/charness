#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "shellcheck unavailable; skipping shell lint." >&2
  exit 0
fi

listing_dir="$(mktemp -d)"
trap 'rm -rf "$listing_dir"' EXIT
listing_path="$listing_dir/shell-files.txt"
listing_stderr_path="$listing_dir/shell-files.stderr"

collect_shell_files() {
  find . -maxdepth 1 -type f -name '*.sh' || return "$?"
  find scripts -maxdepth 1 -type f -name '*.sh' || return "$?"
  if [[ -d .githooks ]]; then
    find .githooks -maxdepth 1 -type f || return "$?"
  fi
}

if collect_shell_files 2>"$listing_stderr_path" | sort >"$listing_path"; then
  mapfile -t sh_files <"$listing_path"
else
  rc=$?
  echo "check-shell: shell file discovery failed." >&2
  echo "command: { find . -maxdepth 1 -type f -name '*.sh'; find scripts -maxdepth 1 -type f -name '*.sh'; find .githooks -maxdepth 1 -type f when present; } | sort" >&2
  printf 'exit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$listing_path" >&2
  echo "STDERR:" >&2
  cat "$listing_stderr_path" >&2
  exit 1
fi

if [ "${#sh_files[@]}" -eq 0 ]; then
  exit 0
fi

shellcheck -x "${sh_files[@]}"
