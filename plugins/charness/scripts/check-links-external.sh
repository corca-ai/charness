#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v lychee >/dev/null 2>&1; then
  echo "lychee unavailable; skipping external link checks." >&2
  exit 0
fi

tmp_links="$(mktemp)"
trap 'rm -f "$tmp_links"' EXIT

python3 scripts/list_external_links.py --repo-root "$REPO_ROOT" >"$tmp_links"

if [[ ! -s "$tmp_links" ]]; then
  echo "No external http(s) links found in maintained text surfaces."
  exit 0
fi

link_count="$(wc -l <"$tmp_links" | tr -d '[:space:]')"

if [[ "${CHARNESS_LINK_CHECK_ONLINE:-0}" != "1" ]]; then
  echo "Found ${link_count} external http(s) link(s); set CHARNESS_LINK_CHECK_ONLINE=1 to validate them online."
  exit 0
fi

if [[ -z "${GITHUB_TOKEN:-}" ]] && command -v gh >/dev/null 2>&1; then
  GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
  export GITHUB_TOKEN
fi

lychee \
  --no-progress \
  --include-fragments \
  - <"$tmp_links"
