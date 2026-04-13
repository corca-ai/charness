#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

STANDING_PYTEST_TARGETS=(
  tests/quality_gates
  tests/control_plane
  tests/test_*.py
  tests/charness_cli
)

RUN_QUALITY_TMPDIR="$(mktemp -d)"
trap 'rm -rf "$RUN_QUALITY_TMPDIR"' EXIT

RUN_QUALITY_VERBOSE="${CHARNESS_QUALITY_VERBOSE:-0}"
RUN_QUALITY_LABELS="${CHARNESS_QUALITY_LABELS:-}"
RUN_QUALITY_START_NS="$(date +%s%N)"

declare -a PHASE_LABELS=()
declare -a PHASE_PIDS=()
declare -a PHASE_LOGS=()
declare -a PHASE_METAS=()
declare -a COMPLETED_LABELS=()
declare -a COMPLETED_ELAPSED_MS=()
declare -a COMPLETED_STATUSES=()

TOTAL_PASSES=0
TOTAL_FAILURES=0
OVERALL_RC=0

format_elapsed() {
  local elapsed_ms="$1"

  if (( elapsed_ms >= 1000 )); then
    printf '%s.%ss' "$((elapsed_ms / 1000))" "$(((elapsed_ms % 1000) / 100))"
    return
  fi

  printf '%sms' "$elapsed_ms"
}

record_runtime() {
  local label="$1"
  local elapsed_ms="$2"
  local status="$3"
  local timestamp="$4"
  python3 scripts/record_quality_runtime.py \
    --repo-root "$REPO_ROOT" \
    --label "$label" \
    --elapsed-ms "$elapsed_ms" \
    --status "$status" \
    --timestamp "$timestamp" >/dev/null
}

queue_timed() {
  local label="$1"
  shift
  local slug="${label//[^A-Za-z0-9_.-]/_}"
  local log_path="$RUN_QUALITY_TMPDIR/${slug}.log"
  local meta_path="$RUN_QUALITY_TMPDIR/${slug}.meta"

  (
    local start_ns end_ns elapsed_ms rc status timestamp
    start_ns="$(date +%s%N)"
    if "$@" >"$log_path" 2>&1; then
      rc=0
      status="pass"
    else
      rc=$?
      status="fail"
    fi
    end_ns="$(date +%s%N)"
    elapsed_ms="$(((end_ns - start_ns) / 1000000))"
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf '%s\n%s\n%s\n%s\n' "$elapsed_ms" "$status" "$timestamp" "$rc" >"$meta_path"
    exit 0
  ) &

  PHASE_LABELS+=("$label")
  PHASE_PIDS+=("$!")
  PHASE_LOGS+=("$log_path")
  PHASE_METAS+=("$meta_path")
}

label_is_selected() {
  local label="$1"
  local raw selected_label

  if [[ -z "$RUN_QUALITY_LABELS" ]]; then
    return 0
  fi

  IFS=',' read -r -a raw <<< "$RUN_QUALITY_LABELS"
  for selected_label in "${raw[@]}"; do
    selected_label="${selected_label#"${selected_label%%[![:space:]]*}"}"
    selected_label="${selected_label%"${selected_label##*[![:space:]]}"}"
    if [[ "$selected_label" == "$label" ]]; then
      return 0
    fi
  done

  return 1
}

queue_selected() {
  local label="$1"
  shift

  if ! label_is_selected "$label"; then
    return 0
  fi

  queue_timed "$label" "$@"
}

print_phase_output() {
  local label="$1"
  local status="$2"
  local elapsed_ms="$3"
  local log_path="$4"

  printf '%s %-24s %s\n' "${status^^}" "$label" "$(format_elapsed "$elapsed_ms")"

  if [[ "$status" == "fail" || "$RUN_QUALITY_VERBOSE" == "1" ]]; then
    if [[ -s "$log_path" ]]; then
      printf -- '--- %s output ---\n' "$label"
      cat "$log_path"
    else
      printf -- '--- %s output ---\n(no output)\n' "$label"
    fi
  fi
}

flush_phase() {
  local rc=0
  local pid label log_path meta_path elapsed_ms status timestamp cmd_rc
  local -a meta_lines

  for pid in "${PHASE_PIDS[@]}"; do
    wait "$pid" || true
  done

  for i in "${!PHASE_LABELS[@]}"; do
    label="${PHASE_LABELS[$i]}"
    log_path="${PHASE_LOGS[$i]}"
    meta_path="${PHASE_METAS[$i]}"

    mapfile -t meta_lines <"$meta_path"
    elapsed_ms="${meta_lines[0]}"
    status="${meta_lines[1]}"
    timestamp="${meta_lines[2]}"
    cmd_rc="${meta_lines[3]}"
    record_runtime "$label" "$elapsed_ms" "$status" "$timestamp"

    print_phase_output "$label" "$status" "$elapsed_ms" "$log_path"
    COMPLETED_LABELS+=("$label")
    COMPLETED_ELAPSED_MS+=("$elapsed_ms")
    COMPLETED_STATUSES+=("$status")
    if [[ "$status" == "pass" ]]; then
      TOTAL_PASSES=$((TOTAL_PASSES + 1))
    else
      TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
    fi

    if [[ "$cmd_rc" != "0" ]]; then
      rc="$cmd_rc"
    fi
  done

  PHASE_LABELS=()
  PHASE_PIDS=()
  PHASE_LOGS=()
  PHASE_METAS=()
  return "$rc"
}

print_final_summary() {
  local end_ns elapsed_ms

  end_ns="$(date +%s%N)"
  elapsed_ms="$(((end_ns - RUN_QUALITY_START_NS) / 1000000))"
  printf 'Quality summary: %s passed, %s failed, total %s\n' \
    "$TOTAL_PASSES" \
    "$TOTAL_FAILURES" \
    "$(format_elapsed "$elapsed_ms")"
}

queue_selected "validate-skills" python3 scripts/validate-skills.py --repo-root "$REPO_ROOT"
queue_selected "validate-surfaces" python3 scripts/validate-surfaces.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-validation" python3 scripts/validate-public-skill-validation.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-scenarios" python3 scripts/validate-cautilus-scenarios.py --repo-root "$REPO_ROOT"
queue_selected "validate-profiles" python3 scripts/validate-profiles.py --repo-root "$REPO_ROOT"
queue_selected "validate-presets" python3 scripts/validate-presets.py --repo-root "$REPO_ROOT"
queue_selected "validate-adapters" python3 scripts/validate-adapters.py --repo-root "$REPO_ROOT"
queue_selected "validate-integrations" python3 scripts/validate-integrations.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging" python3 scripts/validate-packaging.py --repo-root "$REPO_ROOT"
queue_selected "validate-handoff-artifact" python3 scripts/validate-handoff-artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-artifact" python3 scripts/validate-debug-artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-artifact" python3 scripts/validate-quality-artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-maintainer-setup" python3 scripts/validate-maintainer-setup.py --repo-root "$REPO_ROOT"
queue_selected "check-python-lengths" python3 scripts/check-python-lengths.py --repo-root "$REPO_ROOT"
queue_selected "check-skill-contracts" python3 scripts/check-skill-contracts.py --repo-root "$REPO_ROOT"
queue_selected "check-doc-links" python3 scripts/check-doc-links.py --repo-root "$REPO_ROOT"
flush_phase || OVERALL_RC=$?

queue_selected "check-markdown" ./scripts/check-markdown.sh
queue_selected "check-secrets" ./scripts/check-secrets.sh
queue_selected "check-supply-chain" python3 scripts/check-supply-chain.py --repo-root "$REPO_ROOT"
queue_selected "check-github-actions" python3 scripts/check-github-actions.py --repo-root "$REPO_ROOT"
if [[ "${CHARNESS_SUPPLY_CHAIN_ONLINE:-0}" == "1" ]]; then
  queue_selected "check-supply-chain-online" python3 scripts/check-supply-chain-online.py --repo-root "$REPO_ROOT" --triage-owner "repo-maintainers"
fi
queue_selected "check-shell" ./scripts/check-shell.sh
queue_selected "check-links-external" ./scripts/check-links-external.sh
shopt -s nullglob
python_files=(
  scripts/*.py
  skills/public/*/scripts/*.py
  skills/support/*/scripts/*.py
  skills/support/*/vendor/*.py
)
queue_selected "py-compile" python3 -m py_compile "${python_files[@]}"
queue_selected "ruff" ruff check scripts tests skills/public/*/scripts skills/support/*/scripts
flush_phase || OVERALL_RC=$?

queue_selected "pytest" pytest -q "${STANDING_PYTEST_TARGETS[@]}"
queue_selected "run-evals" python3 scripts/run-evals.py --repo-root "$REPO_ROOT"
queue_selected "check-duplicates" python3 scripts/check-duplicates.py --repo-root "$REPO_ROOT" --fail-on-match
queue_selected "check-coverage" python3 scripts/check-coverage.py --repo-root "$REPO_ROOT"
flush_phase || OVERALL_RC=$?
print_final_summary
exit "$OVERALL_RC"
