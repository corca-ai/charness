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

RUN_QUALITY_REVIEW=0
for arg in "$@"; do
  case "$arg" in
    --review)
      RUN_QUALITY_REVIEW=1
      ;;
    --help|-h)
      echo "Usage: ./scripts/run-quality.sh [--review]"
      echo "  --review  replay passing phase logs and validate external links online"
      exit 0
      ;;
    *)
      echo "run-quality: unknown argument $arg" >&2
      exit 2
      ;;
  esac
done

RUN_QUALITY_TMPDIR="$(mktemp -d)"
trap 'rm -rf "$RUN_QUALITY_TMPDIR"' EXIT

RUN_QUALITY_VERBOSE="${CHARNESS_QUALITY_VERBOSE:-0}"
RUN_QUALITY_LABELS="${CHARNESS_QUALITY_LABELS:-}"
RUN_QUALITY_RUNTIME_PROFILE="${CHARNESS_RUNTIME_PROFILE:-}"
RUN_QUALITY_START_NS="$(date +%s%N)"

if [[ "$RUN_QUALITY_REVIEW" == "1" ]]; then
  RUN_QUALITY_VERBOSE=1
  export CHARNESS_LINK_CHECK_ONLINE=1
fi

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

uppercase_status() {
  case "$1" in
    pass) printf 'PASS' ;;
    fail) printf 'FAIL' ;;
    *) printf '%s' "$1" ;;
  esac
}

collect_quality_changed_paths() {
  local upstream_ref merge_base

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 1
  fi

  if upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)"; then
    if merge_base="$(git merge-base HEAD "$upstream_ref" 2>/dev/null)"; then
      git diff --name-only "$merge_base"...HEAD || true
    fi
  fi

  git diff --name-only || true
  git diff --name-only --cached || true
  git ls-files --others --exclude-standard || true
}

coverage_relevant_changes_present() {
  local path

  if [[ -n "$RUN_QUALITY_LABELS" ]]; then
    return 0
  fi

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi

  while IFS= read -r path; do
    case "$path" in
      scripts/control_plane_lib.py|scripts/control_plane_lifecycle_lib.py|scripts/doctor.py|scripts/install_provenance_lib.py|scripts/install_tools.py|scripts/support_sync_lib.py|scripts/sync_support.py|scripts/update_tools.py|scripts/upstream_release_lib.py|scripts/check_coverage.py|scripts/check_coverage_lib.py|scripts/check_coverage_extra_lib.py|tests/control_plane/*|tests/quality_gates/test_check_coverage_inventory.py)
        return 0
        ;;
    esac
  done < <(collect_quality_changed_paths)

  return 1
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

  printf '%s %-24s %s\n' "$(uppercase_status "$status")" "$label" "$(format_elapsed "$elapsed_ms")"

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

  if ((${#PHASE_LABELS[@]} == 0)); then
    return 0
  fi

  for pid in "${PHASE_PIDS[@]}"; do
    wait "$pid" || true
  done

  for i in "${!PHASE_LABELS[@]}"; do
    label="${PHASE_LABELS[$i]}"
    log_path="${PHASE_LOGS[$i]}"
    meta_path="${PHASE_METAS[$i]}"

    meta_lines=()
    while IFS= read -r meta_line; do
      meta_lines+=("$meta_line")
    done <"$meta_path"
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

queue_selected "validate-skills" python3 scripts/validate_skills.py --repo-root "$REPO_ROOT"
queue_selected "validate-skill-ergonomics" python3 scripts/validate_skill_ergonomics.py --repo-root "$REPO_ROOT"
queue_selected "check-cli-skill-surface" python3 scripts/check_cli_skill_surface.py --repo-root "$REPO_ROOT" --run-probes
queue_selected "validate-surfaces" python3 scripts/validate_surfaces.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-validation" python3 scripts/validate_public_skill_validation.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-dogfood" python3 scripts/validate_public_skill_dogfood.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-scenarios" python3 scripts/validate_cautilus_scenarios.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-proof" python3 scripts/validate_cautilus_proof.py --repo-root "$REPO_ROOT"
queue_selected "validate-profiles" python3 scripts/validate_profiles.py --repo-root "$REPO_ROOT"
queue_selected "validate-presets" python3 scripts/validate_presets.py --repo-root "$REPO_ROOT"
queue_selected "validate-adapters" python3 scripts/validate_adapters.py --repo-root "$REPO_ROOT"
queue_selected "validate-integrations" python3 scripts/validate_integrations.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging" python3 scripts/validate_packaging.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging-committed" python3 scripts/validate_packaging_committed.py --repo-root "$REPO_ROOT"
queue_selected "validate-handoff-artifact" python3 scripts/validate_handoff_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-artifact" python3 scripts/validate_debug_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-seam-index" python3 scripts/build_debug_seam_risk_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-retro-lesson-index" python3 scripts/build_retro_lesson_selection_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-quality-artifact" python3 scripts/validate_quality_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-closeout-contract" python3 scripts/validate_quality_closeout_contract.py --repo-root "$REPO_ROOT"
queue_selected "validate-current-pointer-freshness" python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"
queue_selected "inventory-quality-handoff" python3 scripts/inventory_quality_handoff.py --repo-root "$REPO_ROOT"
queue_selected "validate-maintainer-setup" python3 scripts/validate_maintainer_setup.py --repo-root "$REPO_ROOT"
queue_selected "check-python-lengths" python3 scripts/check_python_lengths.py --repo-root "$REPO_ROOT"
queue_selected "check-python-filenames" python3 scripts/check_python_filenames.py --repo-root "$REPO_ROOT"
queue_selected "check-python-runtime-inheritance" python3 scripts/check_python_runtime_inheritance.py --repo-root "$REPO_ROOT"
queue_selected "check-skill-contracts" python3 scripts/check_skill_contracts.py --repo-root "$REPO_ROOT"
queue_selected "check-export-safe-imports" python3 scripts/check_export_safe_imports.py --repo-root "$REPO_ROOT"
queue_selected "check-plugin-import-smoke" python3 scripts/check_plugin_import_smoke.py --repo-root "$REPO_ROOT"
queue_selected "check-command-docs" python3 scripts/check_command_docs.py --repo-root "$REPO_ROOT"
queue_selected "check-doc-links" python3 scripts/check_doc_links.py --repo-root "$REPO_ROOT"
queue_selected "check-markdown" ./scripts/check-markdown.sh
flush_phase || OVERALL_RC=$?

queue_selected "check-secrets" ./scripts/check-secrets.sh
queue_selected "check-supply-chain" python3 scripts/check_supply_chain.py --repo-root "$REPO_ROOT"
queue_selected "check-github-actions" python3 scripts/check_github_actions.py --repo-root "$REPO_ROOT"
if [[ "${CHARNESS_SUPPLY_CHAIN_ONLINE:-0}" == "1" ]]; then
  queue_selected "check-supply-chain-online" python3 scripts/check_supply_chain_online.py --repo-root "$REPO_ROOT" --triage-owner "repo-maintainers"
fi
queue_selected "check-shell" ./scripts/check-shell.sh
queue_selected "check-links-internal" ./scripts/check-links-internal.sh
queue_selected "check-links-external" ./scripts/check-links-external.sh
shopt -s nullglob
python_files=(
  scripts/*.py
  skills/public/*/scripts/*.py
  skills/support/*/scripts/*.py
  skills/support/*/vendor/*.py
)
queue_selected "py-compile" python3 -m py_compile "${python_files[@]}"
queue_selected "ruff" ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts
flush_phase || OVERALL_RC=$?

PYTEST_CMD=(pytest)
if python3 -m pytest --version >/dev/null 2>&1; then
  PYTEST_CMD=(python3 -m pytest)
fi

PYTEST_PARALLEL_FLAGS=()
PYTEST_HELP="$("${PYTEST_CMD[@]}" --help 2>/dev/null || true)"
if grep -q -- "--numprocesses" <<<"$PYTEST_HELP"; then
  PYTEST_PARALLEL_FLAGS=(-n auto)
else
  echo "run-quality: pytest-xdist not installed; pytest will run serially and may exceed runtime budgets. Install with: pip install pytest-xdist" >&2
fi
if ((${#PYTEST_PARALLEL_FLAGS[@]})); then
  queue_selected "pytest" "${PYTEST_CMD[@]}" -q -m "not ci_only" "${PYTEST_PARALLEL_FLAGS[@]}" "${STANDING_PYTEST_TARGETS[@]}"
else
  queue_selected "pytest" "${PYTEST_CMD[@]}" -q -m "not ci_only" "${STANDING_PYTEST_TARGETS[@]}"
fi
if coverage_relevant_changes_present; then
  queue_selected "check-coverage" python3 scripts/check_coverage.py --repo-root "$REPO_ROOT"
fi
queue_selected "check-test-completeness" python3 scripts/check_test_completeness.py --repo-root "$REPO_ROOT" -- "${STANDING_PYTEST_TARGETS[@]}"
queue_selected "check-test-production-ratio" python3 scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT"
queue_selected "specdown" bash -c 'command -v specdown >/dev/null || { echo "specdown is required for executable specs. Install from https://github.com/corca-ai/specdown or run charness tool doctor specdown --json for current readiness."; exit 1; }; specdown run -quiet -no-report'
queue_selected "run-evals" python3 scripts/run_evals.py --repo-root "$REPO_ROOT"
queue_selected "check-duplicates" python3 scripts/check_duplicates.py --repo-root "$REPO_ROOT" --fail-on-match
flush_phase || OVERALL_RC=$?

queue_selected "measure-startup-probes" python3 skills/public/quality/scripts/measure_startup_probes.py --repo-root "$REPO_ROOT" --class standing --record-runtime-signals
flush_phase || OVERALL_RC=$?

if [[ -n "$RUN_QUALITY_RUNTIME_PROFILE" ]]; then
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT" --runtime-profile "$RUN_QUALITY_RUNTIME_PROFILE"
else
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT"
fi
flush_phase || OVERALL_RC=$?
print_final_summary
exit "$OVERALL_RC"
