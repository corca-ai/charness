#!/usr/bin/env bash
# Source this file from any Charness-owned shell entrypoint before starting Python or
# another cache-writing tool. It is the single shell-compatible owner of runtime
# isolation; hooks are only one consumer. The Python bootstrap repairs the same
# settings after import because an interpreter can write its first __pycache__ before
# Python code runs.

if [[ -z "${REPO_ROOT:-}" ]]; then
  echo "charness runtime-env: REPO_ROOT must be set by the calling hook" >&2
  return 2
fi

# Git exports repository-discovery variables to hooks.  If a hook launches pytest,
# those variables leak into fixture subprocesses and make their throwaway `git init`
# or `git config` operate on the hook's repository instead (observed during release:
# fixture commits moved the release branch and made the source look deleted).  The
# runtime owner is the one place every Charness shell entrypoint reaches, so clear
# the hook context before any child command can inherit it.  `REPO_ROOT` survives as
# the explicit checkout identity; later git commands rediscover it from that root.
while IFS= read -r git_environment_name; do
  [[ -z "$git_environment_name" ]] || unset "$git_environment_name"
done < <(git -C "$REPO_ROOT" rev-parse --local-env-vars 2>/dev/null || true)

RUNTIME_TMP_BASE="${TMPDIR:-/tmp}"
case "$RUNTIME_TMP_BASE" in
  "$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) RUNTIME_TMP_BASE="/tmp" ;;
esac

RUNTIME_REPO_KEY="$(printf '%s' "$REPO_ROOT" | sha256sum | cut -c1-16)"
RUNTIME_CONFIGURED_ROOT="${CHARNESS_RUNTIME_ROOT:-}"
if [[ -z "$RUNTIME_CONFIGURED_ROOT" || "${CHARNESS_RUNTIME_ROOT_AUTO:-}" == "1" && "${CHARNESS_RUNTIME_REPO_KEY:-}" != "$RUNTIME_REPO_KEY" ]]; then
  RUNTIME_CONFIGURED_ROOT="$RUNTIME_TMP_BASE/charness-runtime/$RUNTIME_REPO_KEY"
  export CHARNESS_RUNTIME_ROOT_AUTO=1
  export CHARNESS_RUNTIME_REPO_KEY="$RUNTIME_REPO_KEY"
else
  case "$RUNTIME_CONFIGURED_ROOT" in
    "$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*)
      RUNTIME_CONFIGURED_ROOT="$RUNTIME_TMP_BASE/charness-runtime/$RUNTIME_REPO_KEY"
      export CHARNESS_RUNTIME_ROOT_AUTO=1
      export CHARNESS_RUNTIME_REPO_KEY="$RUNTIME_REPO_KEY"
      ;;
    *)
      unset CHARNESS_RUNTIME_ROOT_AUTO CHARNESS_RUNTIME_REPO_KEY
      ;;
  esac
fi
export CHARNESS_RUNTIME_ROOT="$RUNTIME_CONFIGURED_ROOT"

case "${PYTHONPYCACHEPREFIX:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export PYTHONPYCACHEPREFIX="$RUNTIME_CONFIGURED_ROOT/pycache" ;;
esac
case "${TMPDIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export TMPDIR="$RUNTIME_CONFIGURED_ROOT/tmp" ;;
esac
case "${PYTEST_DEBUG_TEMPROOT:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export PYTEST_DEBUG_TEMPROOT="$RUNTIME_CONFIGURED_ROOT/pytest-tmp" ;;
esac
case "${CHARNESS_PYTEST_CACHE_DIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export CHARNESS_PYTEST_CACHE_DIR="$RUNTIME_CONFIGURED_ROOT/pytest-cache" ;;
esac
case "${RUFF_CACHE_DIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export RUFF_CACHE_DIR="$RUNTIME_CONFIGURED_ROOT/ruff" ;;
esac
case "${COVERAGE_FILE:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export COVERAGE_FILE="$RUNTIME_CONFIGURED_ROOT/coverage/.coverage" ;;
esac

case "${TMP:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export TMP="$TMPDIR" ;;
esac
case "${TEMP:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export TEMP="$TMPDIR" ;;
esac
case "${XDG_CACHE_HOME:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export XDG_CACHE_HOME="$RUNTIME_CONFIGURED_ROOT/xdg-cache" ;;
esac
case "${PIP_CACHE_DIR:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export PIP_CACHE_DIR="$RUNTIME_CONFIGURED_ROOT/pip" ;;
esac
case "${NPM_CONFIG_CACHE:-}" in
  ""|"$REPO_ROOT"|"$REPO_ROOT"/*|[^/]*) export NPM_CONFIG_CACHE="$RUNTIME_CONFIGURED_ROOT/npm" ;;
esac
export npm_config_cache="$NPM_CONFIG_CACHE"

# pytest has no standard cache environment variable. Carry the one override into
# every child of a Charness-owned shell command; an explicit later CLI option can
# still override it. Avoid adding the exact option twice when the Python bootstrap
# repairs the same process or a nested Charness entrypoint is called.
RUNTIME_PYTEST_CACHE_OPTION="-o $(printf '%q' "cache_dir=$CHARNESS_PYTEST_CACHE_DIR")"
case " ${PYTEST_ADDOPTS:-} " in
  *" $RUNTIME_PYTEST_CACHE_OPTION "*) ;;
  *) export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:+$PYTEST_ADDOPTS }$RUNTIME_PYTEST_CACHE_OPTION" ;;
esac

mkdir -p -- "$CHARNESS_RUNTIME_ROOT" "$PYTHONPYCACHEPREFIX" "$TMPDIR" \
  "$PYTEST_DEBUG_TEMPROOT" "$CHARNESS_PYTEST_CACHE_DIR" "$RUFF_CACHE_DIR" \
  "$XDG_CACHE_HOME" "$PIP_CACHE_DIR" "$NPM_CONFIG_CACHE"
if [[ "$COVERAGE_FILE" != :memory: ]]; then
  mkdir -p -- "$(dirname "$COVERAGE_FILE")"
fi
