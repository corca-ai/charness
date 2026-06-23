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

  echo "check-secrets: git file listing failed ($context)" >&2
  printf 'command:' >&2
  printf ' %q' "$@" >&2
  printf '\nexit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$output_path" >&2
  echo "STDERR:" >&2
  cat "$stderr_path" >&2
  return 1
}

filter_existing_file_list() {
  local input_path="$1"
  local output_path="$2"
  local listed_file

  : >"$output_path"
  while IFS= read -r -d '' listed_file; do
    if [[ -e "$listed_file" || -L "$listed_file" ]]; then
      printf '%s\0' "$listed_file" >>"$output_path"
    fi
  done <"$input_path"
}

if command -v gitleaks >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    scan_dir="$(mktemp -d)"
    tracked_files_path="$scan_dir/tracked-files.zlist"
    existing_files_path="$scan_dir/existing-files.zlist"
    trap 'rm -rf "$scan_dir"' EXIT
    run_git_listing_to_file secret-scan-files "$tracked_files_path" \
      git ls-files -z --cached --others --exclude-standard
    filter_existing_file_list "$tracked_files_path" "$existing_files_path"
    if [[ ! -s "$existing_files_path" ]]; then
      echo "No tracked or unignored files to scan."
      exit 0
    fi
    if tar --null -T "$existing_files_path" -cf - | tar -xf - -C "$scan_dir"; then
      exec gitleaks dir \
        --config "$REPO_ROOT/.gitleaks.toml" \
        --no-banner \
        --redact \
        "$scan_dir"
    fi
    echo "check-secrets: failed to stage git file listing for gitleaks scan." >&2
    exit 1
  fi

  exec gitleaks dir \
    --config "$REPO_ROOT/.gitleaks.toml" \
    --no-banner \
    --redact \
    "$REPO_ROOT"
fi

echo "check-secrets: gitleaks not found, falling back to secretlint via npm (~5s vs sub-1s). Install gitleaks for the fast path from https://github.com/gitleaks/gitleaks#installing" >&2

if command -v npm >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    secretlint_files=()
    secretlint_list_dir="$(mktemp -d)"
    secretlint_list_path="$secretlint_list_dir/tracked-files.zlist"
    secretlint_existing_list_path="$secretlint_list_dir/existing-files.zlist"
    trap 'rm -rf "$secretlint_list_dir"' EXIT
    run_git_listing_to_file secretlint-files "$secretlint_list_path" \
      git ls-files -z --cached --others --exclude-standard
    filter_existing_file_list "$secretlint_list_path" "$secretlint_existing_list_path"
    while IFS= read -r -d '' secretlint_file; do
      secretlint_files+=("$secretlint_file")
    done <"$secretlint_existing_list_path"
    if ((${#secretlint_files[@]} == 0)); then
      echo "No tracked or unignored files to scan."
      exit 0
    fi
    exec npm exec --no-install -- secretlint --secretlintignore .secretlintignore "${secretlint_files[@]}"
  fi

  exec npm exec --no-install -- secretlint --secretlintignore .secretlintignore "**/*"
fi

echo "secret scanning requires either gitleaks or repo-local secretlint via npm." >&2
exit 1
