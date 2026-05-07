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

PARSED_URL="$(
  node -e '
const raw = process.argv[1];
let url;
try { url = new URL(raw); } catch { process.exit(2); }
const host = url.hostname.match(/^([^.]+)\.slack\.com$/);
const path = url.pathname.match(/^\/archives\/([^/]+)\/p([0-9]+)$/);
if (!host || !path || path[2].length <= 10) process.exit(2);
const messageTs = path[2].slice(0, 10) + "." + path[2].slice(10);
const threadTs = url.searchParams.get("thread_ts") || messageTs;
if (!/^[0-9]{10}\.[0-9]+$/.test(threadTs)) process.exit(2);
process.stdout.write([host[1], path[1], messageTs, threadTs].join("\t"));
' "$THREAD_URL"
)" || {
  echo "Unsupported Slack thread URL: $THREAD_URL" >&2
  exit 1
}

IFS=$'\t' read -r WORKSPACE CHANNEL_ID REQUESTED_MESSAGE_TS THREAD_TS <<< "$PARSED_URL"
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
OUTPUT_BASENAME="$(basename "$OUTPUT_FILE")"
OUTPUT_STEM="${OUTPUT_BASENAME%.*}"
ATTACHMENTS_DIR="$OUTPUT_DIR/${OUTPUT_STEM}.attachments"
TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

mkdir -p "$OUTPUT_DIR" "$ATTACHMENTS_DIR"

node "$VENDOR_DIR/slack-api.mjs" "$CHANNEL_ID" "$THREAD_TS" --attachments-dir "$ATTACHMENTS_DIR" > "$TMP_JSON"

if ! jq -e --arg ts "$REQUESTED_MESSAGE_TS" '.messages[]? | select(.ts == $ts)' "$TMP_JSON" >/dev/null; then
  echo "Slack export did not include requested message ts $REQUESTED_MESSAGE_TS in thread $CHANNEL_ID:$THREAD_TS" >&2
  exit 1
fi

REQUESTED_SLACK_URL="$THREAD_URL" REQUESTED_MESSAGE_TS="$REQUESTED_MESSAGE_TS" \
  "$VENDOR_DIR/slack-to-md.sh" "$CHANNEL_ID" "$THREAD_TS" "$WORKSPACE" "$OUTPUT_FILE" "$TITLE" < "$TMP_JSON"
