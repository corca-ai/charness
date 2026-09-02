#!/usr/bin/env bash
set -euo pipefail

# Stable adapter-facing command: the Python engine owns the declarative list,
# selection, preamble, runtime state, receipts, and execution.
GATE_NAME="run-quality"
GATE_CONSEQUENCE="This runner executes the declared quality gate list from its package root."
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "run-quality: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=0
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

engine_args=()
release=0
non_claim=""
for arg in "$@"; do
  case "$arg" in
    --review|--read-only|--full)
      engine_args+=("$arg")
      ;;
    --release)
      release=1
      engine_args+=("$arg")
      ;;
    --receipt-json=*)
      if [[ -z "${arg#*=}" ]]; then
        echo "run-quality: --receipt-json= requires a non-empty path" >&2
        exit 2
      fi
      engine_args+=("$arg")
      ;;
    --non-claim=release-changed-line-coverage)
      non_claim='release-changed-line-coverage'
      engine_args+=("$arg")
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
      echo "  CHARNESS_QUALITY_VERBOSE=1  print every gate's log instead of only failures (engine environment)"
      exit 0
      ;;
    *)
      echo "run-quality: unknown argument $arg" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$non_claim" && "$release" != "1" ]]; then
  echo "run-quality: --non-claim=release-changed-line-coverage requires --release" >&2
  exit 2
fi
if [[ "$release" == "1" && -n "${CHARNESS_QUALITY_LABELS:-}" ]]; then
  echo "run-quality: --release is one indivisible lane; CHARNESS_QUALITY_LABELS cannot narrow it" >&2
  exit 2
fi

exec python3 "$CHARNESS_GATE_DIR/run_quality_engine.py" \
  --repo-root "$REPO_ROOT" \
  --gates "$REPO_ROOT/.agents/quality-gates.yaml" \
  "${engine_args[@]}"
