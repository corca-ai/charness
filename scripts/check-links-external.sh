#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. The full rule is written out in scripts/check-markdown.sh; keep the
# guards in step. `scripts/list_external_links.py` lists candidates with `git ls-files` run at
# `--repo-root`, so the mirrored copy at `plugins/charness/scripts/` would hand it the mirror as
# a repo root and collect only the mirror's own links -- then print "No external http(s) links
# found in maintained text surfaces" and exit 0 over a population it never had. Same class as
# issue #618, with the empty-population-is-green shape on top.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
else
  git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_toplevel" && "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
    {
      echo "check-links-external: refusing to run from an exported copy."
      echo "  script root:  $REPO_ROOT"
      echo "  git toplevel: $git_toplevel"
      echo "This gate collects links from a git-tracked listing rooted at its own root, so a"
      echo "package root that is not the git root reports a clean run over a narrower tree"
      echo "(issue #618 class)."
      echo "Run scripts/check-links-external.sh from the charness source checkout, or set"
      echo "CHARNESS_REPO_ROOT to that checkout."
    } >&2
    exit 1
  fi
fi
cd "$REPO_ROOT"

if ! command -v lychee >/dev/null 2>&1; then
  cat >&2 <<'EOF'
lychee is required for link checking. Install one of:
  - cargo install lychee
  - download from https://github.com/lycheeverse/lychee/releases
EOF
  exit 1
fi

tmp_links="$(mktemp)"
trap 'rm -f "$tmp_links"' EXIT

python3 scripts/list_external_links.py --repo-root "$REPO_ROOT" >"$tmp_links"

if [[ ! -s "$tmp_links" ]]; then
  # Name the root that was measured. An empty result stays green -- a tree may honestly have no
  # external links, and this gate has no way to tell that from a repo it should not be judging --
  # but it must not be SILENT about the scope it reached, which is how the mirrored copy used to
  # report a clean external-link run over 240 files instead of 542.
  echo "No external http(s) links found in maintained text surfaces under $REPO_ROOT."
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
