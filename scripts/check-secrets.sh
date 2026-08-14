#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. scripts/check-markdown.sh carries the canonical statement of this
# rule and the reasoning; this is the same guard with this gate's own consequence.
#
# This gate already failed rather than passing from the mirror, so it was never a false green --
# but what it printed was `FTL unable to load gitleaks config, err: open
# .../plugins/charness/.gitleaks.toml: no such file or directory`, which names a missing file
# instead of the reason it is missing. The scanned population is cwd-scoped too, so if the
# config resolution were ever relaxed this would silently scan a narrower tree, and a narrowed
# secret scan is the one green in this repo that must never be wrong. Guarding it converts an
# archaeology-shaped diagnostic into the actual cause. Issue #618.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
else
  git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_toplevel" && "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
    {
      echo "check-secrets: refusing to run from an exported copy."
      echo "  script root:  $REPO_ROOT"
      echo "  git toplevel: $git_toplevel"
      echo "This gate scans a git-tracked population and loads .gitleaks.toml from its root,"
      echo "so a package root that is not the git root scans a narrower tree with no config"
      echo "(issue #618)."
      echo "Run scripts/check-secrets.sh from the charness source checkout, or set"
      echo "CHARNESS_REPO_ROOT to that checkout."
    } >&2
    exit 1
  fi
fi
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
