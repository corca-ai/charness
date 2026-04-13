#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENDOR_DIR="$SKILL_DIR/vendor"

THREAD_URL="${1:-}"
OUTPUT_FILE="${2:-}"
TITLE="${3:-Slack Thread}"
CAPABILITY_LOGICAL_ID="${CHARNESS_SLACK_CAPABILITY:-slack.default}"
TARGET_REPO_ROOT="${CHARNESS_CAPABILITY_REPO_ROOT:-$PWD}"

if [[ -z "$THREAD_URL" || -z "$OUTPUT_FILE" ]]; then
  echo "Usage: $0 <slack_thread_url> <output_file> [title]" >&2
  exit 1
fi

for tool in node jq perl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing runtime dependency: $tool" >&2
    exit 1
  fi
done

if [[ -z "${SLACK_BOT_TOKEN:-}" ]] && command -v charness >/dev/null 2>&1; then
  ENV_EXPORTS="$(charness capability env "$CAPABILITY_LOGICAL_ID" --target-repo-root "$TARGET_REPO_ROOT")" || exit 1
  eval "$ENV_EXPORTS"
fi

if [[ ! "$THREAD_URL" =~ ^https://([^.]+)\.slack\.com/archives/([^/]+)/p([0-9]+)$ ]]; then
  echo "Unsupported Slack thread URL: $THREAD_URL" >&2
  exit 1
fi

WORKSPACE="${BASH_REMATCH[1]}"
CHANNEL_ID="${BASH_REMATCH[2]}"
THREAD_RAW="${BASH_REMATCH[3]}"

if (( ${#THREAD_RAW} <= 10 )); then
  echo "Unsupported Slack thread timestamp in URL: $THREAD_URL" >&2
  exit 1
fi

THREAD_TS="${THREAD_RAW:0:10}.${THREAD_RAW:10}"
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
OUTPUT_BASENAME="$(basename "$OUTPUT_FILE")"
OUTPUT_STEM="${OUTPUT_BASENAME%.*}"
ATTACHMENTS_DIR="$OUTPUT_DIR/${OUTPUT_STEM}.attachments"

mkdir -p "$OUTPUT_DIR" "$ATTACHMENTS_DIR"

node "$VENDOR_DIR/slack-api.mjs" "$CHANNEL_ID" "$THREAD_TS" --attachments-dir "$ATTACHMENTS_DIR" | \
  "$VENDOR_DIR/slack-to-md.sh" "$CHANNEL_ID" "$THREAD_TS" "$WORKSPACE" "$OUTPUT_FILE" "$TITLE"
