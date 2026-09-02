#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. The rule and its one implementation live in
# scripts/exported-copy-guard.sh. `scripts/gates_support/list_external_links.py` lists candidates with `git ls-files` run at
# `--repo-root`, so the mirrored copy at `plugins/charness/scripts/` would hand it the mirror as
# a repo root and collect only the mirror's own links -- then print "No external http(s) links
# found in maintained text surfaces" and exit 0 over a population it never had. Same class as
# issue #618, with the empty-population-is-green shape on top.
GATE_NAME="check-links-external"
GATE_CONSEQUENCE="This gate collects links from a git-tracked listing rooted at its own root, so a
package root that is not the git root reports a clean run over a narrower tree."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-links-external: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

if ! command -v lychee >/dev/null 2>&1; then
  cat >&2 <<'EOF'
lychee is required for link checking. Install one of:
  - cargo install lychee
  - download from https://github.com/lycheeverse/lychee/releases
EOF
  exit 1
fi

tmp_links="$(mktemp)"
# `|| true` so a failed removal cannot restate this gate's verdict: `set -e` is in
# force inside an EXIT trap, so an aborting `rm` replaces the pending status with its
# own. Measured on run-quality.sh, where it turned a correct exit 2 into a 1.
trap 'rm -f "$tmp_links" || true' EXIT

python3 scripts/gates_support/list_external_links.py --repo-root "$REPO_ROOT" >"$tmp_links"

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
