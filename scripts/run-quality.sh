#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

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

STANDING_PYTEST_TARGETS_TEXT="$(python3 scripts/run_standing_pytest.py --repo-root "$REPO_ROOT" --print-expanded-targets)"
mapfile -t STANDING_PYTEST_TARGETS <<<"$STANDING_PYTEST_TARGETS_TEXT"

RUN_QUALITY_TMPDIR="$(mktemp -d)"
trap 'rm -rf "$RUN_QUALITY_TMPDIR"' EXIT
RUN_QUALITY_RUNTIME_BATCH="$RUN_QUALITY_TMPDIR/runtime-batch.jsonl"
: >"$RUN_QUALITY_RUNTIME_BATCH"

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
TOTAL_UNESTABLISHED=0
OVERALL_RC=0

format_elapsed() {
  local elapsed_ms="$1"

  if (( elapsed_ms >= 1000 )); then
    printf '%s.%ss' "$((elapsed_ms / 1000))" "$(((elapsed_ms % 1000) / 100))"
    return
  fi

  printf '%sms' "$elapsed_ms"
}

# Exit 3 means "ran, established nothing" -- not a pass and not a failure. A gate
# that judged no scope must not print PASS: that is a terminal green over an
# unestablished scope appearing in the runner's own summary line. It cost this
# repo a cycle and two dead guards on 2026-07-29, where a changed-line run whose
# payload said it proved nothing was rendered `PASS` beside its own warning.
#
# OPT-IN PER LABEL, never a global reinterpretation of the byte. 3 is not ours to
# redefine: measured on this machine, `pytest` exits 3 on INTERNAL_ERROR (a crashed
# plugin or conftest) and `shellcheck` exits 3 on a bad invocation. Reading those as
# "unestablished, non-blocking" would silently stop gating on a test suite that
# never ran and on shell linting that never linted -- laundering a real failure,
# which is a worse escape than the green this exists to remove. A gate joins by
# being named here, after its own exit-code contract has been read.
UNESTABLISHED_EXIT=3
UNESTABLISHED_CAPABLE_LABELS="check-changed-line-mutation-coverage"

label_may_report_unestablished() {
  case " $UNESTABLISHED_CAPABLE_LABELS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

uppercase_status() {
  case "$1" in
    pass) printf 'PASS' ;;
    fail) printf 'FAIL' ;;
    unestablished) printf 'UNPROVEN' ;;
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

# One interpreter start plus a full rewrite of runtime-signals.json per gate cost
# ~70ms x ~80 gates (~5.5s, ~9% of wall) of strictly serial time inside flush_phase.
# The per-gate samples are queued into this batch file instead and handed to the
# recorder once per phase; the aggregate label below still records on its own
# because it is a single sample with its own failure handling.
queue_runtime_record() {
  # Gate labels are double-quoted literals in this file (the timing/verbosity
  # inventories parse the queue lines for them, so a quote-bearing label is not
  # expressible), statuses are pass/fail, timestamps come from `date` — none need JSON
  # string escaping. `elapsed_ms` is the one field that can arrive empty: a gate
  # subshell killed (OOM, SIGKILL) after its meta path exists but before it is
  # written yields "", which would emit `"elapsed_ms":` and make the line invalid.
  # Refuse to write that line rather than hand the recorder a broken batch.
  local label="$1"
  local elapsed_ms="$2"
  local status="$3"
  local timestamp="$4"
  if [[ ! "$elapsed_ms" =~ ^-?[0-9]+$ ]]; then
    echo "run-quality: warning: no usable elapsed time for ${label}; runtime sample skipped." >&2
    return 0
  fi
  printf '{"label":"%s","elapsed_ms":%s,"status":"%s","timestamp":"%s"}\n' \
    "$label" "$elapsed_ms" "$status" "$timestamp" >>"$RUN_QUALITY_RUNTIME_BATCH"
}

flush_runtime_batch() {
  if [[ ! -s "$RUN_QUALITY_RUNTIME_BATCH" ]]; then
    return 0
  fi
  if ! python3 scripts/record_quality_runtime.py \
    --repo-root "$REPO_ROOT" \
    --batch "$RUN_QUALITY_RUNTIME_BATCH" >/dev/null; then
    echo "run-quality: warning: failed to record phase runtimes." >&2
  fi
  : >"$RUN_QUALITY_RUNTIME_BATCH"
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
      if [[ "$rc" == "$UNESTABLISHED_EXIT" ]] && label_may_report_unestablished "$label"; then
        status="unestablished"
      else
        status="fail"
      fi
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

  # `unestablished` always prints its log: the entire point of the status is that
  # the reader learns WHAT was not established, and a bare `UNPROVEN <label>` line
  # is the same unexplained verdict in a new word.
  if [[ "$status" == "fail" || "$status" == "unestablished" || "$RUN_QUALITY_VERBOSE" == "1" || "$attention_output" == "1" ]]; then
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
    queue_runtime_record "$label" "$elapsed_ms" "$status" "$timestamp"

    print_phase_output "$label" "$status" "$elapsed_ms" "$log_path"
    COMPLETED_LABELS+=("$label")
    COMPLETED_ELAPSED_MS+=("$elapsed_ms")
    COMPLETED_STATUSES+=("$status")
    if [[ "$status" == "pass" ]]; then
      TOTAL_PASSES=$((TOTAL_PASSES + 1))
    elif [[ "$status" == "unestablished" ]]; then
      TOTAL_UNESTABLISHED=$((TOTAL_UNESTABLISHED + 1))
    else
      TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
    fi

    # An unestablished gate does not fail the run. It must not be counted as
    # passing either, and the summary says so -- the point is to remove the
    # green, not to add a blocker where the lane deliberately has none.
    # Keyed on the resolved STATUS, not on the raw code: a label that is not
    # unestablished-capable exiting 3 must still fail the run.
    if [[ "$cmd_rc" != "0" && "$status" != "unestablished" ]]; then
      rc="$cmd_rc"
    fi
  done

  flush_runtime_batch

  PHASE_LABELS=()
  PHASE_PIDS=()
  PHASE_LOGS=()
  PHASE_METAS=()
  return "$rc"
}

print_final_summary() {
  local end_ns elapsed_ms status timestamp aggregate_label

  end_ns="$(date +%s%N)"
  elapsed_ms="$(((end_ns - RUN_QUALITY_START_NS) / 1000000))"
  if [[ "$TOTAL_UNESTABLISHED" -gt 0 ]]; then
    printf 'Quality summary: %s passed, %s failed, %s UNPROVEN (ran, established nothing), total %s\n' \
      "$TOTAL_PASSES" \
      "$TOTAL_FAILURES" \
      "$TOTAL_UNESTABLISHED" \
      "$(format_elapsed "$elapsed_ms")"
  else
    printf 'Quality summary: %s passed, %s failed, total %s\n' \
      "$TOTAL_PASSES" \
      "$TOTAL_FAILURES" \
      "$(format_elapsed "$elapsed_ms")"
  fi

  if [[ -z "$RUN_QUALITY_LABELS" ]]; then
    status="pass"
    if [[ "$OVERALL_RC" != "0" ]]; then
      status="fail"
    elif [[ "$TOTAL_UNESTABLISHED" -gt 0 ]]; then
      # Otherwise the green survives one layer up: the console line said UNPROVEN
      # and the durable artifact -- the one later readers and closeout narratives
      # quote -- said `pass`. Same class, one surface over.
      status="unestablished"
    fi
    aggregate_label="run-quality-${RUN_QUALITY_MODE}"
    if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]]; then
      aggregate_label="${aggregate_label}-release"
    fi
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    if ! record_runtime "$aggregate_label" "$elapsed_ms" "$status" "$timestamp"; then
      echo "run-quality: warning: failed to record aggregate runtime for ${aggregate_label}." >&2
    fi
  fi
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

# `pytest` is the critical path (~44s against ~9s for every other gate combined),
# so it is queued FIRST and the cheap gates below overlap it instead of the other
# way round. It has no data dependency on any of them; the only real ordering in
# this script is `doc-duplicates` -> `dup-ratchet` (a later phase) and the
# agent-browser baseline above.
PYTEST_FLAGS=(--repo-root "$REPO_ROOT" --mode "$RUN_QUALITY_MODE")
# Standing and release-only pytest are different workloads (the release set adds
# minutes of subprocess-heavy tests). Recording both under one label made the
# budget unable to catch a standing regression: it was sized from the release
# mode's max, so a 2x standing slowdown still landed under the bar. Same
# `-release` suffix convention as the aggregate label below.
# Both arms spell the label literally on purpose: the timing-completeness and
# gate-verbosity inventories parse this file for queued gate labels and cannot
# resolve a shell variable, so a computed label reads as an untimed gate.
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]]; then
  PYTEST_FLAGS+=(--include-release-only)
  queue_selected "pytest-release" env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"
else
  queue_selected "pytest" env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"
fi

queue_selected "validate-skills" python3 scripts/validate_skills.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-reference-catalog" python3 scripts/validate_quality_reference_catalog.py --repo-root "$REPO_ROOT"
queue_selected "validate-skill-ergonomics" python3 scripts/validate_skill_ergonomics.py --repo-root "$REPO_ROOT"
queue_selected "validate-usage-episodes" python3 scripts/validate_usage_episodes.py --repo-root "$REPO_ROOT"
queue_selected "report-usage-episodes" python3 scripts/report_usage_episodes.py --repo-root "$REPO_ROOT"
# Dead-code advisory (vulture-backed): DEFAULT-OFF opt-in. Two full vulture passes
# are slow and the findings need per-item triage, so it never runs in the default
# battery and never blocks (advisory only — the script always exits 0 and surfaces an
# ADVISORY line for review_candidates). Opt in with CHARNESS_QUALITY_DEAD_CODE=1 (runs
# regardless of label scoping, mirroring the agent-browser-runtime gate) or
# CHARNESS_QUALITY_LABELS=dead-code-advisory to run just this gate.
if [[ "${CHARNESS_QUALITY_DEAD_CODE:-0}" == "1" ]] || label_is_explicitly_selected "dead-code-advisory"; then
  queue_timed "dead-code-advisory" python3 skills/public/quality/scripts/run_dead_code_advisory.py --repo-root "$REPO_ROOT"
fi
queue_selected "check-cli-skill-surface" python3 scripts/check_cli_skill_surface.py --repo-root "$REPO_ROOT" --run-probes
queue_selected "validate-surfaces" python3 scripts/validate_surfaces.py --repo-root "$REPO_ROOT"
queue_selected "validate-inference-interpretation" python3 scripts/validate_inference_interpretation.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-public-skill-validation" python3 scripts/validate_public_skill_validation.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-dogfood" python3 scripts/validate_public_skill_dogfood.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-scenarios" python3 scripts/validate_cautilus_scenarios.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-proof" python3 scripts/validate_cautilus_proof.py --repo-root "$REPO_ROOT"
queue_selected "validate-cautilus-diagnostics" python3 scripts/validate_cautilus_diagnostics.py --repo-root "$REPO_ROOT" --all
queue_selected "validate-cautilus-call-provenance" python3 scripts/validate_cautilus_call_provenance.py --repo-root "$REPO_ROOT"
queue_selected "validate-claim-fidelity-specs" python3 scripts/validate_claim_fidelity_specs.py --repo-root "$REPO_ROOT"
queue_selected "validate-scenario-conditional-reads" python3 scripts/validate_scenario_conditional_reads.py --repo-root "$REPO_ROOT"
queue_selected "validate-profiles" python3 scripts/validate_profiles.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-presets" python3 scripts/validate_presets.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-adapters" python3 scripts/validate_adapters.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-integrations" python3 scripts/validate_integrations.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging" python3 scripts/validate_packaging.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging-committed" python3 scripts/validate_packaging_committed.py --repo-root "$REPO_ROOT"
queue_selected "validate-handoff-artifact" python3 scripts/validate_handoff_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-artifact" python3 scripts/validate_debug_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-seam-index" python3 scripts/build_debug_seam_risk_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-retro-lesson-index" python3 scripts/build_retro_lesson_selection_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-quality-artifact" python3 scripts/validate_quality_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-attention-state-visibility" python3 scripts/validate_attention_state_visibility.py --repo-root "$REPO_ROOT" --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support
queue_selected "validate-inventory-consumption" python3 scripts/validate_inventory_consumption.py --repo-root "$REPO_ROOT"
queue_selected "validate-inventory-consumption-declaration" python3 scripts/validate_inventory_consumption_declaration.py --repo-root "$REPO_ROOT"
queue_selected "check-inventory-declaration-coverage" python3 scripts/check_inventory_declaration_coverage.py --repo-root "$REPO_ROOT"
# Non-blocking by operator decision (2026-08-02): the script has no non-zero exit
# path, so this surfaces WARN: only. The blocking half is the regression test in
# tests/test_skill_script_references.py.
queue_selected "inventory-skill-script-references" python3 scripts/inventory_skill_script_references.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-closeout-contract" python3 scripts/validate_quality_closeout_contract.py --repo-root "$REPO_ROOT"
# Base for the changed-path probes below — the merge-base with origin/main (the
# unpushed range). An empty base leaves the changed-line mutation gate below
# non-blocking; it no longer does so for the critique cross-surface probe, which
# passes --include-worktree (see that line). Shared by the critique probe
# (--changed-ref, the
# #408 5b tooth: a bare `single-surface` verdict is rejected when the unpushed
# range touches a boundary_cross_surface_globs path) and the changed-line
# mutation-coverage gate below.
CHANGED_LINE_BASE_SHA="$(git -C "$REPO_ROOT" merge-base origin/main HEAD 2>/dev/null || true)"
# Pass a RANGE (base..HEAD) so surfaces_lib routes it through `git diff <range>`
# (the changed set of the unpushed range). A BARE sha would instead resolve to
# that single commit's OWN diff-tree — the fork-point's history, not the change
# under review — silently mis-targeting the 5b tooth. A scope that resolves to NO
# paths reports `not-established` rather than `evaluated (no match)`, so the tooth
# is off without claiming it looked.
CRITIQUE_CHANGED_REF=""
[ -n "$CHANGED_LINE_BASE_SHA" ] && CRITIQUE_CHANGED_REF="${CHANGED_LINE_BASE_SHA}..HEAD"
# `--include-worktree` unions the working tree into the probe's scope. Verify
# precedes commit, so the slice under critique is on disk and a committed range
# alone cannot see it: measured, the same tree gave hit=false from the range and
# hit=true from its own worktree paths, which armed or disarmed the #408 5b tooth
# by which question was asked rather than by the code. Widening can only make the
# gate stricter -- `overrides` fires solely on an EVALUATED probe that matched --
# so the whole cost is false refusals, and the checked-in corpus carries 11 bare
# `single-surface` verdicts out of 965 artifacts to bound that.
queue_selected "validate-critique-artifacts" python3 scripts/validate_critique_artifacts.py --repo-root "$REPO_ROOT" --changed-ref "$CRITIQUE_CHANGED_REF" --include-worktree
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
queue_selected "check-documented-command-flags" python3 scripts/check_documented_command_flags.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-spec-evidence-durability" python3 scripts/check_spec_evidence_durability.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-references-link-inventory" python3 scripts/check_references_link_inventory.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-title-slug-drift" python3 scripts/check_title_slug_drift.py
queue_selected "check-markdown" ./scripts/check-markdown.sh

# No barrier here: `flush_phase` is not fail-fast (every phase runs regardless of
# an earlier failure), so a barrier between independent gates buys output grouping
# and nothing else — while the gates below wait on the slowest gate above. The
# barriers that stay are the ones that carry a real dependency: `doc-duplicates`
# hands its drift JSON to `dup-ratchet`, `check-seed-fixture-budget` needs pytest's
# temp tree to be settled (see its comment below), and `check-runtime-budget` reads
# the samples every earlier phase recorded.
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
  skills/shared/scripts/*.py
  skills/support/*/vendor/*.py
)
queue_selected "py-compile" python3 -m py_compile "${python_files[@]}"
queue_selected "ruff" ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts skills/shared/scripts

if [[ "$RUN_QUALITY_MODE" == "full" ]] || coverage_relevant_changes_present; then
  queue_selected "check-coverage" python3 scripts/check_coverage.py --repo-root "$REPO_ROOT"
fi
# Changed-line mutation-coverage PRE-MERGE TEETH (spec:
# charness-artifacts/spec/mutation-changed-line-premerge-gate.md; armed by D40 in
# docs/deferred-decisions.md, owner decision 2026-07-29).
#
# This lane BLOCKS on uncovered changed lines in eligible mutation-pool files over the
# unpushed range. It used to skip non-blocking whenever the author had not first paid
# the ~10-minute broad coverage producer, and that skip is why the recurring class
# (#219 -> #251 -> #260 -> #320 -> #321 -> #335 -> #453 -> #464) landed eight times: the
# lane that could stop a push exited 0 by construction, while the lane with teeth ran
# after the push where it cannot unland. The warning was already loud and was read and
# walked past, so a ninth warning was not the fix.
#
# Cost is scoped to the change rather than the repo: the producer asks
# suggest_mutation_coverage_command which standing tests reach the CHANGED pool files
# and instruments only those. Measured with the gate's own coverage mechanism: ~24s for
# a realistic single-commit slice, ~5min for a whole nine-commit session, against
# 11-15min broad. It writes reports/mutation/prepush-focused-coverage.json, NOT the
# canonical test-coverage.json, so subset coverage never sits at the broad producer's
# path carrying a valid freshness marker.
#
# Two deliberate non-blocking holes, both named loudly rather than silent:
#   - policy (a): a changed pool file the mapper resolves to NO standing test is not
#     blocked on, because that is a mapper gap and blocking there stops a push over the
#     tool's blind spot.
#   - a dirty mutation pool is `unestablished`, not clean -- the focused coverage is
#     collected from the live worktree while the mapping is computed against HEAD.
# --refuse-unestablished turns the second one into a failure in read-only mode, which is
# the pre-push hook's mode: mid-work a dirty worktree is normal, at push time it means
# the code about to land was never proven.
# CHANGED_LINE_BASE_SHA is defined above (hoisted so the critique cross-surface probe
# shares the same merge-base anchor).
# Keyed on the HOOK, not on `--read-only`. `--read-only` means "skip phases that
# mutate git-tracked artifacts" and is the published portable command operators run
# mid-work; overloading it as "a push is imminent" made an ordinary mid-work run over
# one uncommitted pool file fail the whole battery with "refusing at push time", with
# no push in flight. That false stop is how a lane gets disabled.
CHANGED_LINE_REFUSE_ARGS=()
if [[ "${CHARNESS_PRE_PUSH:-0}" == "1" ]]; then
  CHANGED_LINE_REFUSE_ARGS+=(--refuse-unestablished)
fi
queue_selected "check-changed-line-mutation-coverage" python3 scripts/prepush_focused_changed_line_coverage.py --repo-root "$REPO_ROOT" --base-sha "$CHANGED_LINE_BASE_SHA" "${CHANGED_LINE_REFUSE_ARGS[@]}"
queue_selected "check-test-completeness" python3 scripts/check_test_completeness.py --repo-root "$REPO_ROOT" -- "${STANDING_PYTEST_TARGETS[@]}"
queue_selected "check-test-production-ratio" python3 scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT" --require-git-file-listing --advisory
queue_selected "check-boundary-bypass-ratchet" python3 scripts/check_boundary_bypass_ratchet.py --repo-root "$REPO_ROOT"
# The JSON reporter's destination lives in specdown.json, not behind -out, so an
# unredirected run rewrites the tracked report on every gate with nothing changed
# but its generatedAt timestamp. Run against an ephemeral config instead.
queue_selected "specdown" bash -c "command -v specdown >/dev/null || { echo \"specdown is required for executable specs. Install from https://github.com/corca-ai/specdown or run charness tool doctor specdown for current readiness.\"; exit 1; }; specdown_config=\$(python3 \"$REPO_ROOT/scripts/specdown_ephemeral_config.py\" --repo-root \"$REPO_ROOT\" --out-dir \"$RUN_QUALITY_TMPDIR/specdown-report\") || exit 1; trap 'rm -f \"\$specdown_config\"' EXIT; specdown run -config \"\$specdown_config\" -jobs 4 -out \"$RUN_QUALITY_TMPDIR/specdown-report\""
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

# A THIRD real ordering dependency, found by review after the barrier removal:
# this gate scans `$PYTEST_DEBUG_TEMPROOT/pytest-of-<user>`, the same tree the
# `pytest` gate fills and then rmtree's. Run concurrently it measures a half-built
# tree. Reproduced directly: polling it during a standing pytest run returned
# `unavailable` the moment pytest tore its basetemp down. It belongs after the
# pytest barrier, where the tree is settled.
#
# The gate no longer fails OPEN on a scan error, so moving it back here would now
# fail the RUN rather than silently stop gating — do not move it on the strength
# of the older "it just goes advisory" reasoning, which is no longer true.
# The gate's escape hatch has to be reachable from HERE, because here is where it
# fires. `CHARNESS_QUALITY_LABELS` is an allowlist, so an operator cannot subtract
# one gate without enumerating the other ~80, which leaves `--no-verify` -- turning
# off all 82 gates to get past one. A gate whose remediation names a flag the
# operator cannot pass is a gate that lies at the moment it blocks.
seed_budget_args=(--repo-root "$REPO_ROOT")
if [[ -n "${CHARNESS_SEED_FIXTURE_ADVISORY:-}" ]]; then
  seed_budget_args+=(--advisory-on-scan-failure)
fi
queue_selected "check-seed-fixture-budget" python3 scripts/check_seed_fixture_budget.py "${seed_budget_args[@]}"

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
