#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

STANDING_PYTEST_TARGETS_TEXT="$(python3 scripts/run_standing_pytest.py --repo-root "$REPO_ROOT" --print-expanded-targets)"
mapfile -t STANDING_PYTEST_TARGETS <<<"$STANDING_PYTEST_TARGETS_TEXT"

RUN_QUALITY_REVIEW=0
RUN_QUALITY_MODE="${CHARNESS_QUALITY_MODE:-full}"
RUN_QUALITY_INCLUDE_RELEASE_ONLY="${CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY:-0}"
for arg in "$@"; do
  case "$arg" in
    --review)
      RUN_QUALITY_REVIEW=1
      ;;
    --read-only)
      RUN_QUALITY_MODE="read-only"
      ;;
    --full)
      RUN_QUALITY_MODE="full"
      ;;
    --release)
      RUN_QUALITY_INCLUDE_RELEASE_ONLY=1
      ;;
    --help|-h)
      echo "Usage: ./scripts/run-quality.sh [--review] [--read-only|--full] [--release]"
      echo "  --review     replay passing phase logs and validate external links online"
      echo "  --read-only  skip phases that would mutate git-tracked quality artifacts"
      echo "  --full       refresh git-tracked quality artifacts (default)"
      echo "  --release    include release_only pytest cases (charness update/install lifecycle regression tests)"
      exit 0
      ;;
    *)
      echo "run-quality: unknown argument $arg" >&2
      exit 2
      ;;
  esac
done

case "$RUN_QUALITY_MODE" in
  full|read-only) ;;
  *)
    echo "run-quality: CHARNESS_QUALITY_MODE must be 'full' or 'read-only', got '$RUN_QUALITY_MODE'" >&2
    exit 2
    ;;
esac
export CHARNESS_QUALITY_MODE="$RUN_QUALITY_MODE"

RUN_QUALITY_TMPDIR="$(mktemp -d)"
trap 'rm -rf "$RUN_QUALITY_TMPDIR"' EXIT

RUN_QUALITY_VERBOSE="${CHARNESS_QUALITY_VERBOSE:-0}"
RUN_QUALITY_LABELS="${CHARNESS_QUALITY_LABELS:-}"
RUN_QUALITY_RUNTIME_PROFILE="${CHARNESS_RUNTIME_PROFILE:-}"
RUN_QUALITY_START_NS="$(date +%s%N)"
PYTEST_DEBUG_TEMPROOT="$(python3 scripts/run_standing_pytest.py --repo-root "$REPO_ROOT" --print-temp-root)"
export PYTEST_DEBUG_TEMPROOT

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

run_changed_path_git() {
  local context="$1"
  shift
  local stdout_path stderr_path rc

  stdout_path="$RUN_QUALITY_TMPDIR/changed-path-${context//[^A-Za-z0-9_.-]/_}.stdout"
  stderr_path="$RUN_QUALITY_TMPDIR/changed-path-${context//[^A-Za-z0-9_.-]/_}.stderr"

  if "$@" >"$stdout_path" 2>"$stderr_path"; then
    cat "$stdout_path"
    return 0
  else
    rc=$?
  fi

  echo "run-quality: changed-path discovery command failed ($context)" >&2
  printf 'command:' >&2
  printf ' %q' "$@" >&2
  printf '\nexit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$stdout_path" >&2
  echo "STDERR:" >&2
  cat "$stderr_path" >&2
  return 1
}

collect_quality_changed_paths() {
  local upstream_ref merge_base

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 1
  fi

  if upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)"; then
    if ! merge_base="$(run_changed_path_git upstream-merge-base git merge-base HEAD "$upstream_ref")"; then
      return 1
    fi
    run_changed_path_git upstream-diff git diff --name-only "$merge_base"...HEAD || return 1
  fi

  run_changed_path_git unstaged-diff git diff --name-only || return 1
  run_changed_path_git staged-diff git diff --name-only --cached || return 1
  run_changed_path_git untracked-list git ls-files --others --exclude-standard || return 1
}

coverage_relevant_changes_present() {
  local path changed_paths_path

  if [[ -n "$RUN_QUALITY_LABELS" ]]; then
    return 0
  fi

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi

  changed_paths_path="$RUN_QUALITY_TMPDIR/quality-changed-paths.txt"
  if ! collect_quality_changed_paths >"$changed_paths_path"; then
    echo "run-quality: changed-path discovery failed; running check-coverage fail-closed." >&2
    return 0
  fi

  while IFS= read -r path; do
    case "$path" in
      scripts/control_plane_lib.py|scripts/control_plane_lifecycle_lib.py|scripts/doctor.py|scripts/install_provenance_lib.py|scripts/install_tools.py|scripts/support_sync_lib.py|scripts/sync_support.py|scripts/update_tools.py|scripts/upstream_release_lib.py|scripts/check_coverage.py|scripts/check_coverage_lib.py|scripts/check_coverage_extra_lib.py|tests/control_plane/*|tests/quality_gates/test_check_coverage_inventory.py)
        return 0
        ;;
    esac
  done <"$changed_paths_path"

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

label_is_explicitly_selected() {
  local label="$1"
  local raw selected_label

  if [[ -z "$RUN_QUALITY_LABELS" ]]; then
    return 1
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

agent_browser_runtime_gate_enabled() {
  local label="$1"

  if [[ "${CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE:-0}" == "1" ]]; then
    return 0
  fi

  label_is_explicitly_selected "$label"
}

queue_selected() {
  local label="$1"
  shift

  if ! label_is_selected "$label"; then
    return 0
  fi

  queue_timed "$label" "$@"
}

queue_agent_browser_runtime_gate() {
  local label="$1"
  shift

  if ! agent_browser_runtime_gate_enabled "$label"; then
    return 0
  fi

  queue_timed "$label" "$@"
}

print_phase_output() {
  local label="$1"
  local status="$2"
  local elapsed_ms="$3"
  local log_path="$4"
  local attention_output=0

  printf '%s %-24s %s\n' "$(uppercase_status "$status")" "$label" "$(format_elapsed "$elapsed_ms")"

  if [[ -s "$log_path" ]] && grep -Eq '^(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])' "$log_path"; then
    attention_output=1
  fi

  if [[ "$status" == "fail" || "$RUN_QUALITY_VERBOSE" == "1" || "$attention_output" == "1" ]]; then
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

if agent_browser_runtime_gate_enabled "agent-browser-runtime-baseline"; then
  queue_agent_browser_runtime_gate "agent-browser-runtime-baseline" env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --cleanup-orphans
  if flush_phase; then
    :
  else
    OVERALL_RC=$?
    echo "run-quality: agent-browser runtime baseline failed; stopping before other gates." >&2
    print_final_summary
    exit "$OVERALL_RC"
  fi
fi

queue_selected "validate-skills" python3 scripts/validate_skills.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-reference-catalog" python3 scripts/validate_quality_reference_catalog.py --repo-root "$REPO_ROOT"
queue_selected "validate-skill-ergonomics" python3 scripts/validate_skill_ergonomics.py --repo-root "$REPO_ROOT"
queue_selected "validate-usage-episodes" python3 scripts/validate_usage_episodes.py --repo-root "$REPO_ROOT"
queue_selected "report-usage-episodes" python3 scripts/report_usage_episodes.py --repo-root "$REPO_ROOT"
queue_selected "check-cli-skill-surface" python3 scripts/check_cli_skill_surface.py --repo-root "$REPO_ROOT" --run-probes
queue_selected "validate-surfaces" python3 scripts/validate_surfaces.py --repo-root "$REPO_ROOT"
queue_selected "validate-inference-interpretation" python3 scripts/validate_inference_interpretation.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-public-skill-validation" python3 scripts/validate_public_skill_validation.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-dogfood" python3 scripts/validate_public_skill_dogfood.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-scenarios" python3 scripts/validate_cautilus_scenarios.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-proof" python3 scripts/validate_cautilus_proof.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-diagnostics" python3 scripts/validate_cautilus_diagnostics.py --repo-root "$REPO_ROOT" --all
queue_selected "validate-cautilus-call-provenance" python3 scripts/validate_cautilus_call_provenance.py --repo-root "$REPO_ROOT"
queue_selected "validate-profiles" python3 scripts/validate_profiles.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-presets" python3 scripts/validate_presets.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-adapters" python3 scripts/validate_adapters.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-integrations" python3 scripts/validate_integrations.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging" python3 scripts/validate_packaging.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging-committed" python3 scripts/validate_packaging_committed.py --repo-root "$REPO_ROOT"
queue_selected "validate-handoff-artifact" python3 scripts/validate_handoff_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-artifact" python3 scripts/validate_debug_artifact.py --repo-root "$REPO_ROOT" --report-all
queue_selected "validate-debug-seam-index" python3 scripts/build_debug_seam_risk_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-retro-lesson-index" python3 scripts/build_retro_lesson_selection_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-quality-artifact" python3 scripts/validate_quality_artifact.py --repo-root "$REPO_ROOT" --report-all
queue_selected "validate-attention-state-visibility" python3 scripts/validate_attention_state_visibility.py --repo-root "$REPO_ROOT" --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support
queue_selected "validate-inventory-consumption" python3 scripts/validate_inventory_consumption.py --repo-root "$REPO_ROOT"
queue_selected "validate-inventory-consumption-declaration" python3 scripts/validate_inventory_consumption_declaration.py --repo-root "$REPO_ROOT"
queue_selected "check-inventory-declaration-coverage" python3 scripts/check_inventory_declaration_coverage.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-closeout-contract" python3 scripts/validate_quality_closeout_contract.py --repo-root "$REPO_ROOT"
queue_selected "validate-critique-artifacts" python3 scripts/validate_critique_artifacts.py --repo-root "$REPO_ROOT" --report-all
queue_selected "validate-ideation-artifact" python3 scripts/validate_ideation_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-retro-artifact" python3 scripts/validate_retro_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-current-pointer-freshness" python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"
queue_selected "inventory-quality-handoff" python3 scripts/inventory_quality_handoff.py --repo-root "$REPO_ROOT"
queue_selected "validate-maintainer-setup" python3 scripts/validate_maintainer_setup.py --repo-root "$REPO_ROOT"
queue_selected "check-python-lengths" python3 scripts/check_python_lengths.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-python-filenames" python3 scripts/check_python_filenames.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-python-runtime-inheritance" python3 scripts/check_python_runtime_inheritance.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-skill-contracts" python3 scripts/check_skill_contracts.py --repo-root "$REPO_ROOT"
queue_selected "check-skill-bootstrap-vars" python3 scripts/check_skill_bootstrap_vars.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-bootstrap-shim-consistency" python3 scripts/check_bootstrap_shim_consistency.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-public-doc-coupling" python3 scripts/check_public_doc_coupling.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-timing-layer-completeness" python3 scripts/check_timing_layer_completeness.py --repo-root "$REPO_ROOT"
queue_selected "check-export-safe-imports" python3 scripts/check_export_safe_imports.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-plugin-import-smoke" python3 scripts/check_plugin_import_smoke.py --repo-root "$REPO_ROOT"
queue_selected "check-command-docs" python3 scripts/check_command_docs.py --repo-root "$REPO_ROOT"
queue_selected "check-doc-links" python3 scripts/check_doc_links.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-spec-evidence-durability" python3 scripts/check_spec_evidence_durability.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-references-link-inventory" python3 scripts/check_references_link_inventory.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-seed-fixture-budget" python3 scripts/check_seed_fixture_budget.py --repo-root "$REPO_ROOT"
queue_selected "check-title-slug-drift" python3 scripts/check_title_slug_drift.py
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

PYTEST_FLAGS=(--repo-root "$REPO_ROOT" --mode "$RUN_QUALITY_MODE")
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]]; then
  PYTEST_FLAGS+=(--include-release-only)
fi
queue_selected "pytest" python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"
if [[ "$RUN_QUALITY_MODE" == "full" ]] || coverage_relevant_changes_present; then
  queue_selected "check-coverage" python3 scripts/check_coverage.py --repo-root "$REPO_ROOT"
fi
# Changed-line mutation-coverage pre-merge teeth (spec:
# charness-artifacts/spec/mutation-changed-line-premerge-gate.md). Blocks uncovered
# changed lines in eligible mutation-pool files over the unpushed range (merge-base
# with origin/main) — the recurring #219->#251->#260->#320->#321 class — before the
# scheduled cron re-derives it post-merge. Cheap and safe by construction: it NEVER
# runs the slow coverage probe here (--skip-if-no-coverage) and it only trusts a
# coverage source FRESH for the current changed-pool content (--require-fresh-coverage,
# a `.fingerprint` marker match), so a stale reports/mutation/test-coverage.json cannot
# raise false positives — it skips non-blocking instead. With no fresh coverage, or no
# origin/main base, it is non-blocking by construction. The producer that writes fresh
# coverage + the `.fingerprint` marker is the closeout step
# `run_slice_closeout.py --produce-mutation-coverage` (run with --verification-lock).
CHANGED_LINE_BASE_SHA="$(git -C "$REPO_ROOT" merge-base origin/main HEAD 2>/dev/null || true)"
queue_selected "check-changed-line-mutation-coverage" python3 scripts/check_changed_line_mutation_coverage.py --repo-root "$REPO_ROOT" --base-sha "$CHANGED_LINE_BASE_SHA" --head-sha HEAD --reuse-coverage --skip-if-no-coverage --require-fresh-coverage
queue_selected "check-test-completeness" python3 scripts/check_test_completeness.py --repo-root "$REPO_ROOT" -- "${STANDING_PYTEST_TARGETS[@]}"
queue_selected "check-test-production-ratio" python3 scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT" --require-git-file-listing --advisory
queue_selected "check-boundary-bypass-ratchet" python3 scripts/check_boundary_bypass_ratchet.py --repo-root "$REPO_ROOT"
queue_selected "specdown" bash -c 'command -v specdown >/dev/null || { echo "specdown is required for executable specs. Install from https://github.com/corca-ai/specdown or run charness tool doctor specdown --json for current readiness."; exit 1; }; specdown run -quiet -no-report -jobs 4'
queue_selected "run-evals" python3 scripts/run_evals.py --repo-root "$REPO_ROOT"
queue_selected "doc-duplicates" python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root "$REPO_ROOT" --require-nose --json-out "$RUN_QUALITY_TMPDIR/doc-duplicates.json"
flush_phase || OVERALL_RC=$?

# Boy-scout duplicate ratchet (item 5, slice 2). Runs in the broad path only (this
# phase is not in the pre-push DOCS_ONLY_LABELS subset; C5). Hard-blocks a new
# fixable-eligible clone family (code via the full nose family_id scan vs the gate
# baseline; doc via signature drift) and escalates the boy-scout nudge when the
# reviewed fixable ceiling stagnates above the healthy floor. Reuses the
# doc-duplicates drift JSON above (flushed) so it does not pay the ~18.5s doc scan
# twice; it runs its own ~0.6s code scan. Inert when dup_ratchet is disabled;
# advisory (never blocks) when the overlay/baseline/nose are missing. See
# skills/public/quality/references/dup-ratchet.md.
queue_selected "dup-ratchet" python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root "$REPO_ROOT" --doc-inventory "$RUN_QUALITY_TMPDIR/doc-duplicates.json"

queue_selected "inventory-ci-local-gate-parity" python3 skills/public/quality/scripts/inventory_ci_local_gate_parity.py --repo-root "$REPO_ROOT" --require-empty-parity-issues --require-git-file-listing
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py" ]]; then
  queue_selected "inventory-gitignore-scan-hygiene" python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root "$REPO_ROOT" --require-empty --require-git-file-listing
else
  queue_selected "inventory-gitignore-scan-hygiene" bash -c 'echo "inventory_gitignore_scan_hygiene.py unavailable; skipping optional advisory inventory."'
fi
queue_selected "check-current-pointer-writes" python3 scripts/check_current_pointer_writes.py --repo-root "$REPO_ROOT" --require-empty
queue_selected "measure-startup-probes" python3 skills/public/quality/scripts/measure_startup_probes.py --repo-root "$REPO_ROOT" --class standing --record-runtime-signals
# inventory-sloc writes a git-tracked artifact, which the adapter declares via
# quality_phases. Read-only mode (e.g. the pre-push hook) drops the --output
# redirect so the working tree stays clean; full mode refreshes the artifact.
if [[ "$RUN_QUALITY_MODE" == "read-only" ]]; then
  queue_selected "inventory-sloc" python3 skills/public/quality/scripts/inventory_sloc.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-sloc" python3 skills/public/quality/scripts/inventory_sloc.py --repo-root "$REPO_ROOT" --output "$REPO_ROOT/charness-artifacts/quality/sloc-inventory/latest.json"
fi
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_ubiquitous_language.py" ]]; then
  queue_selected "inventory-ubiquitous-language" python3 skills/public/quality/scripts/inventory_ubiquitous_language.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-ubiquitous-language" bash -c 'echo "inventory_ubiquitous_language.py unavailable; skipping optional advisory inventory."'
fi
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_cli_ergonomics.py" ]]; then
  queue_selected "inventory-cli-ergonomics" python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-cli-ergonomics" bash -c 'echo "inventory_cli_ergonomics.py unavailable; skipping optional advisory inventory."'
fi
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_nose_clones.py" ]]; then
  queue_selected "inventory-nose-clones" python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-nose-clones" bash -c 'echo "ADVISORY: inventory_nose_clones.py unavailable; skipping optional clone-family inventory."'
fi
flush_phase || OVERALL_RC=$?

if [[ -n "$RUN_QUALITY_RUNTIME_PROFILE" ]]; then
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT" --runtime-profile "$RUN_QUALITY_RUNTIME_PROFILE"
else
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT"
fi
flush_phase || OVERALL_RC=$?

if agent_browser_runtime_gate_enabled "agent-browser-runtime-hygiene"; then
  queue_agent_browser_runtime_gate "agent-browser-runtime-hygiene" env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --assert-no-orphans
  flush_phase || {
    OVERALL_RC=$?
    env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --cleanup-orphans --execute >/dev/null 2>&1 || true
  }
fi
print_final_summary
exit "$OVERALL_RC"
