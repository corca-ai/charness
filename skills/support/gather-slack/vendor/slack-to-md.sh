#!/usr/bin/env bash
# Vendored Slack thread to Markdown converter.
# Reads JSON from stdin (from slack-api.mjs)
# Usage: ./slack-to-md.sh <channel_id> <thread_ts> <workspace> <output_file> [title]

set -euo pipefail

CHANNEL_ID="${1:-}"
THREAD_TS="${2:-}"
WORKSPACE="${3:-}"
OUTPUT_FILE="${4:-}"
TITLE="${5:-Slack Thread}"

if [[ -z "$CHANNEL_ID" || -z "$THREAD_TS" || -z "$WORKSPACE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <channel_id> <thread_ts> <workspace> <output_file> [title]" >&2
    echo "       JSON is read from stdin" >&2
    exit 1
fi

JSON=$(cat)

if [[ -z "$JSON" ]]; then
    echo "Error: No JSON data received from stdin" >&2
    exit 1
fi

THREAD_URL="https://${WORKSPACE}.slack.com/archives/${CHANNEL_ID}/p${THREAD_TS//./}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

UPDATED_AT=$(date "+%Y-%m-%d %H:%M")

cat > "$OUTPUT_FILE" << EOF
# $TITLE

> Slack thread archive
> Source: $THREAD_URL
> Last updated: $UPDATED_AT

EOF

USER_MAP=$(echo "$JSON" | jq -r '.users[] | "\(.id)\t\(.real_name)"')

get_username() {
    local user_id="$1"
    echo "$USER_MAP" | grep "^$user_id	" | cut -f2 || echo "$user_id"
}

convert_links() {
    local text="$1"
    text=$(echo "$text" | perl -pe 's/<(https?:\/\/[^|>]+)\|([^>]+)>/[$2]($1)/g')
    text=$(echo "$text" | perl -pe 's/<(https?:\/\/[^>]+)>/$1/g')
    text=$(echo "$text" | sed 's/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g')
    echo "$text"
}

IMAGE_EXTS="png jpg jpeg gif webp svg bmp"

is_image() {
    local ext="${1##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    for img_ext in $IMAGE_EXTS; do
        if [[ "$ext" == "$img_ext" ]]; then
            return 0
        fi
    done
    return 1
}

MSG_COUNT=$(echo "$JSON" | jq '.messages | sort_by(.ts) | length')

for (( i=0; i<MSG_COUNT; i++ )); do
    ts=$(echo "$JSON" | jq -r ".messages | sort_by(.ts) | .[$i].ts")
    user_id=$(echo "$JSON" | jq -r ".messages | sort_by(.ts) | .[$i].user")
    text=$(echo "$JSON" | jq -r ".messages | sort_by(.ts) | .[$i].text | gsub(\"\\n\"; \"\\\\n\")")

    user_name=$(get_username "$user_id")
    unix_ts="${ts%%.*}"
    date_str=$(date -r "$unix_ts" "+%Y-%m-%d %H:%M" 2>/dev/null || date -d "@$unix_ts" "+%Y-%m-%d %H:%M" 2>/dev/null)

    text=$(echo -e "$text")
    text=$(convert_links "$text")

    while [[ "$text" =~ \<@(U[A-Z0-9]+)\> ]]; do
        mention_id="${BASH_REMATCH[1]}"
        mention_name=$(get_username "$mention_id")
        text="${text//<@$mention_id>/@$mention_name}"
    done

    cat >> "$OUTPUT_FILE" << EOF
---

**${user_name}** · ${date_str}

$text

EOF

    FILE_COUNT=$(echo "$JSON" | jq ".messages | sort_by(.ts) | .[$i].files // [] | length")
    if [[ "$FILE_COUNT" -gt 0 ]]; then
        printf '\xf0\x9f\x93\x8e **Attachments**\n' >> "$OUTPUT_FILE"

        for (( j=0; j<FILE_COUNT; j++ )); do
            file_name=$(echo "$JSON" | jq -r ".messages | sort_by(.ts) | .[$i].files[$j].name // \"unknown\"")
            local_path=$(echo "$JSON" | jq -r ".messages | sort_by(.ts) | .[$i].files[$j].local_path // empty")

            if [[ -n "$local_path" ]]; then
                rel_path="attachments/$local_path"
                if is_image "$file_name"; then
                    echo "- ![${file_name}](<${rel_path}>)" >> "$OUTPUT_FILE"
                else
                    echo "- [${file_name}](<${rel_path}>)" >> "$OUTPUT_FILE"
                fi
            else
                echo "- ${file_name}" >> "$OUTPUT_FILE"
            fi
        done

        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "Saved to $OUTPUT_FILE" >&2
echo "$OUTPUT_FILE"
