#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. scripts/exported-copy-guard.sh carries the rule, the reasoning and
# the one implementation; what follows is this gate's own consequence.
#
# This gate already failed rather than passing from the mirror, so it was never a false green --
# but what it printed was `FTL unable to load gitleaks config, err: open
# .../plugins/charness/.gitleaks.toml: no such file or directory`, which names a missing file
# instead of the reason it is missing. The scanned population is cwd-scoped too, so if the
# config resolution were ever relaxed this would silently scan a narrower tree, and a narrowed
# secret scan is the one green in this repo that must never be wrong. Guarding it converts an
# archaeology-shaped diagnostic into the actual cause. Issue #618.
GATE_NAME="check-secrets"
GATE_CONSEQUENCE="This gate scans a git-tracked population and loads .gitleaks.toml from its root,
so a package root that is not the git root scans a narrower tree with no config."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-secrets: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

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

resolve_secrets_config() {
  local universe_payload config_path

  if ! config_path="$({
    python3 "$REPO_ROOT/scripts/adapters/quality_universes_lib.py" \
      --repo-root "$REPO_ROOT" \
      --key secrets_config \
      --format lines
  } 2>/dev/null)"; then
    # U0's landed CLI predates the keyed output flags required by the shared
    # contract. Keep this fallback until that CLI grows the narrow form.
    if ! universe_payload="$({
      python3 "$REPO_ROOT/scripts/adapters/quality_universes_lib.py" \
        --repo-root "$REPO_ROOT"
    })"; then
      echo "check-secrets: refusing to resolve the secrets_config universe." >&2
      exit 1
    fi
    config_path="$(printf '%s' "$universe_payload" | python3 -c '
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

payload_text = sys.stdin.read()
payload = yaml.safe_load(payload_text) if yaml is not None else json.loads(payload_text)
patterns = payload.get("secrets_config", {}).get("patterns", [])
if patterns:
    print(patterns[0])
')"
  fi
  if [[ -z "$config_path" ]]; then
    echo "check-secrets: refusing empty declared secrets_config universe." >&2
    exit 1
  fi
  if [[ "$config_path" != /* ]]; then
    config_path="$REPO_ROOT/$config_path"
  fi
  if [[ ! -f "$config_path" ]]; then
    echo "check-secrets: refusing missing secrets config: $config_path" >&2
    exit 1
  fi
  SECRETS_CONFIG_PATH="$config_path"
}

if command -v gitleaks >/dev/null 2>&1; then
  resolve_secrets_config
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    scan_dir="$(mktemp -d)"
    tracked_files_path="$scan_dir/tracked-files.zlist"
    existing_files_path="$scan_dir/existing-files.zlist"
    # `|| true` so a failed removal cannot restate this gate's verdict: `set -e` is in
    # force inside an EXIT trap, so an aborting `rm` replaces the pending status with its
    # own. Measured on run-quality.sh, where it turned a correct exit 2 into a 1.
    trap 'rm -rf "$scan_dir" || true' EXIT
    run_git_listing_to_file secret-scan-files "$tracked_files_path" \
      git ls-files -z --cached --others --exclude-standard
    filter_existing_file_list "$tracked_files_path" "$existing_files_path"
    if [[ ! -s "$existing_files_path" ]]; then
      echo "No tracked or unignored files to scan."
      exit 0
    fi
    if tar --null -T "$existing_files_path" -cf - | tar -xf - -C "$scan_dir"; then
      exec gitleaks dir \
        --config "$SECRETS_CONFIG_PATH" \
        --no-banner \
        --redact \
        "$scan_dir"
    fi
    echo "check-secrets: failed to stage git file listing for gitleaks scan." >&2
    exit 1
  fi

  exec gitleaks dir \
    --config "$SECRETS_CONFIG_PATH" \
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
    trap 'rm -rf "$secretlint_list_dir" || true' EXIT
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
