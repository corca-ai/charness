#!/usr/bin/env bash
set -euo pipefail

# The consumer-facing entry point in `skills/public/quality/references/catalog.yaml` is
# `./scripts/run-quality.sh`, conditioned on "repo exposes this repo-native command" --
# i.e. the CONSUMER's own script, never this exported copy. Without a guard the exported
# copy self-locates to `plugins/charness/` and drives ~85 gates against the plugin tree,
# which is the widest-blast-radius instance of the class the other gates already refuse.
GATE_NAME="run-quality"
GATE_CONSEQUENCE="This runner drives every gate from its own root, so a package root that is not the git
root would run the whole standing lane against the exported plugin tree instead of the
repository under test."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "run-quality: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=0
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

RUN_QUALITY_REVIEW=0
RUN_QUALITY_RELEASE=0
RUN_QUALITY_MODE="${CHARNESS_QUALITY_MODE:-full}"
RUN_QUALITY_INCLUDE_RELEASE_ONLY="${CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY:-0}"
RUN_QUALITY_RECEIPT_JSON="${CHARNESS_QUALITY_RECEIPT_JSON:-}"
RUN_QUALITY_NON_CLAIM=""
# The default developer lane is deliberately small.  `--full` remains the
# explicit broad battery; an implementation should not
# pay every inventory, evaluator, and mutation-proof gate just because it ran the
# repo's quality command.
RUN_QUALITY_FULL_QUEUE="${CHARNESS_QUALITY_FULL_QUEUE:-0}"
for arg in "$@"; do
  case "$arg" in
    --review)
      RUN_QUALITY_REVIEW=1
      RUN_QUALITY_FULL_QUEUE=1
      ;;
    --read-only)
      RUN_QUALITY_MODE="read-only"
      ;;
    --full)
      RUN_QUALITY_MODE="full"
      RUN_QUALITY_FULL_QUEUE=1
      ;;
    --release)
      RUN_QUALITY_RELEASE=1
      RUN_QUALITY_INCLUDE_RELEASE_ONLY=1
      RUN_QUALITY_FULL_QUEUE=1
      ;;
    --receipt-json=*)
      RUN_QUALITY_RECEIPT_JSON="${arg#*=}"
      if [[ -z "$RUN_QUALITY_RECEIPT_JSON" ]]; then
        echo "run-quality: --receipt-json= requires a non-empty path" >&2
        exit 2
      fi
      ;;
    --non-claim=release-changed-line-coverage)
      RUN_QUALITY_NON_CLAIM="release-changed-line-coverage"
      ;;
    --non-claim=*)
      echo "run-quality: unsupported --non-claim label ${arg#*=}" >&2
      exit 2
      ;;
    --help|-h)
      echo "Usage: ./scripts/run-quality.sh [--review] [--read-only|--full] [--release] [--non-claim=release-changed-line-coverage] [--receipt-json=PATH]"
      echo "  --review     replay passing phase logs and validate external links online"
      echo "  --read-only  skip phases that would mutate git-tracked quality artifacts"
      echo "  --full       run the broad quality battery and refresh git-tracked artifacts"
      echo "  default      run only the core implementation lane"
      echo "  --release    include release-only tests"
      echo "  --non-claim=release-changed-line-coverage  explicitly omit only the release-final changed-line lane; requires --release"
      echo "  --receipt-json=PATH  write the per-run semantic receipt (also via CHARNESS_QUALITY_RECEIPT_JSON)"
      exit 0
      ;;
    *)
      echo "run-quality: unknown argument $arg" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$RUN_QUALITY_NON_CLAIM" && "$RUN_QUALITY_RELEASE" != "1" ]]; then
  echo "run-quality: --non-claim=release-changed-line-coverage requires --release" >&2
  exit 2
fi

if [[ "$RUN_QUALITY_RELEASE" == "1" && -n "${CHARNESS_QUALITY_LABELS:-}" ]]; then
  echo "run-quality: --release is one indivisible lane; CHARNESS_QUALITY_LABELS cannot narrow it" >&2
  exit 2
fi

case "$RUN_QUALITY_MODE" in
  full|read-only) ;;
  *)
    echo "run-quality: CHARNESS_QUALITY_MODE must be 'full' or 'read-only', got '$RUN_QUALITY_MODE'" >&2
    exit 2
    ;;
esac
export CHARNESS_QUALITY_MODE="$RUN_QUALITY_MODE"

# Refuse an interrupted mutation run before loading optional runtime helpers.  A
# minimal consumer copy may expose this runner without the Charness hook helper;
# recovery is still the first actionable verdict in that state.
RUN_QUALITY_GIT_DIR="$(git rev-parse --git-dir 2>/dev/null || true)"
if [[ ( -n "$RUN_QUALITY_GIT_DIR" && -e "$RUN_QUALITY_GIT_DIR/charness-mutation-recovery" ) \
   || -e "$REPO_ROOT/.charness/mutation-recovery" ]]; then
  echo "run-quality: FAIL interrupted mutation recovery is REQUIRED; run python3 scripts/mutate_and_restore.py --repo-root . --check-recovery, then --recover" >&2
  exit 2
fi

# The shell runtime primitive is shared with hooks and lint. Keeping this boundary
# in one file prevents a new cache/temp policy from being copied into each entrypoint.
# shellcheck source=.githooks/runtime-env.sh
source "$REPO_ROOT/.githooks/runtime-env.sh"
RUN_QUALITY_RUNTIME_ROOT="$CHARNESS_RUNTIME_ROOT"
RUN_QUALITY_RUNTIME_RECORD_ARGS=(--repo-root "$REPO_ROOT")
RUN_QUALITY_STATE_ROOT_ARGS=()
if [[ "${CHARNESS_RUNTIME_ROOT_AUTO:-}" != "1" ]]; then
  RUN_QUALITY_STATE_ROOT="$RUN_QUALITY_RUNTIME_ROOT/quality"
  RUN_QUALITY_STATE_ROOT_ARGS+=(--state-root "$RUN_QUALITY_STATE_ROOT")
  RUN_QUALITY_RUNTIME_RECORD_ARGS+=("${RUN_QUALITY_STATE_ROOT_ARGS[@]}")
fi

# Every gate command below writes to a per-phase file so concurrent checks cannot
# interleave their output. Before this line existed, that useful buffering made a
# healthy long run indistinguishable from a command that never started: a caller
# redirecting both streams observed a zero-byte transcript until the slowest check
# in the first batch (normally pytest) finished. Keep progress on stderr so stdout's
# verdict/reporting contract stays machine-consumable, and emit it before discovery
# or queue construction can introduce another silent interval.
if [[ -n "${CHARNESS_QUALITY_LABELS:-}" ]]; then
  RUN_QUALITY_PROGRESS_SCOPE="$CHARNESS_QUALITY_LABELS"
elif [[ "$RUN_QUALITY_FULL_QUEUE" == "1" ]]; then
  RUN_QUALITY_PROGRESS_SCOPE="full"
else
  RUN_QUALITY_PROGRESS_SCOPE="core"
fi
printf 'run-quality: START mode=%s release=%s requested_scope=%s outputs=isolated status=streamed\n' \
  "$RUN_QUALITY_MODE" "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" "$RUN_QUALITY_PROGRESS_SCOPE" >&2

STANDING_PYTEST_TARGETS_TEXT="$(python3 scripts/run_standing_pytest.py --repo-root "$REPO_ROOT" --print-expanded-targets)"
mapfile -t STANDING_PYTEST_TARGETS <<<"$STANDING_PYTEST_TARGETS_TEXT"

RUN_QUALITY_TMPDIR="$(mktemp -d)"
# The VERDICT is authoritative; cleanup is best-effort.
#
# Measured, because a first version of this comment stated the mechanism WRONG and a
# reviewer caught it. Bash does NOT hand the trap's status to the script:
# `bash -c 'trap "false" EXIT; exit 2'` exits 2. What rewrote the verdict is `set -e`,
# in force inside the EXIT trap on the ORDINARY exit path: the failing `rm` tripped
# errexit, the trap aborted, and the shell exited with the failing command's 1 instead
# of the pending 2. (Not unconditional -- errexit is suspended in a condition context,
# so a trap reached from inside `flush_phase || OVERALL_RC=$?` would not abort. The fix
# below does not depend on which path was taken.)
# The distinction is load-bearing for anyone repairing a sibling gate from this note:
# under the true mechanism `rm ... || true` is a complete fix, and under the false one
# it would have been actively harmful.
#
# What made the `rm` fail: a run that correctly refused with exit 2 ("a queued gate
# label the universe reader cannot see") does so from `assert_label_in_universe`, which
# fires AFTER `queue_selected "pytest"` has forked its background subshell. That child
# was still writing into the temp dir while the trap walked it, so `rm -rf` reported
# `Directory not empty`. A gate runner whose cleanup can restate its verdict is the
# class this runner exists to catch, one level up.
#
# `$?` is captured first, NOTHING in the body can abort the trap, and the captured
# status is what the shell exits with. Both the removal and the warning are guarded --
# a first repair guarded only the removal, and a reviewer pointed out the warning could
# then abort it in turn: `./scripts/run-quality.sh | head` closes stderr's pipe, `echo`
# dies on SIGPIPE, and errexit takes the trap out before `exit "$rc"`. The trailing
# `|| :` is what makes the sentence above true rather than aspirational.
#
# The removal error is WARNED rather than discarded: it is the only signal that a gate
# child outlived the runner, and silencing it would let undeletable `/tmp` dirs and
# detached gate processes accumulate invisibly. `rm`'s own message is left on stderr
# beneath the warning, because "Directory not empty", "Permission denied" and
# "Read-only file system" need different responses and the warning names only the first.
#
# Cleanup deliberately does NOT `wait` on outstanding phase children: a stuck gate would
# hang teardown forever. The cost is that the warning can fire while a child is still
# writing, which is exactly what it says.
#
# One consequence, stated rather than hidden: the explicit `exit` means a signal death
# leaves normally with 128+n instead of re-raising, so a wrapper sees the number but not
# `WIFSIGNALED`. The verdict is unchanged; only "interrupted" vs "failed" blurs.
# shellcheck disable=SC2317  # reached only through the EXIT trap below
run_quality_cleanup() {
  local rc=$?
  rm -rf "$RUN_QUALITY_TMPDIR" ||
    echo "run-quality: warning: could not remove $RUN_QUALITY_TMPDIR (a gate child may still be running)" >&2 || :
  exit "$rc"
}
trap run_quality_cleanup EXIT
RUN_QUALITY_RUNTIME_BATCH="$RUN_QUALITY_TMPDIR/runtime-batch.jsonl"
: >"$RUN_QUALITY_RUNTIME_BATCH"

# The label universe (#546). `check-runtime-budget-universe` reconciles the
# adapter's budget blocks against the labels a reader can find in THIS file, and a
# budget whose label the reader missed reads as orphaned -- a blocking red whose
# remedy tells the operator to delete a correct bar. So the reader is not trusted
# alone: `queue_timed` refuses any label the reader did not find, which turns an
# extraction miss into a loud failure naming the gate that caused it, at the moment
# it is queued, instead of a wrong verdict about a correct adapter later.
#
# An EMPTY set disables the assertion rather than refusing every gate. That is the
# consumer case (a runner this reader cannot see), where refusing would be the same
# false-red the reconciliation exists to avoid. The reader keeps stdout to labels or
# nothing and puts its prose on stderr precisely so this can be true: the first cut
# printed "not derivable ..." on stdout, that sentence became a one-element universe,
# the empty check below never fired, and the first gate was refused with a remedy
# about queue-line quoting. A reader that genuinely cannot resolve a call site exits
# nonzero instead of returning an empty set, and that is handled below.
declare -A RUN_QUALITY_LABEL_UNIVERSE=()
RUN_QUALITY_UNIVERSE_ERR="$RUN_QUALITY_TMPDIR/label-universe.err"
if RUN_QUALITY_UNIVERSE_YAML="$(python3 scripts/quality_label_universe.py --repo-root "$REPO_ROOT" 2>"$RUN_QUALITY_UNIVERSE_ERR")"; then
  # The reader emits one YAML document since the 2026-08-14 --json removal, not bare
  # label lines. Reading it as lines made EVERY line ("resolved: true", "- label") a
  # label, so the first queued gate failed the assertion and the runner exited 2.
  # `resolved: false` still degrades to the empty set the block above describes: an
  # unresolvable reader disables the assertion rather than refusing every gate.
  RUN_QUALITY_UNIVERSE_TEXT="$(
    # No backticks in the comments below: shellcheck reads this single-quoted Python as shell
    # and reports SC2016 for them. Plain names cost nothing and keep the gate green without a
    # suppression that would also hide a genuine unexpanded `$VAR` here.
    printf '%s' "$RUN_QUALITY_UNIVERSE_YAML" | python3 -c '
import json, sys
raw = sys.stdin.read()
try:
    # JSON first, exactly like the Python readers (charness.parse_repo_script_payload
    # and friends): yaml_output.render_yaml falls back to COMPACT JSON when PyYAML is
    # absent, so on such an interpreter the producer emits JSON -- and requiring yaml
    # here would refuse a payload the producer wrote perfectly well, while blaming YAML.
    payload = json.loads(raw)
except json.JSONDecodeError:
    import yaml
    payload = yaml.safe_load(raw)
payload = payload or {}
labels = payload.get("labels") or [] if payload.get("resolved") else []
print("\n".join(labels))
'
  )" || {
    echo "run-quality: FAIL could not parse the gate-label reader payload (tried JSON, then YAML)." >&2
    exit 2
  }
  while IFS= read -r universe_label; do
    if [[ -n "$universe_label" ]]; then
      RUN_QUALITY_LABEL_UNIVERSE["$universe_label"]=1
    fi
  done <<<"$RUN_QUALITY_UNIVERSE_TEXT"
else
  # The reader's own message, captured rather than re-derived: invoking it a second
  # time to print the reason risks reporting a different failure than the one that
  # actually stopped the run.
  echo "run-quality: FAIL the gate-label reader refused this runner, so no budget can be reconciled against it:" >&2
  cat "$RUN_QUALITY_UNIVERSE_ERR" >&2
  exit 2
fi

assert_label_in_universe() {
  local label="$1"
  if [[ ${#RUN_QUALITY_LABEL_UNIVERSE[@]} -eq 0 ]]; then
    return 0
  fi
  if [[ -z "${RUN_QUALITY_LABEL_UNIVERSE[$label]:-}" ]]; then
    echo "run-quality: FAIL gate label '${label}' is queued here but scripts/quality_label_universe.py did not find it in this file, so every budget naming it would read as orphaned. Spell the label as a plain double-quoted literal on the queue line, or add its wrapper to QUEUE_FUNCTIONS in that reader." >&2
    exit 2
  fi
}

RUN_QUALITY_VERBOSE="${CHARNESS_QUALITY_VERBOSE:-0}"
RUN_QUALITY_LABELS="${CHARNESS_QUALITY_LABELS:-}"
RUN_QUALITY_HEARTBEAT_SECONDS="${CHARNESS_QUALITY_HEARTBEAT_SECONDS:-15}"
if [[ ! "$RUN_QUALITY_HEARTBEAT_SECONDS" =~ ^[0-9]+$ ]]; then
  echo "run-quality: CHARNESS_QUALITY_HEARTBEAT_SECONDS must be a non-negative integer" >&2
  exit 2
fi
RUN_QUALITY_RUNTIME_PROFILE="${CHARNESS_RUNTIME_PROFILE:-}"
# A label-filtered run measures the SAME gate against a different amount of
# competition, and the sample records only elapsed time. Pooled with full-queue
# samples, the enforcement median becomes a function of how the operator happened
# to invoke the gate rather than of the code (#544). The aggregate label already
# refuses to record under a filter for exactly this reason; the per-gate samples
# are re-keyed instead of dropped, so the subset regime stays measurable.
# A caller that runs a RECURRING subset names it; an ad hoc filter falls back to
# one shared `filtered` bucket, which is
# honest about being a mixture rather than pretending to be a regime.
# A gate set can differ from the standard battery in two directions, and both
# change what every sibling is competing with: a label filter NARROWS it, and an
# opt-in gate WIDENS it. Every env-gated gate that queues into the MAIN concurrent
# phase is a widening case, so they are enumerated rather than special-cased one at
# a time — naming only the first one found is how the second keeps contaminating
# the enforced window. Gates that occupy their own phase (the agent-browser pair,
# each queued and flushed alone) are deliberately absent: they compete with
# nothing, so they change no sibling's sample.
RUN_QUALITY_EXTRA_GATE_TOKENS=""
if [[ "${CHARNESS_QUALITY_DEAD_CODE:-0}" == "1" ]]; then
  RUN_QUALITY_EXTRA_GATE_TOKENS="${RUN_QUALITY_EXTRA_GATE_TOKENS}-dead-code"
fi
if [[ "${CHARNESS_SUPPLY_CHAIN_ONLINE:-0}" == "1" ]]; then
  RUN_QUALITY_EXTRA_GATE_TOKENS="${RUN_QUALITY_EXTRA_GATE_TOKENS}-supply-chain"
fi
if [[ -n "$RUN_QUALITY_LABELS" ]]; then
  RUN_QUALITY_RUNTIME_REGIME="${CHARNESS_RUNTIME_REGIME:-filtered}"
elif [[ -n "$RUN_QUALITY_EXTRA_GATE_TOKENS" ]]; then
  RUN_QUALITY_RUNTIME_REGIME="${CHARNESS_RUNTIME_REGIME:-plus${RUN_QUALITY_EXTRA_GATE_TOKENS}}"
else
  RUN_QUALITY_RUNTIME_REGIME=""
fi
# Exported as well as passed explicitly: gates that record their OWN samples
# through the recorder (`measure_startup_probes.py --record-runtime-signals`)
# never see this script's locals, and an unregimed sample from inside a filtered
# run is the same contamination one call site over. Same variable both ways, so
# the ambient and explicit values cannot disagree.
export CHARNESS_RUNTIME_REGIME="$RUN_QUALITY_RUNTIME_REGIME"
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
declare -a PHASE_STARTED_NS=()
declare -a COMPLETED_LABELS=()
declare -a COMPLETED_ELAPSED_MS=()
declare -a COMPLETED_STATUSES=()
declare -a MEASURED_LABELS=()

TOTAL_PASSES=0
TOTAL_FAILURES=0
TOTAL_UNESTABLISHED=0
RUN_QUALITY_SELECTED_LABEL_MATCHES=0
# The NAMES behind the counts. The summary used to report "1 failed" without saying
# which, and the summary is the LAST line -- the one line every `tail` preserves. So a
# reader who truncated the output (a human scrolling, a CI log tail, an agent piping
# through `tail` to save context) kept the count and lost the only fact they could act
# on, and had to re-run a ~95s gate to recover it. Naming them here makes the common
# truncation harmless instead of forbidding the truncation.
UNESTABLISHED_LABELS=""
# The final line is the per-run operator receipt. Each failed label travels with either
# the verified durable log path or an explicit unavailable marker; a preceding path
# line is not enough because a truncating reader may preserve only the final line.
declare -a FAILED_RECEIPT_SUBJECTS=()
declare -a FAILED_RECEIPT_RECOVERY_SPECS=()
# Per-phase logs live in a mktemp dir this script `rm -rf`s on EXIT, so after a run
# there was nothing left to re-read: a truncated view of a failure could only be
# recovered by running the whole gate again. Failing phases' logs are copied here
# instead, and the path is named in the summary -- the durable half of the same fix.
RUN_QUALITY_FAILURE_LOG_DIR="$RUN_QUALITY_RUNTIME_ROOT/quality-failure-logs"

append_label() {
  # $1 = current list, $2 = label. Space-separated, no leading space.
  if [[ -z "$1" ]]; then printf '%s' "$2"; else printf '%s %s' "$1" "$2"; fi
}
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
# A lane that judged what it analyzed CLEAN but could not analyze part of its
# changed set. Renders UNPROVEN, exactly like 3, and for the same reason: it is
# not a pass. Kept a DISTINCT byte from 3 upstream because only 3 is refusable at
# push time; here the two collapse, because the runner's job is the verdict LINE,
# not the push decision. Same opt-in discipline as 3 -- a label joins this list
# after its own exit-code contract has been read, never by global reinterpretation.
PARTIAL_EXIT=4
# `docs-graph` joins after its exit contract was read, per the rule above: it
# exits 3 only when it could not OBSERVE the graph -- awiki absent, an unreadable
# summary line, a scan that read zero documents, or an awiki exit code outside
# its clean/findings pair -- and never when it observed a bad graph. An
# unobserved orphan count is not zero, and this is the byte that says so.
UNESTABLISHED_CAPABLE_LABELS="inventory-nose-clones docs-graph check-docs check-closeout-classification-parity check-export-self-sufficiency check-artifact-referents"
NATIVE_GATE_LABELS="check-export-safe-imports check-plugin-dir-references"

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
  # Only the batch path passes the regime on ARGV. `record_runtime` serves the
  # aggregate label, which is unreachable under a label filter (its
  # `-z "$RUN_QUALITY_LABELS"` guard) but IS reachable under a widening opt-in —
  # so the aggregate does get regimed, via the exported variable rather than a
  # flag. That is a real dependency on the `export` above, not an accident: an
  # unregimed `run-quality-full` sample from a dead-code run would land against
  # the real bar while all its per-gate siblings went to the regime bucket.
  if ! python3 scripts/record_quality_runtime.py \
    "${RUN_QUALITY_RUNTIME_RECORD_ARGS[@]}" \
    --runtime-regime "$RUN_QUALITY_RUNTIME_REGIME" \
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
    "${RUN_QUALITY_RUNTIME_RECORD_ARGS[@]}" \
    --label "$label" \
    --elapsed-ms "$elapsed_ms" \
    --status "$status" \
    --timestamp "$timestamp" >/dev/null
}

queue_timed() {
  local label="$1"
  shift
  # Every wrapper funnels here, so this is the one place that sees every label the
  # run will actually queue -- including the two dispatchers' forwarded "$label".
  assert_label_in_universe "$label"
  local slug="${label//[^A-Za-z0-9_.-]/_}"
  local log_path="$RUN_QUALITY_TMPDIR/${slug}.log"
  local meta_path="$RUN_QUALITY_TMPDIR/${slug}.meta"
  local started_ns
  started_ns="$(date +%s%N)"

  (
    local start_ns end_ns elapsed_ms rc status timestamp
    start_ns="$started_ns"
    if "$@" >"$log_path" 2>&1; then
      rc=0
      status="pass"
    else
      rc=$?
      if [[ "$rc" == "$UNESTABLISHED_EXIT" || "$rc" == "$PARTIAL_EXIT" ]] && label_may_report_unestablished "$label"; then
        status="unestablished"
      else
        status="fail"
      fi
    fi
    end_ns="$(date +%s%N)"
    elapsed_ms="$(((end_ns - start_ns) / 1000000))"
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf '%s\n%s\n%s\n%s\n' "$elapsed_ms" "$status" "$timestamp" "$rc" >"${meta_path}.tmp"
    mv "${meta_path}.tmp" "$meta_path"
    exit 0
  ) &

  PHASE_LABELS+=("$label")
  PHASE_PIDS+=("$!")
  PHASE_LOGS+=("$log_path")
  PHASE_METAS+=("$meta_path")
  PHASE_STARTED_NS+=("$started_ns")
  printf 'run-quality: CHECK_START label=%s\n' "$label" >&2
}

RUN_QUALITY_CORE_LABELS="validate-skills validate-packaging check-shell py-compile ruff"

label_is_core() {
  case " $RUN_QUALITY_CORE_LABELS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

label_is_selected() {
  local label="$1"
  local raw selected_label

  if [[ -z "$RUN_QUALITY_LABELS" ]]; then
    [[ "$RUN_QUALITY_FULL_QUEUE" == "1" ]] && return 0
    label_is_core "$label"
    return $?
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

  if [[ -n "$RUN_QUALITY_LABELS" ]]; then
    RUN_QUALITY_SELECTED_LABEL_MATCHES=$((RUN_QUALITY_SELECTED_LABEL_MATCHES + 1))
  fi
  queue_timed "$label" "$@"
}

queue_agent_browser_runtime_gate() {
  local label="$1"
  shift

  if ! agent_browser_runtime_gate_enabled "$label"; then
    return 0
  fi

  if [[ -n "$RUN_QUALITY_LABELS" ]] && label_is_explicitly_selected "$label"; then
    RUN_QUALITY_SELECTED_LABEL_MATCHES=$((RUN_QUALITY_SELECTED_LABEL_MATCHES + 1))
  fi
  queue_timed "$label" "$@"
}

native_gate_preflight() {
  local label
  for label in $NATIVE_GATE_LABELS; do
    if label_is_selected "$label"; then
      if ! python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT" --probe export-safe; then
        echo "run-quality: native gate preflight failed for $label" >&2
        exit 1
      fi
      return 0
    fi
  done
}

native_gate_preflight

print_phase_output() {
  local label="$1"
  local status="$2"
  local elapsed_ms="$3"
  local log_path="$4"
  local attention_output=0

  printf '%s %-24s %s\n' "$(uppercase_status "$status")" "$label" "$(format_elapsed "$elapsed_ms")"

  # The marker no longer has to start a physical line. Gate output is unconditionally
  # YAML since the 2026-08-14 --json removal, so an advisory that used to be printed as
  # `WARN: ...` now rides inside a payload as `advisory: 'WARN: ...'` or a `- WARN: ...`
  # list item. Anchoring on `^` alone silently retired the whole attention tier on
  # PASSING runs -- a green gate that stops speaking is exactly the fail-quiet shape
  # this block exists to prevent. So the marker is also accepted at the start of a YAML
  # scalar (after `: `, `- `, or an opening quote). Matching a little too eagerly costs
  # an extra printed log; matching too narrowly costs the advisory itself.
  if [[ -s "$log_path" ]] && grep -Eq '(^|: |- |["'"'"'])(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])' "$log_path"; then
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

PHASE_RC=0

consume_phase_result() {
  local i="$1"
  local pid label log_path meta_path elapsed_ms status timestamp cmd_rc
  local failure_slug failure_log recovery_spec meta_line
  local -a meta_lines=()

  pid="${PHASE_PIDS[$i]}"
  label="${PHASE_LABELS[$i]}"
  log_path="${PHASE_LOGS[$i]}"
  meta_path="${PHASE_METAS[$i]}"
  wait "$pid" || true
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
    MEASURED_LABELS+=("$label")
    TOTAL_PASSES=$((TOTAL_PASSES + 1))
  elif [[ "$status" == "unestablished" ]]; then
    TOTAL_UNESTABLISHED=$((TOTAL_UNESTABLISHED + 1))
    UNESTABLISHED_LABELS="$(append_label "$UNESTABLISHED_LABELS" "$label")"
  else
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
    failure_slug="${label//[^A-Za-z0-9_.-]/_}"
    failure_log="$RUN_QUALITY_FAILURE_LOG_DIR/${failure_slug}.log"
    if mkdir -p "$RUN_QUALITY_FAILURE_LOG_DIR" 2>/dev/null && cp "$log_path" "$failure_log" 2>/dev/null; then
      recovery_spec="available:$failure_log"
    else
      printf 'WARN: could not save full output for %s to %s; its log is NOT available.\n' \
        "$label" "$failure_log" >&2
      recovery_spec="unavailable:full output could not be copied"
    fi
    FAILED_RECEIPT_SUBJECTS+=("$label")
    FAILED_RECEIPT_RECOVERY_SPECS+=("$recovery_spec")
  fi

  if [[ "$cmd_rc" != "0" && "$status" != "unestablished" ]]; then
    PHASE_RC="$cmd_rc"
  fi
}

print_phase_heartbeat() {
  local now_ns="$1"
  local remaining="$2"
  local i elapsed_ms item running_sample="" shown=0
  local -n done_ref="$3"

  for i in "${!PHASE_LABELS[@]}"; do
    if [[ "${done_ref[$i]:-0}" == "1" ]]; then
      continue
    fi
    elapsed_ms="$(((now_ns - PHASE_STARTED_NS[i]) / 1000000))"
    item="${PHASE_LABELS[$i]}:$(format_elapsed "$elapsed_ms")"
    if [[ -z "$running_sample" ]]; then
      running_sample="$item"
    else
      running_sample="${running_sample},${item}"
    fi
    shown=$((shown + 1))
    if (( shown == 5 )); then
      break
    fi
  done
  if (( remaining > shown )); then
    running_sample="${running_sample},+$((remaining - shown))-more"
  fi
  printf 'run-quality: HEARTBEAT remaining=%s running=%s\n' \
    "$remaining" "${running_sample:-none}" >&2
}

synthesize_missing_phase_meta() {
  local i="$1"
  local pid="${PHASE_PIDS[$i]}"
  local meta_path="${PHASE_METAS[$i]}"
  local log_path="${PHASE_LOGS[$i]}"
  local now_ns elapsed_ms timestamp

  if [[ -f "$meta_path" ]] || kill -0 "$pid" 2>/dev/null; then
    return 1
  fi
  wait "$pid" || true
  now_ns="$(date +%s%N)"
  elapsed_ms="$(((now_ns - PHASE_STARTED_NS[i]) / 1000000))"
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf 'run-quality: child exited without writing its completion metadata\n' >>"$log_path"
  printf '%s\nfail\n%s\n2\n' "$elapsed_ms" "$timestamp" >"${meta_path}.tmp"
  mv "${meta_path}.tmp" "$meta_path"
  return 0
}

flush_phase() {
  local phase_count first_label last_label remaining made_progress i now_ns next_heartbeat_ns
  local heartbeat_interval_ns
  local -a phase_done=()

  if ((${#PHASE_LABELS[@]} == 0)); then
    return 0
  fi

  phase_count="${#PHASE_LABELS[@]}"
  first_label="${PHASE_LABELS[0]}"
  last_label="${PHASE_LABELS[$((phase_count - 1))]}"
  remaining="$phase_count"
  heartbeat_interval_ns="$((RUN_QUALITY_HEARTBEAT_SECONDS * 1000000000))"
  now_ns="$(date +%s%N)"
  next_heartbeat_ns="$((now_ns + heartbeat_interval_ns))"
  PHASE_RC=0
  printf 'run-quality: BATCH_START checks=%s first=%s last=%s\n' \
    "$phase_count" "$first_label" "$last_label" >&2

  while (( remaining > 0 )); do
    made_progress=0
    for i in "${!PHASE_LABELS[@]}"; do
      if [[ "${phase_done[$i]:-0}" == "1" ]]; then
        continue
      fi
      if [[ ! -f "${PHASE_METAS[$i]}" ]]; then
        synthesize_missing_phase_meta "$i" || continue
      fi
      consume_phase_result "$i"
      phase_done[i]=1
      remaining=$((remaining - 1))
      made_progress=1
    done

    if (( remaining > 0 && heartbeat_interval_ns > 0 )); then
      now_ns="$(date +%s%N)"
      if (( now_ns >= next_heartbeat_ns )); then
        print_phase_heartbeat "$now_ns" "$remaining" phase_done
        next_heartbeat_ns="$((now_ns + heartbeat_interval_ns))"
      fi
    fi
    if (( remaining > 0 && made_progress == 0 )); then
      sleep 0.1
    fi
  done

  flush_runtime_batch

  PHASE_LABELS=()
  PHASE_PIDS=()
  PHASE_LOGS=()
  PHASE_METAS=()
  PHASE_STARTED_NS=()
  return "$PHASE_RC"
}

print_final_summary() {
  local end_ns elapsed_ms status timestamp aggregate_label

  end_ns="$(date +%s%N)"
  elapsed_ms="$(((end_ns - RUN_QUALITY_START_NS) / 1000000))"
  status="pass"
  if [[ "$OVERALL_RC" != "0" ]]; then
    status="fail"
  elif [[ "$TOTAL_UNESTABLISHED" -gt 0 ]]; then
    status="unestablished"
  fi

  # Record the aggregate before printing the receipt. A warning from this best-effort
  # telemetry write must not become the last combined-output line and displace the
  # actionable verdict from a context-truncated reader.
  if [[ -z "$RUN_QUALITY_LABELS" ]]; then
    aggregate_label="run-quality-${RUN_QUALITY_MODE}"
    if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]]; then
      aggregate_label="${aggregate_label}-release"
    fi
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    if ! record_runtime "$aggregate_label" "$elapsed_ms" "$status" "$timestamp"; then
      echo "run-quality: warning: failed to record aggregate runtime for ${aggregate_label}." >&2
    fi
  fi

  local -a receipt_args=(--status "$status" --effective-exit-code "$OVERALL_RC" \
    --passed "$TOTAL_PASSES" --failed "$TOTAL_FAILURES" --elapsed "$(format_elapsed "$elapsed_ms")")
  local scope_label unproven_label i
  for scope_label in "${MEASURED_LABELS[@]}"; do
    receipt_args+=(--measured-scope "$scope_label")
  done
  for i in "${!FAILED_RECEIPT_SUBJECTS[@]}"; do
    receipt_args+=(--adverse-subject "${FAILED_RECEIPT_SUBJECTS[$i]}" \
      --recovery "${FAILED_RECEIPT_RECOVERY_SPECS[$i]}")
  done
  if [[ -n "$UNESTABLISHED_LABELS" ]]; then
    local -a unproven_labels=()
    read -r -a unproven_labels <<< "$UNESTABLISHED_LABELS"
    for unproven_label in "${unproven_labels[@]}"; do
      receipt_args+=(--unproven-subject "$unproven_label")
    done
  fi
  if [[ -n "$RUN_QUALITY_RECEIPT_JSON" ]]; then
    receipt_args+=(--json-path "$RUN_QUALITY_RECEIPT_JSON")
  fi
  # The helper owns the terminal line and its semantic fields. Its diagnostic is
  # emitted before that line; keep a failed optional write from changing the
  # already-computed gate result or displacing the final human receipt.
  if ! python3 scripts/proof_receipt.py quality "${receipt_args[@]}"; then
    :
  fi
}

# `pytest` is the first release decision. Release pytest is deliberately isolated
# from every other gate: it is the cheapest broad prerequisite and a failure must
# not spend time starting inventories or mutation. Ordinary development still
# queues its small/core lane as before.
PYTEST_FLAGS=(--repo-root "$REPO_ROOT" --mode "$RUN_QUALITY_MODE")
# Standing and release-only pytest are different workloads (the release set adds
# minutes of subprocess-heavy tests). Recording both under one label made the
# budget unable to catch a standing regression: it was sized from the release
# mode's max, so a 2x standing slowdown still landed under the bar. Same
# `-release` suffix convention as the aggregate label below.
# Both arms spell the label literally on purpose: the timing-completeness and
# gate-verbosity inventories parse this file for queued gate labels and cannot
# resolve a shell variable, so a computed label reads as an untimed gate.
RUN_QUALITY_PYTEST_RELEASE=0
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]] || label_is_explicitly_selected "pytest-release"; then
  RUN_QUALITY_PYTEST_RELEASE=1
  PYTEST_FLAGS+=(--include-release-only)
  queue_selected "pytest-release" env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"
else
  queue_selected "pytest" env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"
fi

# A selected standing/release pytest is always its own first batch. This keeps
# full standing runs fail-fast too, while an explicit label filter may still
# request a different narrow diagnostic without implicitly adding pytest.
if ((${#PHASE_LABELS[@]} > 0)); then
  if flush_phase; then
    :
  else
    pytest_rc=$?
    OVERALL_RC="$pytest_rc"
    if [[ "$RUN_QUALITY_PYTEST_RELEASE" == "1" ]]; then
      echo "run-quality: release pytest failed; stopping before later release checks." >&2
    else
      echo "run-quality: standing pytest failed; stopping before later quality checks." >&2
    fi
    print_final_summary
    exit "$pytest_rc"
  fi
fi

# Browser startup is another optional runtime diagnostic, but it must not delay
# the cheap broad pytest prerequisite in a normal release run. Explicit
# agent-browser-only labels still retain their narrow diagnostic behavior.
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
queue_selected "quality-tool-fixtures" python3 scripts/check_quality_tool_fixtures.py --repo-root "$REPO_ROOT"
# Dead-code advisory (vulture-backed): DEFAULT-OFF opt-in. Two full vulture passes
# are slow and the findings need per-item triage, so it never runs in the default
# battery and never blocks (advisory only — the script always exits 0 and surfaces an
# ADVISORY line for review_candidates). Opt in with CHARNESS_QUALITY_DEAD_CODE=1 (runs
# regardless of label scoping, mirroring the agent-browser-runtime gate) or
# CHARNESS_QUALITY_LABELS=dead-code-advisory to run just this gate.
if [[ "${CHARNESS_QUALITY_DEAD_CODE:-0}" == "1" ]] || label_is_explicitly_selected "dead-code-advisory"; then
  if [[ -n "$RUN_QUALITY_LABELS" ]] && label_is_explicitly_selected "dead-code-advisory"; then
    RUN_QUALITY_SELECTED_LABEL_MATCHES=$((RUN_QUALITY_SELECTED_LABEL_MATCHES + 1))
  fi
  queue_timed "dead-code-advisory" python3 skills/public/quality/scripts/run_dead_code_advisory.py --repo-root "$REPO_ROOT"
fi
queue_selected "check-cli-skill-surface" python3 scripts/check_cli_skill_surface.py --repo-root "$REPO_ROOT" --run-probes
queue_selected "validate-surfaces" python3 scripts/validate_surfaces.py --repo-root "$REPO_ROOT"
queue_selected "validate-inference-interpretation" python3 scripts/validate_inference_interpretation.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-public-skill-validation" python3 scripts/validate_public_skill_validation.py --repo-root "$REPO_ROOT"
queue_selected "validate-public-skill-dogfood" python3 scripts/validate_public_skill_dogfood.py --repo-root "$REPO_ROOT"
queue_selected "validate-profiles" python3 scripts/validate_profiles.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-presets" python3 scripts/validate_presets.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-adapters" python3 scripts/validate_adapters.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "validate-integrations" python3 scripts/validate_integrations.py --repo-root "$REPO_ROOT"
queue_selected "validate-packaging" python3 scripts/validate_packaging.py --repo-root "$REPO_ROOT"
# Checked-in export drift is a release-boundary concern, but remains available for
# a focused diagnostic without widening ordinary full runs.
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]] || label_is_explicitly_selected "validate-packaging-committed"; then
  queue_selected "validate-packaging-committed" python3 scripts/validate_packaging_committed.py --repo-root "$REPO_ROOT"
fi
queue_selected "validate-debug-artifact" python3 scripts/validate_debug_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-debug-seam-index" python3 scripts/build_debug_seam_risk_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-retro-lesson-index" python3 scripts/build_retro_lesson_selection_index.py --repo-root "$REPO_ROOT" --check
queue_selected "validate-lesson-ledger" python3 scripts/check_lesson_ledger.py --repo-root "$REPO_ROOT"
queue_selected "validate-quality-artifact" python3 scripts/validate_quality_artifact.py --repo-root "$REPO_ROOT"
queue_selected "validate-attention-state-visibility" python3 scripts/validate_attention_state_visibility.py --repo-root "$REPO_ROOT" --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support
queue_selected "validate-inventory-consumption" python3 scripts/validate_inventory_consumption.py --repo-root "$REPO_ROOT"
queue_selected "check-inventory-declaration-coverage" python3 scripts/check_inventory_declaration_coverage.py --repo-root "$REPO_ROOT"
# BLOCKING by operator decision (2026-08-02), promoted after one advisory run:
# a documented command that cannot run is a wrong answer that escapes silently.
# NOT because false positives are impossible -- the promoting slice shipped two,
# caught by its own bounded review (wrong resolution root; treating absence as a
# defect for `<repo-root>/`, which names the reader's tree). Both are repaired
# and pinned. `--strict` refuses on findings and on unreadable docs; without it
# the same command stays a read-only inventory.
queue_selected "inventory-skill-script-references" python3 scripts/inventory_skill_script_references.py --repo-root "$REPO_ROOT" --strict
queue_selected "validate-quality-closeout-contract" python3 scripts/validate_quality_closeout_contract.py --repo-root "$REPO_ROOT"
# Resolve the release/change range once. The release-final changed-line producer
# receives this explicit SHA, and the critique probe shares the same range. The
# empty value remains an honest no-verdict input for a checkout without origin/main.
# #408 5b tooth: a bare `single-surface` verdict is rejected when the release/change
# range touches a boundary_cross_surface_globs path).
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
queue_selected "validate-maintainer-setup" python3 scripts/validate_maintainer_setup.py --repo-root "$REPO_ROOT"
queue_selected "check-python-lengths" python3 scripts/check_code_lengths.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-python-filenames" python3 scripts/check_python_filenames.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-python-runtime-inheritance" python3 scripts/check_python_runtime_inheritance.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-skill-contracts" python3 scripts/check_skill_contracts.py --repo-root "$REPO_ROOT"
queue_selected "check-skill-bootstrap-vars" python3 scripts/check_skill_bootstrap_vars.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-bootstrap-shim-consistency" python3 scripts/check_bootstrap_shim_consistency.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-public-doc-coupling" python3 scripts/check_public_doc_coupling.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-regenerable-facts" python3 skills/public/quality/scripts/check_regenerable_facts.py --repo-root "$REPO_ROOT"
queue_selected "check-timing-layer-completeness" python3 scripts/check_timing_layer_completeness.py --repo-root "$REPO_ROOT"
# Sibling of the line above: both reconcile a declaration against the label set
# THIS file can queue. Queued here rather than beside `check-runtime-budget`
# because it reads no samples -- it asks whether the runner still knows a budgeted
# label's name, which is answerable before any gate has run.
queue_selected "check-runtime-budget-universe" python3 scripts/check_runtime_budget_universe.py --repo-root "$REPO_ROOT"
# Third in that family, and the one that reads COMMANDS rather than labels. The
# two gates above ask whether a declared bar still names something real; this asks
# whether a command a gate SPAWNS is dominated by a cheaper one this repo already
# has. Queued rather than left as an on-demand script deliberately: the recorded
# waste class here is a correct rule with no carrier, and the instance that
# produced this gate cost 25 minutes inside the session that wrote the retro
# about it.
queue_selected "check-command-dominance" python3 scripts/check_command_dominance.py --repo-root "$REPO_ROOT"
queue_selected "check-export-safe-imports" python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT" export-safe --repo-root "$REPO_ROOT"
# Adjacent to the line above and NOT the same question. That gate asks whether a
# path literal survives the `skills/public/` collapse, reading the SOURCE tree.
# This one reads the CHECKED-IN EXPORT and asks whether it can run on a machine
# that has only the export -- the question the packaging validator structurally
# cannot answer, because its oracle is the exporter.
queue_selected "check-export-self-sufficiency" python3 scripts/check_export_self_sufficiency.py --repo-root "$REPO_ROOT"
queue_selected "check-plugin-import-smoke" python3 scripts/check_plugin_import_smoke.py --repo-root "$REPO_ROOT"
# Command-doc drift remains available at the release boundary and for focused
# diagnostics, but it is not part of the ordinary broad/default battery.
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]] || label_is_explicitly_selected "check-command-docs"; then
  queue_selected "check-command-docs" python3 scripts/check_command_docs.py --repo-root "$REPO_ROOT"
fi
queue_selected "check-docs" ./scripts/check-docs.sh
# Compatibility entry points remain available for focused diagnostics and older
# automation. They are never part of the default battery, so the composite does
# not run the same document population twice.
if [[ -n "$RUN_QUALITY_LABELS" ]]; then
  queue_selected "check-doc-links" python3 scripts/check_doc_links.py --repo-root "$REPO_ROOT" --require-git-file-listing
  queue_selected "docs-graph" python3 scripts/check_docs_graph.py --repo-root "$REPO_ROOT"
  # No --require-git-file-listing: this gate's subject is the GENERATED mirror,
  # which is gitignored, so the git listing is the wrong ruler and the flag named
  # a strictness it could not deliver.
  queue_selected "check-plugin-doc-links" python3 scripts/check_plugin_doc_links.py --repo-root "$REPO_ROOT"
  queue_selected "check-markdown" ./scripts/check-markdown.sh
  queue_selected "check-links-internal" ./scripts/check-links-internal.sh
  queue_selected "check-links-external" ./scripts/check-links-external.sh
fi
# Resolves `<plugin-dir>/` against the generated package. Unlike `<repo-root>/`,
# which means the reader's tree and is unverifiable from here, this placeholder
# names a tree this repo builds -- so it can be checked, which is the whole
# reason it was worth adopting (D50).
queue_selected "check-plugin-dir-references" python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT" plugin-refs --repo-root "$REPO_ROOT"
queue_selected "check-plugin-asset-command-carriers" python3 scripts/check_plugin_asset_command_carriers.py --repo-root "$REPO_ROOT"
queue_selected "check-documented-command-flags" python3 scripts/check_documented_command_flags.py --repo-root "$REPO_ROOT" --require-git-file-listing
# position: the rung above the flags gate. That one proves a documented flag against
# the named script's argparse; this one proves a documented `charness <subcommand>`
# against the CLI's. It replaces `domain-language-contract`'s hand-declared alias
# list, which could only catch a rename someone remembered to declare.
queue_selected "check-documented-subcommands" python3 scripts/check_documented_subcommands.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-spec-evidence-durability" python3 scripts/check_spec_evidence_durability.py --repo-root "$REPO_ROOT" --require-git-file-listing
queue_selected "check-artifact-referents" python3 scripts/check_artifact_referents.py --repo-root "$REPO_ROOT"
queue_selected "check-references-link-inventory" python3 scripts/check_references_link_inventory.py --repo-root "$REPO_ROOT" --require-git-file-listing

# No barrier here: `flush_phase` is not fail-fast (every phase runs regardless of
# an earlier failure), so a barrier between independent gates buys output grouping
# and nothing else — while the gates below wait on the slowest gate above. The
# barriers that stay carry a real dependency: `doc-duplicates` hands its drift
# JSON to `dup-ratchet`, `check-seed-fixture-budget` needs pytest's temp tree to be
# settled (see its comment below), and `check-runtime-budget` reads the samples
# every earlier phase recorded. The inventory declaration drift check is the one
# measured scheduling exception: its own subprocess fan-out makes its runtime
# sample sensitive to the first phase's CPU load, so it runs alone after this
# phase drains and is flushed before unrelated gates resume.
queue_selected "check-secrets" ./scripts/check-secrets.sh
queue_selected "check-supply-chain" python3 scripts/check_supply_chain.py --repo-root "$REPO_ROOT"
queue_selected "check-github-actions" python3 scripts/check_github_actions.py --repo-root "$REPO_ROOT"
if [[ "${CHARNESS_SUPPLY_CHAIN_ONLINE:-0}" == "1" ]]; then
  queue_selected "check-supply-chain-online" python3 scripts/check_supply_chain_online.py --repo-root "$REPO_ROOT" --triage-owner "repo-maintainers"
fi
queue_selected "check-shell" ./scripts/check-shell.sh
# Rust is counted as PRODUCTION by check_test_production_ratio (native/*/src/**.rs is in
# its source denominator) and was read by no gate at all: 11,891 lines, files up to 1,399
# against a 480-line Python cap. This closes the lint half. The length half is still open
# and check-rust.sh names that blind class in its own header.
queue_selected "check-rust" ./scripts/check-rust.sh
shopt -s nullglob
python_files=(
  scripts/*.py
  skills/public/*/scripts/*.py
  skills/support/*/scripts/*.py
  skills/shared/scripts/*.py
  skills/support/*/vendor/*.py
)
queue_selected "py-compile" python3 -m py_compile "${python_files[@]}"
queue_selected "ruff" ./scripts/check-python-lint.sh

if [[ "$RUN_QUALITY_MODE" == "full" ]] || coverage_relevant_changes_present; then
  queue_selected "check-coverage" python3 scripts/check_coverage.py --repo-root "$REPO_ROOT"
fi
# Changed-line coverage is release-final only. It is deliberately absent from the
# ordinary implementation and explicit full queues; the release phase below owns
# the one producer/consumer proof after every other release check has flushed.
queue_selected "check-test-completeness" python3 scripts/check_test_completeness.py --repo-root "$REPO_ROOT" -- "${STANDING_PYTEST_TARGETS[@]}"
# The advisory ratio is likewise retained for release and focused diagnostics,
# while ordinary broad/default runs pay only for the core test contract.
# ADVISORY, and the posture is pinned by test_ratio_gate_stays_advisory_in_the_runner.
# `4122f6cd0` promoted this to blocking on 2026-08-29 at ratio 0.993, one day after
# `issue-753/lane-A-ratio-surface-brief.md:37` said the posture was a LATER #753
# decision. At 144800/144799 the cap then had only 4-decimal rounding left, and it
# pulled directly against `release-changed-line-coverage`: covering a changed line
# tripped the cap, and the cheapest relief was deleting release safety machinery.
# A JTBD audit of all ten release subsystems found no defensible cut. The gate's own
# `--advisory` docstring names this hazard, `2026-06-19-gate-buy-vs-build-triage.md:36-38`
# ranked the hard cap the repo's strongest DROP candidate, and the #420 critique
# predicted exactly this recurrence. The measurement stays; the hard block does not.
if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]] || label_is_explicitly_selected "check-test-production-ratio"; then
  queue_selected "check-test-production-ratio" python3 scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT" --require-git-file-listing --advisory
fi
queue_selected "check-boundary-bypass-ratchet" python3 scripts/check_boundary_bypass_ratchet.py --repo-root "$REPO_ROOT"
# Every packaged check_/validate_ script needs a consumer-facing decision, public
# contract metadata, and an explicit consumer adoption decision. This is the
# catalog's self-check; a new validator cannot become silent by omission.
queue_selected "check-consumer-validator-catalog" python3 scripts/check_consumer_validator_catalog.py --repo-root "$REPO_ROOT" --adoption-path .agents/consumer-validator-adoption.yaml --require-adoption
PROVENANCE_CONTRACT_CHECKER=""
for candidate in \
  "$REPO_ROOT/skills/public/quality/scripts/check_provenance_contract.py" \
  "$REPO_ROOT/skills/quality/scripts/check_provenance_contract.py"; do
  if [[ -f "$candidate" ]]; then
    PROVENANCE_CONTRACT_CHECKER="$candidate"
    break
  fi
done
if [[ -n "$PROVENANCE_CONTRACT_CHECKER" ]]; then
  queue_selected "check-provenance-contract" python3 "$PROVENANCE_CONTRACT_CHECKER" --repo-root "$REPO_ROOT"
else
  # A missing checker is not a clean proof.  Keep ordinary consumer runs
  # diagnosable, but refuse the irreversible release boundary unless the adapter
  # explicitly ships the contract checker (or the operator has a separate proof
  # packet). This prevents not-packaged -> exit 0 from being read as executable
  # provenance approval.
  # The single-quoted payload is intentionally evaluated by the inner bash.
  # shellcheck disable=SC2016
  queue_selected "check-provenance-contract" bash -c '
    echo "status: unestablished"
    echo "proof_level: unavailable"
    echo "non_claims: [provenance contract checker is not packaged in this consumer tree]"
    if [[ "$RUN_QUALITY_INCLUDE_RELEASE_ONLY" == "1" ]]; then
      echo "REFUSAL: release provenance proof is unavailable"
      exit 2
    fi
  '
fi
# Keep the remaining closeout classification consumers on one vocabulary. This
# is a direct parity check, not a second matrix of every floor and carrier.
queue_selected "check-closeout-classification-parity" python3 scripts/check_closeout_classification_parity.py --repo-root "$REPO_ROOT"
# The JSON reporter's destination lives in specdown.json, not behind -out, so an
# unredirected run rewrites the tracked report on every gate with nothing changed
# but its generatedAt timestamp. Run against an ephemeral config instead.
queue_selected "specdown" bash -c "command -v specdown >/dev/null || { echo \"specdown is required for executable specs. Install from https://github.com/corca-ai/specdown or run charness tool doctor specdown for current readiness.\"; exit 1; }; specdown_config=\$(python3 \"$REPO_ROOT/scripts/specdown_ephemeral_config.py\" --repo-root \"$REPO_ROOT\" --out-dir \"$RUN_QUALITY_TMPDIR/specdown-report\") || exit 1; trap 'rm -f \"\$specdown_config\" || true' EXIT; specdown run -config \"\$specdown_config\" -jobs 4 -out \"$RUN_QUALITY_TMPDIR/specdown-report\""
queue_selected "run-evals" python3 scripts/run_evals.py --repo-root "$REPO_ROOT"
queue_selected "doc-duplicates" python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root "$REPO_ROOT" --require-nose --json-out "$RUN_QUALITY_TMPDIR/doc-duplicates.json"

flush_phase || OVERALL_RC=$?

queue_selected "validate-inventory-consumption-declaration" python3 scripts/validate_inventory_consumption_declaration.py --repo-root "$REPO_ROOT"
flush_phase || OVERALL_RC=$?

# Boy-scout duplicate ratchet (item 5, slice 2). Runs in the broad path only (this
# phase is not in any narrow documentation-only subset; C5). Hard-blocks a new
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
queue_selected "check-current-pointer-writes" python3 scripts/check_current_pointer_writes.py --repo-root "$REPO_ROOT" --require-empty --require-git-file-listing
queue_selected "measure-startup-probes" python3 skills/public/quality/scripts/measure_startup_probes.py --repo-root "$REPO_ROOT" --class standing --record-runtime-signals "${RUN_QUALITY_STATE_ROOT_ARGS[@]}"
# SLOC is advisory measurement, not a quality-run write obligation. Keep its
# detailed report in the already-isolated run directory in every mode; the
# checked-in snapshot is refreshed explicitly through the quality-inventory
# surface command when a maintainer chooses to update it.
queue_selected "inventory-sloc" python3 skills/public/quality/scripts/inventory_sloc.py --repo-root "$REPO_ROOT" --output "$RUN_QUALITY_TMPDIR/sloc-inventory.json"
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_cli_ergonomics.py" ]]; then
  queue_selected "inventory-cli-ergonomics" python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-cli-ergonomics" bash -c 'echo "inventory_cli_ergonomics.py unavailable; skipping optional advisory inventory."'
fi
if [[ -f "$REPO_ROOT/skills/public/quality/scripts/inventory_nose_clones.py" ]]; then
  queue_selected "inventory-nose-clones" python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root "$REPO_ROOT"
else
  queue_selected "inventory-nose-clones" bash -c 'echo "ADVISORY: inventory_nose_clones.py unavailable; clone-family inventory is unproven."; exit 3'
fi
flush_phase || OVERALL_RC=$?

if [[ -n "$RUN_QUALITY_RUNTIME_PROFILE" ]]; then
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT" --runtime-profile "$RUN_QUALITY_RUNTIME_PROFILE" "${RUN_QUALITY_STATE_ROOT_ARGS[@]}" --advisory
else
  queue_selected "check-runtime-budget" python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT" "${RUN_QUALITY_STATE_ROOT_ARGS[@]}" --advisory
fi
flush_phase || OVERALL_RC=$?

if agent_browser_runtime_gate_enabled "agent-browser-runtime-hygiene"; then
  queue_agent_browser_runtime_gate "agent-browser-runtime-hygiene" env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --assert-no-orphans
  flush_phase || {
    OVERALL_RC=$?
    env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --cleanup-orphans --execute >/dev/null 2>&1 || true
  }
fi

# The release-final proof is the last release decision and has exactly one owner.
# Every earlier release phase has flushed by this point; a blocking predecessor
# leaves OVERALL_RC nonzero, so no changed-line work starts after a failed check.
if [[ "$RUN_QUALITY_RELEASE" == "1" && "$OVERALL_RC" == "0" && -n "$RUN_QUALITY_NON_CLAIM" ]]; then
  echo "NON-CLAIM: release-changed-line-coverage was not run by explicit release policy; no changed-line verdict exists" >&2
elif [[ "$RUN_QUALITY_RELEASE" == "1" && "$OVERALL_RC" == "0" ]]; then
  release_changed_line_coverage_json="$RUN_QUALITY_RUNTIME_ROOT/release-changed-line-coverage/coverage.json"
  if [[ -n "$CHANGED_LINE_BASE_SHA" ]]; then
    queue_selected "release-changed-line-coverage" python3 scripts/release_changed_line_coverage.py \
      --repo-root "$REPO_ROOT" \
      --base-sha "$CHANGED_LINE_BASE_SHA" \
      --coverage-json "$release_changed_line_coverage_json" \
      --refuse-unestablished
  else
    queue_selected "release-changed-line-coverage" bash -c \
      'echo "release changed-line coverage: no resolved origin/main base SHA; proof is unestablished" >&2; exit 2'
  fi
  flush_phase || OVERALL_RC=$?
fi

if [[ -n "$RUN_QUALITY_LABELS" && "$RUN_QUALITY_SELECTED_LABEL_MATCHES" -eq 0 ]]; then
  echo "run-quality: explicit CHARNESS_QUALITY_LABELS matched no queued checks." >&2
  OVERALL_RC=2
  TOTAL_FAILURES=1
  FAILED_RECEIPT_SUBJECTS+=("explicit label filter")
  FAILED_RECEIPT_RECOVERY_SPECS+=("unavailable:no phase matched the explicit filter")
fi

print_final_summary
exit "$OVERALL_RC"
