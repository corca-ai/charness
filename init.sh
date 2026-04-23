#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_ROOT="${HOME:?HOME must be set}"
MANAGED_CHECKOUT="${CHARNESS_MANAGED_CHECKOUT:-$HOME_ROOT/.agents/src/charness}"
REPO_URL="${CHARNESS_REPO_URL:-https://github.com/corca-ai/charness}"

select_python() {
  local candidate
  for candidate in "${CHARNESS_BOOTSTRAP_PYTHON:-}" python3 python; do
    if [ -n "$candidate" ] && command -v "$candidate" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

ensure_managed_checkout() {
  mkdir -p "$(dirname "$MANAGED_CHECKOUT")"
  if [ -d "$MANAGED_CHECKOUT/.git" ]; then
    return 0
  fi
  if [ -e "$MANAGED_CHECKOUT" ]; then
    echo "managed checkout path exists but is not a git checkout: $MANAGED_CHECKOUT" >&2
    exit 1
  fi

  local bootstrap_source="$REPO_URL"
  if [ -d "$SCRIPT_DIR/.git" ] && [ -f "$SCRIPT_DIR/packaging/charness.json" ] && [ -f "$SCRIPT_DIR/charness" ]; then
    bootstrap_source="$SCRIPT_DIR"
  fi

  git clone "$bootstrap_source" "$MANAGED_CHECKOUT"
}

ensure_managed_checkout
cd "$MANAGED_CHECKOUT"
if ! PYTHON_CMD="$(select_python)"; then
  echo "charness bootstrap requires Python 3.10+ (`python3` or `python`) plus the stdlib \`venv\` module." >&2
  exit 1
fi
BOOTSTRAP_PYTHON="$("$PYTHON_CMD" scripts/bootstrap_runtime.py --repo-root "$MANAGED_CHECKOUT" --base-python "$PYTHON_CMD" --print-python)"
if [ -z "$BOOTSTRAP_PYTHON" ]; then
  echo "bootstrap runtime helper did not return a Python executable" >&2
  exit 1
fi
exec "$BOOTSTRAP_PYTHON" ./charness init "$@"
