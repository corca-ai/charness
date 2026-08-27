#!/usr/bin/env bash
# Source this file from git hooks before starting Python or another cache-writing tool.
# The Python bootstrap repairs the same settings after import; this early shell layer
# exists because the interpreter can write its first __pycache__ before Python code runs.

if [[ -z "${REPO_ROOT:-}" ]]; then
  echo "charness runtime-env: REPO_ROOT must be set by the calling hook" >&2
  return 2
fi

HOOK_TMP_BASE="${TMPDIR:-/tmp}"
case "$HOOK_TMP_BASE" in
  "$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) HOOK_TMP_BASE="/tmp" ;;
esac

HOOK_REPO_KEY="$(printf '%s' "$REPO_ROOT" | sha256sum | cut -c1-16)"
HOOK_CONFIGURED_ROOT="${CHARNESS_RUNTIME_ROOT:-}"
if [[ -z "$HOOK_CONFIGURED_ROOT" || "${CHARNESS_RUNTIME_ROOT_AUTO:-}" == "1" && "${CHARNESS_RUNTIME_REPO_KEY:-}" != "$HOOK_REPO_KEY" ]]; then
  HOOK_CONFIGURED_ROOT="$HOOK_TMP_BASE/charness-runtime/$HOOK_REPO_KEY"
  export CHARNESS_RUNTIME_ROOT_AUTO=1
  export CHARNESS_RUNTIME_REPO_KEY="$HOOK_REPO_KEY"
else
  case "$HOOK_CONFIGURED_ROOT" in
    "$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*)
      HOOK_CONFIGURED_ROOT="$HOOK_TMP_BASE/charness-runtime/$HOOK_REPO_KEY"
      export CHARNESS_RUNTIME_ROOT_AUTO=1
      export CHARNESS_RUNTIME_REPO_KEY="$HOOK_REPO_KEY"
      ;;
    *)
      unset CHARNESS_RUNTIME_ROOT_AUTO CHARNESS_RUNTIME_REPO_KEY
      ;;
  esac
fi
export CHARNESS_RUNTIME_ROOT="$HOOK_CONFIGURED_ROOT"

case "${PYTHONPYCACHEPREFIX:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export PYTHONPYCACHEPREFIX="$HOOK_CONFIGURED_ROOT/pycache" ;;
esac
case "${TMPDIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export TMPDIR="$HOOK_CONFIGURED_ROOT/tmp" ;;
esac
case "${PYTEST_DEBUG_TEMPROOT:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export PYTEST_DEBUG_TEMPROOT="$HOOK_CONFIGURED_ROOT/pytest-tmp" ;;
esac
case "${CHARNESS_PYTEST_CACHE_DIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export CHARNESS_PYTEST_CACHE_DIR="$HOOK_CONFIGURED_ROOT/pytest-cache" ;;
esac
case "${RUFF_CACHE_DIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export RUFF_CACHE_DIR="$HOOK_CONFIGURED_ROOT/ruff" ;;
esac
case "${COVERAGE_FILE:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export COVERAGE_FILE="$HOOK_CONFIGURED_ROOT/coverage/.coverage" ;;
esac

mkdir -p -- "$CHARNESS_RUNTIME_ROOT" "$PYTHONPYCACHEPREFIX" "$TMPDIR" \
  "$PYTEST_DEBUG_TEMPROOT" "$CHARNESS_PYTEST_CACHE_DIR" "$RUFF_CACHE_DIR"
if [[ "$COVERAGE_FILE" != :memory: ]]; then
  mkdir -p -- "$(dirname "$COVERAGE_FILE")"
fi
